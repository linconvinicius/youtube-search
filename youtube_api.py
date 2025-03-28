import requests
from bs4 import BeautifulSoup
import re

def buscar_videos_youtube(termo_busca):
    """
    Busca vídeos no YouTube pelo termo especificado e retorna informações relevantes.

    Args:
        termo_busca (str): O termo de busca para os vídeos.

    Returns:
        list: Uma lista de dicionários contendo informações sobre os vídeos encontrados.
              Cada dicionário contém 'titulo', 'url', 'canal' e 'data_publicacao'.
    """
    url = f"https://www.youtube.com/results?search_query={termo_busca}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Erro ao acessar o YouTube: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    videos = []

    # Encontra todos os vídeos na página
    for video in soup.find_all('div', {'class': 'yt-uix-tile-content'}):
        titulo = video.find('a', {'class': 'yt-uix-tile-link'}).text
        url_relativa = video.find('a', {'class': 'yt-uix-tile-link'})['href']
        url_completa = 'https://www.youtube.com' + url_relativa
        canal = video.find('div', {'class': 'yt-uix-tile-content'}).find('a').text
        
        # Extrai a data de publicação (pode variar dependendo do layout)
        data_publicacao = video.find('ul', {'class': 'yt-uix-tile-meta-details'}).find_all('li')[1].text if video.find('ul', {'class': 'yt-uix-tile-meta-details'}) else 'Data não encontrada'

        videos.append({
            'titulo': titulo,
            'url': url_completa,
            'canal': canal,
            'data_publicacao': data_publicacao
        })

    return videos

# Exemplo de uso
resultados = buscar_videos_youtube("BMW")
for video in resultados:
    print(f"Título: {video['titulo']}")
    print(f"URL: {video['url']}")
    print(f"Canal: {video['canal']}")
    print(f"Data de Publicação: {video['data_publicacao']}")
    print("-" * 30)
