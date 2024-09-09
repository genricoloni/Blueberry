from cachetools import TTLCache
import requests

class cacheManager:
    """
    A class that manages a cache with a maximum size and time-to-live (TTL) for the cached items.
    Args:
        maxsize (int, optional): The maximum number of items that can be stored in the cache. Defaults to 100.
        ttl (int, optional): The time-to-live (in seconds) for the cached items. Defaults to 600.
    Methods:
        get(key): Retrieves the value associated with the given key from the cache. If the key is not found in the cache, it will be fetched and added to the cache.
        set(key): Fetches the content associated with the given key and adds it to the cache. Returns the fetched content.
        delete(key): Removes the item with the given key from the cache.
        clear(): Clears all items from the cache.
    """

    def __init__(self, maxsize=100, ttl=600):
        """
        Initializes the cacheManager object with a maximum size and time-to-live (TTL) for the cached items.
        Args:
            maxsize (int, optional): The maximum number of items that can be stored in the cache. Defaults to 100.
            ttl (int, optional): The time-to-live (in seconds) for the cached items. Defaults to 600.
        """
        self.cache = TTLCache(maxsize, ttl)

    def get(self, key):
        """
        Retrieves the value associated with the given key from the cache. If the key is not found in the cache, it will be fetched and added to the cache.
        Args:
            key: The key to retrieve the value for.
        Returns:
            The value associated with the given key.
        """
        try:
            return self.cache[key]
        except KeyError:
            return self.set(key)

    def set(self, key):
        """
        Fetches the content associated with the given key and adds it to the cache. Returns the fetched content.
        Args:
            key: The key to fetch the content for.
        Returns:
            The fetched content.
        """
        response = requests.get(key)
        response.raise_for_status()

        self.cache[key] = response.content

        return response.content

    def delete(self, key):
        """
        Removes the item with the given key from the cache.
        Args:
            key: The key of the item to remove.
        """
        self.cache.pop(key)

    def clear(self):
        """
        Clears all items from the cache.
        """
        self.cache.clear()