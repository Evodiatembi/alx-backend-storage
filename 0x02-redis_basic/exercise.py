#!/usr/bin/env python3
""" Redis client module
"""
import redis
from uuid import uuid4
from typing import Union

class Cache:
    """ Cache class
    """
    def __init__(self) -> None:
        """ Initialize new cache object
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    
    def store(self, data: Union[str, bytes,  int,  float]) -> str:
        """ Stores data in redis with randomly generated key
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
