from api import YouTubeAPI
from cache import CacheStrategy

# Classe para gerenciar a busca de vídeos com cache
class VideoSearchManager:
    def __init__(self, youtube_api: YouTubeAPI, cache_strategy: CacheStrategy):
        self.youtube_api = youtube_api
        self.cache_strategy = cache_strategy

    def buscar_videos_com_cache(self, termo_busca, canais_ids, max_resultados=10, cache_time=3600):
        cache_key = f"{termo_busca}_{'_'.join(canais_ids)}_{max_resultados}"
        
        # Tenta obter os dados do cache
        cached_data = self.cache_strategy.get(cache_key)
        if cached_data:
            return cached_data
        
        # Se não estiver no cache, busca na API
        videos = self.youtube_api.buscar_videos(termo_busca, canais_ids, max_resultados)
        
        # Armazena no cache
        self.cache_strategy.set(cache_key, videos, cache_time)
        
        return videos
