from app import redis_cluster
from common.cache.users import UserCache


class LikeCommentCache:
    def __init__(self, userid):
        self.userid = userid  # 用户id
        self.key = 'user:{}:like'.format(self.userid)  # redis的键

    def get(self, page, per_page):
        """获取缓存列表

        :return 主键列表 [1, 5, 11] /空列表
        """

        # 先从缓存中读取数据
        is_key_exist = redis_cluster.exists(self.key)

        # 根据页码和每页条数 构建出 开始索引 和 结束索引
        start_index = (page - 1) * per_page  # 开始索引 = (页码 - 1) * 每页条数
        end_index = start_index + per_page - 1  # 结束索引 = 开始索引 + 每页条数 - 1

        if is_key_exist:  # 如果缓存中有数据

            # zrevrange 逆序取出元素, 且返回值一定为列表  ['3', '4', '5']
            print('从缓存中读取集合数据')
            return redis_cluster.zrevrange(self.key, start_index, end_index)

        else:  # 如果缓存中没有

            # 没有缓存, 其实有两种情况: 数据库没有数据 / 数据库有, 但缓存已过期
            user = UserCache(self.userid).get()

            if user and user['follow_count']:  # 如果该用户有关注数量(数据库有, 但缓存已过期)

                followings = Relation.query.options(load_only(Relation.author_id, Relation.update_time)). \
                    filter(Relation.user_id == self.userid, Relation.relation == Relation.RELATION.FOLLOW). \
                    order_by(Relation.update_time.desc()).all()  # 直接查询出所有数据并缓存, 只缓存分页数据可能导致查询错误


                # 如果有, 则应该回填数据, 并返回数据
                following_list = []
                for item in followings:

                    # 追加/更新缓存数据到关注列表中
                    redis_cluster.zadd(self.key, item.author_id, item.update_time.timestamp())
                    following_list.append(item.author_id)

                # 设置过期时间
                redis_cluster.expire(self.key, UserFollowCacheTTL.get_val())

                print('查询集合数据并回填')
                if len(following_list) >= start_index+1:  # 如果开始索引存在
                    try:
                        return following_list[start_index:end_index+1]  # 取出分页数据

                    except Exception as e:  # 如果结束索引不存在, 则将剩余的条数都取出
                        return following_list[start_index:]
                else:
                    return []

            else:  # 判断该用户没有关注数量, 直接返回空列表(通过判断关注数量, 避免了缓存穿透)
                return []




