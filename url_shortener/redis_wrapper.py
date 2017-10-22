# -*- coding: utf-8 -*-

from datetime import timedelta

import redis


class RedisWrapper(object):
    def __init__(self, host, port):
        self.redis_client = redis.StrictRedis(host=host, port=port, db=0)

    def get_url(self, short_id):
        return self.redis_client.get(f'sid:{short_id}')

    def get_short_id(self, url):
        return self.redis_client.get(f'url:{url}')

    def update_expiration(self, short_id, ttl=timedelta(days=365)):
        url = self.get_url(short_id)
        self.redis_client.expire(f'sid:{short_id}', ttl)
        self.redis_client.expire(f'url:{url}', ttl)

    def set_pair(self, short_id, url, ttl=timedelta(days=365)):
        self.redis_client.set(f'sid:{short_id}', url)
        self.redis_client.set(f'url:{url}', short_id)
        if ttl:
            self.redis_client.expire(f'sid:{short_id}', ttl)
            self.redis_client.expire(f'url:{url}', ttl)
