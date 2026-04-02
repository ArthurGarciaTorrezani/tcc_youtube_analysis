# %%
import logging
import os
import csv
#from dotenv import load_dotenv
from google import genai
from google.genai import types
import time

BASE_DIR = "sua_rota"
VIDEO_EXTENSIONS = (".mp4", ".webm", ".mkv", ".avi", ".mov")

#load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("YoutubeCollector")

client = genai.Client(api_key="AIzaSyAht-6ksUp6oy67MjHFOb4t9adBQCw502w")

PROMPT = """
Analise o vídeo fornecido e gere um relatório detalhado contendo:


1. Descrição detalhada de tudo o que acontece no vídeo, incluindo:
- Ações realizadas pelas pessoas ou objetos
- Expressões faciais, linguagem corporal e emoções aparentes
- Movimentação de câmera (zoom, cortes, transições, ângulos, enquadramentos)
- Elementos do cenário (ambiente, objetos, iluminação, cores, clima, contexto)
- Texto exibido na tela (legendas, títulos, banners, placas, etc.)
- Interações entre personagens e objetos
- Sons ambientes e trilha sonora (apenas na parte descritiva, não na transcrição)

2. Análise contextual:
- Objetivo provável do vídeo
- Público-alvo
- Tom da comunicação
- Mensagem principal transmitida

Organize a resposta nas seções:
- Descrição visual e sonora detalhada
- Análise e interpretação

Seja extremamente detalhado e técnico.
"""


def find_video_file(video_path: str) -> str | None:
    """Retorna o caminho do primeiro arquivo de vídeo encontrado na pasta."""
    for file in os.listdir(video_path):
        if file.lower().endswith(VIDEO_EXTENSIONS):
            return os.path.join(video_path, file)
    return None


def get_description(video_file_path: str) -> str:
    try:
#        logger.info(f"Fazendo upload do vídeo: {video_file_path}")
#        uploaded_file = client.files.upload(file=video_file_path)
#        logger.info(f"Upload concluído: {uploaded_file.name}")
        
        response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=types.Content(
            parts=[
                types.Part(
                    file_data=types.FileData(file_uri=video_file_path)
                    ),
                types.Part(text='Faça uma descrição detalhada do que se passa no video, em todos os apectos, visual e auditivo')
                ]
            )
        )

        description = response.text

        if not description:
            logger.warning("Gemini não retornou descrição para este vídeo.")
            return ""

        logger.info(f"Descrição obtida: {len(description)} caracteres")
        return description

    except Exception as e:
        logger.error(f"Erro ao obter descrição via Gemini: {e}", exc_info=False)
        return ""


def describe_all_videos(base_path=BASE_DIR):
    print(f"Buscando vídeos em: {base_path}")

    for coleta_folder in os.listdir(base_path):
        coleta_path = os.path.join(base_path, coleta_folder)

        if not os.path.isdir(coleta_path):
            continue

        for video_folder in os.listdir(coleta_path):
            video_path = os.path.join(coleta_path, video_folder)

            if not os.path.isdir(video_path):
                continue

            # Pula se a descrição já foi feita
            descricao_path = os.path.join(video_path, "descricao.txt")
            if os.path.exists(descricao_path):
                print(f"[PULANDO] Descrição já existe em: {video_path}")
                continue

            video_csv = os.path.join(video_path, "video.csv")
            if not os.path.exists(video_csv):
                print(f"[AVISO] video.csv não encontrado em: {video_path}")
                continue

            with open(video_csv, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    video_id = row.get("id") or row.get("video_id") or list(row.values())[0]
                    video_id = video_id.strip()
                    url = f"https://www.youtube.com/shorts/{video_id}"
                    print(f"\nProcessando: {url}")

                    try:
                        description = get_description(url)
                        if description:
                            with open(descricao_path, "w", encoding="utf-8") as out:
                                out.write(description)
                            print(f"[OK] Descrição salva em: {descricao_path}")
                            time.sleep(15)
                        else:
                            print(f"[ERRO] Descrição vazia para: {url}")
                    except Exception as e:
                        print(f"[ERRO] Falha ao processar {url}: {e}")

if __name__ == "__main__":
    describe_all_videos()