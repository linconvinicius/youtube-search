import os
import csv
import asyncio
import datetime
from typing import List, Dict, Any
import aiohttp
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()
API_KEY = os.getenv('YOUTUBE_API_KEY')

# Lista de canais pré-cadastrados (IDs dos canais)
CHANNELS = [
    "quatrorodas",  # Quatro Rodas
    "Autoesporte",  # Autoesporte
    "motor1brasil",  # Motor1
    "automaisoficial",  # AutoMais
    "webmotors",  # Webmotors
    "Acelerados",  # Acelerados
    "decaronacomleandro",  # De carona com Leandro
    "Macchina",  # Macchina
    "duasrodasbr",  # Duas Rodas
    "motociclismoonline",  # Motociclismo
    "FullpowerTV",  # FullpowerTV
    "UltimaMarcha",  # Última Marcha
    "FlatOutBrasil",  # FlatOut!
    "CanalMotoPlay",  # MotoPLAY
    "Vansfaria",  # Vans Faria
    "OntheRoadBr",  # Rafaela Borges
    "pilotoleandromello",  # Leandro Mello
    "ARodaTV",  # A Roda
    "CarroChefe",  # Carro Chefe
    "CassioCortes",  # Cassio Cortes
    "durvalcareca",  # Durval Careca
    "MinutoMotor",  # Minuto Motor
    "EstadaoMobilidade",  # Mobilidade Estadão
    "AutoPapo",  # AutoPapo
    "garagemdobellotetv",  # Garagem do Bellote
    "KS1951",  # Karina Simões
    "FalandoDeCarro",  # Falando de Carro
    "jorgemoraes",  # Jorge Moraes
    "oloopinfinito",  # Junior Nannetti
    "RevistaMotoAdventureOficial"   # MotoAdventure
]

# Palavra-chave de busca
KEYWORD = "BMW"

class YouTubeClient:
    """Cliente para interagir com a API do YouTube."""
    
    def __init__(self, api_key: str):
        """
        Inicializa o cliente YouTube.
        
        Args:
            api_key: Chave da API do YouTube
        """
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.session = None
    
    async def __aenter__(self):
        """Inicializa a sessão HTTP assíncrona."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fecha a sessão HTTP assíncrona."""
        if self.session:
            await self.session.close()
    
    async def get_channel_videos(self, channel_id: str) -> List[Dict[str, Any]]:
        """
        Obtém vídeos de um canal específico e filtra os que contêm a palavra-chave e estão no período de 15 dias.
        
        Args:
            channel_id: ID do canal do YouTube
            
        Returns:
            Lista de vídeos que contêm a palavra-chave
        """
        try:
            channel_response = self.youtube.channels().list(
                part="contentDetails",
                forUsername=channel_id  # alterando de id para forUsername
            ).execute()
            
            if not channel_response['items']:
                logger.warning(f"Canal não encontrado: {channel_id}")
                return []
            
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            videos = []
            next_page_token = None
            max_results = 50
            max_pages = 2  # Limite de páginas a buscar
            
            for _ in range(max_pages):
                playlist_response = self.youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    maxResults=max_results,
                    playlistId=uploads_playlist_id,
                    pageToken=next_page_token
                ).execute()
                
                for item in playlist_response['items']:
                    title = item['snippet']['title']
                    description = item['snippet'].get('description', '')
                    published_at = item['snippet']['publishedAt']
                    
                    # Verifica se o vídeo contém a palavra-chave e está dentro do período de 15 dias
                    if (KEYWORD.lower() in title.lower() or KEYWORD.lower() in description.lower()) and self.is_within_period(published_at):
                        
                        video_id = item['contentDetails']['videoId']
                        video_response = self.youtube.videos().list(
                            part="statistics,snippet",
                            id=video_id
                        ).execute()

                        if video_response['items']:
                            video_info = build_video_info(video_response, channel_id, title, description)
                            videos.append(video_info)

                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token:
                    break
                
                await asyncio.sleep(0.5)  # Pausa para evitar limite de taxa
            
            return videos
            
        except HttpError as e:
            logger.error(f"Erro na API do YouTube para canal {channel_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Erro inesperado para canal {channel_id}: {e}")
            return []

    def is_within_period(self, published_at: str) -> bool:
        """
        Verifica se o vídeo foi publicado nos últimos 15 dias.
        
        Args:
            published_at: Data de publicação do vídeo
                
        Returns:
            True se o vídeo foi publicado nos últimos 15 dias, caso contrário False.
        """
        # Converte a data de publicação que tem timezone para um objeto datetime c/ timezone
        published_date = datetime.datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        # Obtém a data atual com o timezone UTC
        now = datetime.datetime.now(datetime.timezone.utc)
        
        # Verifica se a data de publicação é maior ou igual a 15 dias atrás
        return published_date >= now - datetime.timedelta(days=15)

def build_video_info(video_response, channel_id, title, description):
    """Constrói um dicionário com informações do vídeo a partir da resposta da API."""
    video_stats = video_response['items'][0]['statistics']
    video_snippet = video_response['items'][0]['snippet']
    
    published_at_formatted = datetime.datetime.fromisoformat(
        video_snippet['publishedAt'].replace('Z', '+00:00')
    ).strftime('%Y-%m-%d %H:%M:%S')
    
    return {
        'video_id': video_response['items'][0]['id'],
        'title': title,
        'channel_id': channel_id,
        'channel_title': video_snippet['channelTitle'],
        'published_at': published_at_formatted,
        'view_count': int(video_stats.get('viewCount', 0)),
        'like_count': int(video_stats.get('likeCount', 0)),
        'comment_count': int(video_stats.get('commentCount', 0)),
        'description': description,
        'url': f"https://www.youtube.com/watch?v={video_response['items'][0]['id']}"
    }

async def search_all_channels(api_key: str, channels: List[str]) -> List[Dict[str, Any]]:
    """
    Busca vídeos em todos os canais usando concorrência.
    
    Args:
        api_key: Chave da API do YouTube
        channels: Lista de IDs de canais
        
    Returns:
        Lista combinada de vídeos de todos os canais
    """
    all_videos = []
    
    async with YouTubeClient(api_key) as client:
        tasks = [client.get_channel_videos(channel_id) for channel_id in channels]
        results = await asyncio.gather(*tasks)
        
        for videos in results:
            all_videos.extend(videos)
    
    all_videos.sort(key=lambda x: x['published_at'], reverse=True)
    
    return all_videos

def save_results_to_csv(videos: List[Dict[str, Any]], filename: str = "bmw_videos.csv"):
    """
    Salva os resultados em um arquivo CSV no diretório do script.

    Args:
        videos: Lista de vídeos
        filename: Nome do arquivo de saída
    """
    if not videos:
        logger.warning("Nenhum vídeo encontrado para salvar no CSV.")
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)

    fieldnames = [
        'video_id', 'title', 'channel_title', 'published_at', 
        'view_count', 'like_count', 'comment_count', 'url'
    ]

    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for video in videos:
                row = {field: video.get(field, '') for field in fieldnames}
                writer.writerow(row)

        logger.info(f"Resultados salvos em {file_path}")
    except Exception as e:
        logger.error(f"Erro ao salvar o arquivo CSV: {e}")

def print_results_summary(videos: List[Dict[str, Any]]):
    """
    Imprime um resumo dos resultados.
    
    Args:
        videos: Lista de vídeos
    """
    if not videos:
        print("Nenhum vídeo encontrado com a palavra-chave 'BMW'.")
        return
    
    print(f"\n{'=' * 80}")
    print(f"Encontrados {len(videos)} vídeos com a palavra-chave 'BMW' nos últimos 15 dias.")
    print(f"{'=' * 80}\n")
    
    for i, video in enumerate(videos[:10]):
        print(f"{i + 1}. {video['title']}")
        print(f"   Canal: {video['channel_title']}")
        print(f"   Publicado em: {video['published_at']}")
        print(f"   Visualizações: {video['view_count']:,}")
        print(f"   URL: {video['url']}")
        print(f"   {'-' * 70}")
    
    if len(videos) > 10:
        print(f"\n... e mais {len(videos) - 10} vídeos. Veja o arquivo CSV para a lista completa.")

async def main():
    """Função principal."""
    if not API_KEY:
        logger.error("A chave da API do YouTube não foi configurada.")
        print("Por favor, defina a variável de ambiente YOUTUBE_API_KEY ou crie um arquivo .env")
        return
    
    print(f"Buscando vídeos sobre 'BMW' em {len(CHANNELS)} canais nos últimos 15 dias...")
    
    start_time = datetime.datetime.now()
    
    videos = await search_all_channels(API_KEY, CHANNELS)
    
    execution_time = (datetime.datetime.now() - start_time).total_seconds()
    
    save_results_to_csv(videos)
    print_results_summary(videos)
    
    print(f"\nBusca concluída em {execution_time:.2f} segundos.")
    print(f"Os resultados foram salvos no arquivo 'bmw_videos.csv'.")

if __name__ == "__main__":
    asyncio.run(main())
