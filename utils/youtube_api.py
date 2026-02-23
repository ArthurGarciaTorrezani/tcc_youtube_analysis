from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google import genai
from google.genai import types
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key= os.getenv("API_KEY_GEMINI"))


class YoutubeApi:
    YOUTUBE_API_SERVICE_NAME = os.getenv("API_SERVICE_NAME")
    YOUTUBE_API_VERSION = os.getenv("API_VERSION")
    DEVELOPER_KEY = os.getenv("API_KEY_YOUTUBE")
    static_YoutubeApi = None

    def __init__(self):
        try:
            self.youtube = build(
                self.YOUTUBE_API_SERVICE_NAME,
                self.YOUTUBE_API_VERSION,
                developerKey=self.DEVELOPER_KEY,
            )
        except Exception as e:
            print(f"Erro ao inicializar YouTube API: {e}")
            raise

    @staticmethod
    def get_instance() -> "YoutubeApi":
        if YoutubeApi.static_YoutubeApi is None:
            YoutubeApi.static_YoutubeApi = YoutubeApi()
        return YoutubeApi.static_YoutubeApi

    def make_api_request(self, method_func, **kwargs):
        max_retries = 3
        retry_count = 0
        wait_time = 30

        while retry_count < max_retries:
            try:
                request = method_func(self.youtube, **kwargs)
                return request.execute()
            except HttpError as e:
                if e.resp.status == 403:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(
                            f"Rate limit atingido. Aguardando {wait_time}s antes de tentar novamente ({retry_count}/{max_retries})..."
                        )
                        time.sleep(wait_time)
                        wait_time *= 2
                    else:
                        print(f"Erro HTTP 403 após {max_retries} tentativas: {e}")
                        raise
                else:
                    print(f"Erro HTTP na requisição API: {e}")
                    raise
            except Exception as e:
                print(f"Erro inesperado na requisição API: {e}")
                raise

        raise Exception("Falha ao executar requisição após múltiplas tentativas")


def get_data_videos(video_id):
    try:
        api_youtube = YoutubeApi.get_instance()
        method_func = lambda client, **kwargs: client.videos().list(**kwargs)
        part = "contentDetails,id,snippet,statistics,status"
        video_response = api_youtube.make_api_request(method_func, id=video_id, part=part)
        return video_response
    except HttpError as error:
        try:
            json_response = error.content if hasattr(error, "content") else None
            dados_json = json.loads(json_response)
            error_msg = f"Erro API {dados_json['error']['code']}"
            print(error_msg)
            return {"error": error_msg}
        except Exception:
            return {"error": str(error)}
    except Exception as e:
        print(f"Erro ao buscar vídeo: {e}")
        return {"error": str(e)}


def get_data_comments(video_id):
    try:
        api_youtube = YoutubeApi.get_instance()
        comentarios_estruturados = []
        next_page_token = None
        page_count = 0

        while True:
            page_count += 1
            print(f" Buscando comentários - página {page_count}...")
            method_func = lambda client, **kwargs: client.commentThreads().list(**kwargs)
            part = "snippet,replies"
            comments_response = api_youtube.make_api_request(
                method_func,
                videoId=video_id,
                part=part,
                pageToken=next_page_token,
                maxResults=100,
            )

            if "items" in comments_response:
                for thread in comments_response["items"]:
                    comentario = {
                        "comment": thread.get("snippet", {}).get("topLevelComment", {}),
                        "replies": thread.get("replies", {}).get("comments", []),
                    }
                    comentarios_estruturados.append(comentario)

            next_page_token = comments_response.get("nextPageToken")
            if not next_page_token:
                break

        print(f" Total de comentários coletados: {len(comentarios_estruturados)}")
        return comentarios_estruturados
    except HttpError as error:
        try:
            json_response = error.content if hasattr(error, "content") else None
            dados_json = json.loads(json_response)
            error_msg = f"Erro API {dados_json['error']['code']}"
            print(error_msg)
            return {"error": error_msg}
        except Exception:
            return {"error": str(error)}
    except Exception as e:
        print(f"Erro ao buscar comentários: {e}")
        return {"error": str(e)}


def get_transcription(video_id):

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
        print(f"Solicitando transcrição ao Gemini para: {video_url}")
        
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

        print(response.text) 
        transcription = response.text

        if not transcription:
            print("Gemini não retornou transcrição para este vídeo.")
            return ""

        print(f"Transcrição obtida via Gemini: {len(transcription)} caracteres")
        return transcription

    except Exception as e:
        print(f"Erro ao obter transcrição via Gemini: {e}")
        return ""