import time
from abc import ABC, abstractmethod

# Interface para a estratégia de cache
class CacheStrategy(ABC):
    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def set(self, key, data, cache_time):
        pass

# Implementação de cache em memória
class InMemoryCache(CacheStrategy):
    def __init__(self):
        self.cache = {}

    def get(self, key):
        if key in self.cache and self.cache[key]['expiry'] > time.time():
            print("Retornando resultados do cache em memória.")
            return self.cache[key]['data']
        return None

    def set(self, key, data, cache_time):
        self.cache[key] = {
            'data': data,
            'expiry': time.time() + cache_time
        }
