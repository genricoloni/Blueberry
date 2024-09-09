from cachetools import TTLCache
import requests

class cacheManager:
    def __init__(self, maxsize=100, ttl=600):
        self.cache = TTLCache(maxsize, ttl)

    def get(self, key):
        try:
            return self.cache[key]
        except KeyError:
            return self.set(key)

            

    def set(self, key):
        response = requests.get(key)
        response.raise_for_status()

        self.cache[key] = response.content

        return response.content

    def delete(self, key):
        self.cache.pop(key)

    def clear(self):
        self.cache.clear()