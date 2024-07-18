#!/usr/bin/env python3
""" Redis client module
"""
import redis
from uuid import uuid4
from typing import Union, Callable, Optional
from functools import wraps

def count_calls(method: Callable) -> Callable:
    """
     A decorator that counts the number of calls to the decorated function
     Args:
        method (Callable): The method to be decorated.
     Returns:
        Callable: The decorated method with counting functionality.
    """
    # wraps preserves the original method metadata
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """increment the call count using method's qualified name"""
        # Get qualified name of the method
        qualname = method.__qualname__

        # Increment the call count in redis
        self._redis.incr(qualname)

        # Execute the original method and return its value
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """
    A decorator to store history of inputs and outputs for a function.
    Args:
         method (Callable): The method to be decorated.
    Returns:
         Callable: The decorated method with history functionality
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        qualname = method.__qualname__
        inputs_key = "{}:inputs".format(qualname)
        outputs_key = "{}:outputs".format(qualname)

        # store the input arguments in redis
        self._redis.rpush(inputs_key, str(args))
        # call the actual method and get the result
        res = method(self, *args, **kwargs)
        # store the output result in redis
        self._redis.rpush(outputs_key, str(res))

        return res

    return wrapper


def replay(method: Callable) -> None:
    """
    Display the history of calls of a particular function
    Args:
        method (Callable): Method whose history is to be displayed
    """
    self = method.__self__
    qualname = method.__qualname__
    # Generate the keys for input and output history
    inputs_key = "{}:inputs".format(qualname)
    outputs_key = "{}:outputs".format(qualname)

    # Retrieve the input and output history from redis
    inputs = self._redis.lrange(inputs_key, 0, -1)
    outputs = self._redis.lrange(outputs_key, 0, -1)

    # Print the history
    print("{} was called {} times:".format(qualname, len(inputs)))
    for input_, output in zip(inputs, outputs):
        print("{}(*{}) -> {}".format(
                                     qualname,
                                     input_.decode('utf-8'),
                                     output.decode('utf-8')))

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
