# -*- coding: utf-8 -*-
# @Author	: brotherbaby
# @Date		: 2025/8/22 15:36
# @Last Modified by:   brotherbaby
# @Last Modified time: 2025/8/22 15:36
# Thanks for your comments!

import logging

import aredis

from ..tools.singleton import singleton

logger = logging.getLogger(__name__)


@singleton
class RedisManger:
    def __init__(self):
        self.redis_con = None
        self.__redis_connect_pool = None
        # self.ensure_redis_connect_pool(redis_conf)

    def ensure_redis_connect_pool(self, redis_conf):
        params = self.__extra_conf(redis_conf)
        params['health_check_interval'] = 20
        params['max_connections'] = 2 ** 15
        self.__redis_connect_pool = None

    def connect(self, redis_conf):
        if self.__redis_connect_pool:
            params = {
                'connection_pool': self.__redis_connect_pool
            }
        else:
            params = self.__extra_conf(redis_conf)

        self.redis_con = aredis.StrictRedis(**params)

    @staticmethod
    def __extra_conf(redis_conf):
        params = {
            'host': redis_conf.get('host', '127.0.0.1'),
            'port': redis_conf.get('port', '6379'),
            'password': redis_conf.get('password', '')
        }
        cluster_mode = redis_conf.get('clusterMode', False)
        if not cluster_mode:
            params['db'] = redis_conf.get('db', 'guest')
        return params

    async def smembers(self, key):
        """
        获取集合所有元素
        :param key:
        :return:
        """
        vals = await self.redis_con.smembers(key)
        return {member.decode('utf-8') for member in vals}

    async def sadd(self, key, items):
        if isinstance(items, list):
            await self.redis_con.sadd(key, *items)
        else:
            await self.redis_con.sadd(key, items)

    async def sismeber(self, key, item):
        """
        判断item是否存在集合中
        :param key:
        :param item:
        :return:
        """
        val = await self.redis_con.sismember(key, item)
        return val

    async def srem(self, key, items):
        if not isinstance(items, list):
            del_items = [items.encode()]
        else:
            del_items = [item if isinstance(item, bytes) else item.encode() for item in items]
        await self.redis_con.srem(key, *del_items)

    async def set_set_expire(self, key, expire):
        """ 设置集合过期时间 """
        await self.redis_con.expire(key, expire)

    async def incr_key(self, *args, **kwargs):
        await self.redis_con.incr(*args, **kwargs)

    async def delete(self, key):
        await self.redis_con.delete(key)

    async def get_value(self, key):
        return await self.redis_con.get(key)

    async def set_key(self, key, value, *args, **kwargs):
        return await self.redis_con.set(key, value, *args, **kwargs)

    async def get_all_keys_list(self, key):
        """ 模糊匹配所有的key """
        all_keys = await self.redis_con.keys(f"{key}*")
        dats = []
        for key in all_keys:
            if isinstance(key, bytes):
                key = key.decode('utf-8')  # 字节转字符串
            dats.append(key)
        return dats

    async def get_match_keys(self, key):
        """ 模糊匹配获取key后所有的key和值 """
        all_keys = await self.redis_con.keys(f"{key}*")
        dats = []
        for key in all_keys:
            if isinstance(key, bytes):
                key = key.decode('utf-8')  # 字节转字符串
            # 分割键并获取最后一部分作为ID
            sub_key = key.split(":")[-1]
            v = await self.redis_con.get(key)
            dats.append({sub_key: v.decode()})

        return dats

    async def exists(self, key):
        return await self.redis_con.exists(key)
