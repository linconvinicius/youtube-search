import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import httplib2

# Classe para a API do YouTube
class YouTubeAPI:
    def __init__(self, api_key):
        # Desabilita a verificação do certificado SSL
        http = httplib2.Http(disable_ssl_certificate_validation=True)
        self.youtube = build('youtube', 'v3', developerKey=api_key, http=http)

    def buscar_videos(self, termo_busca, canais_ids, max_resultados=10):
        try:
            search_response = self.youtube.search().list(
                q=termo_busca,
                part='id,snippet',
                maxResults=max_resultados,
                type='video',
                channelId=','.join(canais_ids) if canais_ids else None
            ).execute()

            videos = []
            for search_result in search_response.get('items', []):
                if search_result['id']['kind'] == 'youtube#video':
                    videos.append({
                        'id': search_result['id']['videoId'],
                        'titulo': search_result['snippet']['title'],
                        'descricao': search_result['snippet']['description'],
                        'canal': search_result['snippet']['channelTitle']
                    })
            return videos
        except HttpError as e:
            print(f"Ocorreu um erro ao buscar vídeos: {e}")
            return []
