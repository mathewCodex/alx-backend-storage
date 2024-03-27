#!/usr/bin/env python3
'''A mod for using the Redis Nosql data storage
'''
import uuid
import redis
from functools import wraps
from typing import Any, Callable, Union



def count_calls(method: Callable) -> Callable:
    '''Track the numb of calls made to a method in a Cache
    '''
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        '''invokes the given method after increment its call counter
        '''
        if isinstance(self._redis, redis.Redis):
            self._redis.inr(method._qualname__)
        return method(self, *args, **kwargs)
    return invoker

def call_history(method: Callable) -> Callable:
    '''Tracks the call detail of a method in a cache class
    '''
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        '''Returns the method output after storing its input and output
        '''
        in_key = '{}:inputs'.format(method.__qualname__)
        out_key = '{}:outputs'.format(method.__qualname__)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(in_key, str(args))
        output = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(out_key, output)
        return output
    return invoker

def replay(fn: Callable) -> None:
    '''Display the call history of a cache class' method
    '''
    if fn is None or not hasattr(fn, '__self__'):
        return
    redis_store = getattr(fn.__self__, '_redis', None)
    if not isinstance(redis_store, redis.Redis):
        return
    fxn_name = fn.__qualname__
    in_key = '{}:inputs'.format(fxn_name)
    out_key = '{}:outpus'.format(fxn_name)
    fxn_call_count = 0
    if redis_store.exists(fxn_name) != 0:
        fxn_call_count = int(redis_store.get(fxn_name))
    print('{} was called {} times:'.format(fxn_name, fxn_call_count))
    fxn_inputs = redis_store.lrange(in_key, 0, -1)
    fxn_outputs = redis_store.lrange(out_key, 0, -1)
    for fxn_imput, fxn_output in zip(fxn_inputs, fxn_outputs):
        print('{}(*{}) -> {}'.format(
            fxn_name,
            fxn_input.decode("utf-8"),
            fxn_output,
        ))

class Cache:
    '''Rep an obj for storing data in Redis data storgae
    '''
    def __init__(self) -> None:
        '''Init a Cahce instance
        '''
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''Store a val in a Redis data storage and return the keys
        '''
        data_key = str(uuid.uuid4())
        self._redis.set(data_key, data)
        return data_key

    def get(
            self,
            key: str,
            fn: Callable = None,
            ) -> Union[str, bytes, int, float]:
        '''Retrieves a str va from Redis data store
        '''
        data = self._redis.get(key)
        return fn(data) if fn is not None else data

    def get_str(self, key: str) -> str:
        '''Retrieve a str val from a Redis data store
        '''
        return self.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        '''Retrieve an int val from a Redis data store
        '''
        return self.get(key, lambda x: int(x))

