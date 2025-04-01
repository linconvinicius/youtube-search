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
    "https://www.youtube.com/@quatrorodas/featured",  # Quatro Rodas
    "https://www.youtube.com/@Autoesporte/featured",  # Autoesporte
    "https://www.youtube.com/@motor1brasil/featured",  # Motor1
    "https://www.youtube.com/@automaisoficial/featured",  # AutoMais
    "https://www.youtube.com/@webmotors/featured",  # Webmotors
    "https://www.youtube.com/@Acelerados/featured",  # Acelerados
    "https://www.youtube.com/@decaronacomleandro/featured",  # De carona com Leandro
    "https://www.youtube.com/@Macchina/featured",  # Macchina
    "https://www.youtube.com/@duasrodasbr/featured",  # Duas Rodas
    "https://www.youtube.com/@motociclismoonline/featured",  # Motociclismo
    "https://www.youtube.com/@FullpowerTV/featured",  # FullpowerTV
    "https://www.youtube.com/@UltimaMarcha/featured",  # Última Marcha
    "https://www.youtube.com/@FlatOutBrasil/featured",  # FlatOut!
    "https://www.youtube.com/@CanalMotoPlay/featured",  # MotoPLAY
    "https://www.youtube.com/@Vansfaria/featured",  # Vans Faria
    "https://www.youtube.com/@OntheRoadBr/featured",  # Rafaela Borges
    "https://www.youtube.com/@pilotoleandromello/featured",  # Leandro Mello
    "https://www.youtube.com/@ARodaTV/featured",  # A Roda
    "https://www.youtube.com/@CarroChefe/featured",  # Carro Chefe
    "https://www.youtube.com/@CassioCortes/featured",  # Cassio Cortes
    "https://www.youtube.com/@durvalcareca/featured",  # Durval Careca
    "https://www.youtube.com/@MinutoMotor/featured",  # Minuto Motor
    "https://www.youtube.com/@EstadaoMobilidade/featured",  # Mobilidade Estadão
    "https://www.youtube.com/@AutoPapo/featured",  # AutoPapo
    "https://www.youtube.com/@garagemdobellotetv/featured",  # Garagem do Bellote
    "https://www.youtube.com/@KS1951/featured",  # Karina Simões
    "https://www.youtube.com/FalandoDeCarro/featured",  # Falando de Carro
    "https://www.youtube.com/jorgemoraes/featured",  # Jorge Moraes
    "https://www.youtube.com/@oloopinfinito/featured",  # Junior Nannetti
    "https://www.youtube.com/@RevistaMotoAdventureOficial/featured"   # MotoAdventure
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
        Obtém vídeos de um canal específico e filtra os que contêm a palavra-chave.
        
        Args:
            channel_id: ID do canal do YouTube
            
        Returns:
            Lista de vídeos que contêm a palavra-chave
        """
        try:
            # Obtém os uploads do canal
            channel_response = self.youtube.channels().list(
                part="contentDetails",
                id=channel_id
            ).execute()
            
            if not channel_response['items']:
                logger.warning(f"Canal não encontrado: {channel_id}")
                return []
            
            # Obtém a ID da playlist de uploads
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Obtém os vídeos da playlist de uploads
            videos = []
            next_page_token = None
            
            # Limite para não exceder cota da API
            max_results = 50
            max_pages = 2  # Ajuste conforme necessário
            
            for _ in range(max_pages):
                playlist_response = self.youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    maxResults=max_results,
                    playlistId=uploads_playlist_id,
                    pageToken=next_page_token
                ).execute()
                
                # Filtra vídeos que contêm a palavra-chave no título ou descrição
                for item in playlist_response['items']:
                    title = item['snippet']['title']
                    description = item['snippet'].get('description', '')
                    
                    if KEYWORD.lower() in title.lower() or KEYWORD.lower() in description.lower():
                        video_id = item['contentDetails']['videoId']
                        
                        # Obtém estatísticas detalhadas do vídeo
                        video_response = self.youtube.videos().list(
                            part="statistics,snippet",
                            id=video_id
                        ).execute()
                        
                        if video_response['items']:
                            video_stats = video_response['items'][0]['statistics']
                            video_snippet = video_response['items'][0]['snippet']
                            
                            # Formata a data de publicação
                            published_at = video_snippet['publishedAt']
                            published_at_formatted = datetime.datetime.fromisoformat(
                                published_at.replace('Z', '+00:00')
                            ).strftime('%Y-%m-%d %H:%M:%S')
                            
                            # Constrói o objeto do vídeo com informações relevantes
                            video_info = {
                                'video_id': video_id,
                                'title': title,
                                'channel_id': channel_id,
                                'channel_title': video_snippet['channelTitle'],
                                'published_at': published_at_formatted,
                                'view_count': int(video_stats.get('viewCount', 0)),
                                'like_count': int(video_stats.get('likeCount', 0)),
                                'comment_count': int(video_stats.get('commentCount', 0)),
                                'description': description,
                                'url': f"https://www.youtube.com/watch?v={video_id}"
                            }
                            
                            videos.append(video_info)
                
                # Verifica se há mais páginas
                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token:
                    break
                
                # Pausa para não ultrapassar limites de taxa
                await asyncio.sleep(0.5)
                
            return videos
            
        except HttpError as e:
            logger.error(f"Erro na API do YouTube para canal {channel_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Erro inesperado para canal {channel_id}: {e}")
            return []

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
        # Cria tasks para buscar vídeos de cada canal
        tasks = [client.get_channel_videos(channel_id) for channel_id in channels]
        
        # Executa todas as tasks concorrentemente
        results = await asyncio.gather(*tasks)
        
        # Combina os resultados
        for videos in results:
            all_videos.extend(videos)
    
    # Ordena por data de publicação (mais recentes primeiro)
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

    # Obtém o diretório do script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)

    # Define os campos para o CSV
    fieldnames = [
        'video_id', 'title', 'channel_title', 'published_at', 
        'view_count', 'like_count', 'comment_count', 'url'
    ]

    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Escreve o cabeçalho
            writer.writeheader()

            # Escreve os dados
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
    print(f"Encontrados {len(videos)} vídeos com a palavra-chave 'BMW'")
    print(f"{'=' * 80}\n")
    
    for i, video in enumerate(videos[:10], 1):  # Mostra apenas os 10 primeiros
        print(f"{i}. {video['title']}")
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
    
    print(f"Buscando vídeos sobre 'BMW' em {len(CHANNELS)} canais...")
    
    # Mede o tempo de execução
    start_time = datetime.datetime.now()
    
    # Busca vídeos em todos os canais
    videos = await search_all_channels(API_KEY, CHANNELS)
    
    # Calcula o tempo de execução
    execution_time = (datetime.datetime.now() - start_time).total_seconds()
    
    # Salva em CSV e imprime resultados
    save_results_to_csv(videos)
    print_results_summary(videos)
    
    print(f"\nBusca concluída em {execution_time:.2f} segundos")
    print(f"Os resultados foram salvos no arquivo 'bmw_videos.csv'")

if __name__ == "__main__":
    asyncio.run(main())