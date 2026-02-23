import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

logger = logging.getLogger("YoutubeCollector")

client = genai.Client(api_key=os.getenv("API_KEY_GEMINI"))


def get_transcription(video_id: str) -> str:
    try:
        video_url = f"https://www.youtube.com/shorts/{video_id}"
        prompt = """
Analise o vídeo fornecido e gere um relatório detalhado contendo:

1. Transcrição completa apenas das falas humanas, incluindo exclusivamente o que as pessoas estão dizendo (não incluir descrição de sons, trilha sonora ou ruídos).

2. Descrição detalhada de tudo o que acontece no vídeo, incluindo:
- Ações realizadas pelas pessoas ou objetos
- Expressões faciais, linguagem corporal e emoções aparentes
- Movimentação de câmera (zoom, cortes, transições, ângulos, enquadramentos)
- Elementos do cenário (ambiente, objetos, iluminação, cores, clima, contexto)
- Texto exibido na tela (legendas, títulos, banners, placas, etc.)
- Interações entre personagens e objetos
- Sons ambientes e trilha sonora (apenas na parte descritiva, não na transcrição)

3. Análise contextual:
- Objetivo provável do vídeo
- Público-alvo
- Tom da comunicação
- Mensagem principal transmitida

Organize a resposta nas seções:
- Transcrição das falas
- Descrição visual e sonora detalhada
- Análise e interpretação

Seja extremamente detalhado e técnico.
"""
        logger.info(f"Solicitando transcrição ao Gemini para: {video_url}")

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part(
                    file_data=types.FileData(
                        file_uri=video_url
                    )
                ),
                types.Part(text=prompt)
            ]
        )

        transcription = response.text

        if not transcription:
            logger.warning("Gemini não retornou transcrição para este vídeo.")
            return ""

        logger.info(f"Transcrição obtida via Gemini: {len(transcription)} caracteres")
        return transcription

    except Exception as e:
        logger.error(f"Erro ao obter transcrição via Gemini: {e}")
        return ""
