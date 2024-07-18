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
         Args:
            data (Union[str, bytes, int, float]): The data to be stored.

        Returns:
            str: The UUID key as a string.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self,
            key: str,
            fn: Optional[Callable[[bytes], Union[str,
                                                 bytes, int, float]]] = None
            ) -> Union[str, bytes, int, float]:
        """
        Retrieve the data from the cache using the provided key.

        Args:
            key (str): The key to retrieve the data.
            fn (Optional[Callable[[bytes], Union[str, bytes, int, float]]]):
            A function to apply to the retrieved data.

        Returns:
            Union[str, bytes, int, float, None]: The retrieved data,
            possibly transformed by fn, or None if the key does not exist.
        """
        data = self._redis.get(key)
        if data is not None and fn is not None:
            return fn(data)
        return data

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve the data as a string from the cache using the provided key.

        Args:
            key (str): The key to retrieve the data.

        Returns:
            Optional[str]: The retrieved data as a string,
            or None if the key does not exist.
        """
        return self.get(key, fn=lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve the data as an integer from the cache using the provided key.

        Args:
            key (str): The key to retrieve the data.

        Returns:
            Optional[int]: The retrieved data as an integer,
            or None if the key does not exist.
        """
        return self.get(key, fn=int)
