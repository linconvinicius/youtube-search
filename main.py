import os
import json
import time
from api import YouTubeAPI
from cache import InMemoryCache
from manager import VideoSearchManager

def main():
    # Inicializa os componentes
    api_key = os.environ.get('YOUTUBE_API_KEY')
    youtube_api = YouTubeAPI(api_key)
    cache_strategy = InMemoryCache()
    video_search_manager = VideoSearchManager(youtube_api, cache_strategy)

    termo_busca = "BMW"
    canais_ids = [
        "UC92_eQW-P_65j6i_EtdOO5Q",  # Quatro Rodas
        "UCunmF-8mo-z3K11Va9Ev6OQ",  # Autoesporte
        "UCw5UN2xJxgjWpWxGAvK43aw",  # Motor1
        "UCYizWsZp_z-o3G_jKxYmFYA",  # AutoMais
        "UCQt93PtF_Ktq2qs-Jv6-u_g",  # Webmotors
        "UCihpiVo-4lH-6sdnJ-msw9Q",  # Acelerados
        "UCQGCI-jig_j3W-5Jv2K0-uw",  # De carona com Leandro
        "UC09wz-D8HOKW-Rg-Kz5dF4w",  # Macchina
        "UCY-uo_EQS-w05jf9er-mo6w",  # Duas Rodas
        "UC-q6GvjJGNpsmdNJouCjFAg",  # Motociclismo
        "UCW_x5c-5i-jzX-jOO-q-aww",  # FullpowerTV
        "UC03zlIIJGTg9cK5-1sW-vAA",  # Última Marcha
        "UCvBm9V89lex-BktEtNjRAJA",  # FlatOut!
        "UCUv0SQt-j-Y-fFw6oZHTbqg",  # MotoPLAY
        "UCy3xlL1ywjytXj-bE2sQ-FA",  # Vans Faria
        "UCg40YwH3GfKGVw9ZJv5-g2w",  # Rafaela Borges
        "UCG_XQJgFT3bYt_bW-9XyX-w",  # Leandro Mello
        "UC0Yg-e0oYYHRY_c6x_qG8tw",  # A Roda
        "UC0E5jCjJ-Wdtm7vj6W-XWgw",  # Carro Chefe
        "UCy3xlL1ywjytXj-bE2sQ-FA",  # Cassio Cortes
        "UCi1-jnY-XkQ-Q6j19DTws6w",  # Durval Careca
        "UC057g_6wT-cWVelKj-6-Q4Q",  # Minuto Motor
        "UCYizWsZp_z-o3G_jKxYmFYA",  # Mobilidade Estadão
        "UCYizWsZp_z-o3G_jKxYmFYA",  # AutoPapo
        "UCYizWsZp_z-o3G_jKxYmFYA",  # Garagem do Bellote
        "UCYizWsZp_z-o3G_jKxYmFYA",  # Karina Simões
        "UCYizWsZp_z-o3G_jKxYmFYA",  # Falando de Carro
        "UCYizWsZp_z-o3G_jKxYmFYA",  # Jorge Moraes
        "UCYizWsZp_z-o3G_jKxYmFYA",  # Junior Nannetti
        "UCYizWsZp_z-o3G_jKxYmFYA"   # MotoAdventure
    ]
    max_resultados = 5

    # Primeira busca: busca na API e armazena no cache
    print("Primeira busca...")
    videos = video_search_manager.buscar_videos_com_cache(termo_busca, canais_ids, max_resultados)
    print(json.dumps(videos, indent=4, ensure_ascii=False))

    # Pequena pausa para simular tempo real
    time.sleep(2)

    # Segunda busca: retorna do cache
    print("\nSegunda busca...")
    videos = video_search_manager.buscar_videos_com_cache(termo_busca, canais_ids, max_resultados)
    print(json.dumps(videos, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()
