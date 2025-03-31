import requests
from config import YOUTUBE_API_KEY

def buscar_videos_canais(canais_ids, termo_busca):
    videos = []
    
    for canal_id in canais_ids:
        url = f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&q={termo_busca}&channelId={canal_id}&maxResults=5&type=video&key={YOUTUBE_API_KEY}"
        response = requests.get(url)
        print(f"Consultando canal: {canal_id}")
        print(f"URL: {url}")
        print("Resposta da API:", response.json()) 
        
        if response.status_code == 200:
            data = response.json()
            for item in data.get("items", []):
                video_info = {
                    "titulo": item["snippet"]["title"],
                    "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    "canal": item["snippet"]["channelTitle"],
                    "data_publicacao": item["snippet"]["publishedAt"]
                }
                videos.append(video_info)
        else:
            print(f"Erro ao buscar vídeos do canal {canal_id}: {response.status_code}")

    return videos

# Lista de canais
canais_ids = [
    "UC92_eQW-P_65j6i_EtdOO5Q",  # Quatro Rodas
    "UCunmF-8mo-z3K11Va9Ev6OQ",  # Autoesporte
    "UCw5UN2xJxgjWpWxGAvK43aw",  # Motor1
    "UCYizWsZp_z-o3G_jKxYmFYA",  # AutoMais
    "UCQt93PtF_Ktq2qs-Jv6-u_g",  # Webmotors
    "UCihpiVo-4lH-6sdnJ-msw9Q",  # Acelerados
]

# Exemplo de uso
resultados = buscar_videos_canais(canais_ids, "BMW")
for video in resultados:
    print(f"Título: {video['titulo']}")
    print(f"URL: {video['url']}")
    print(f"Canal: {video['canal']}")
    print(f"Data de Publicação: {video['data_publicacao']}")
    print("-" * 50)
