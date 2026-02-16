from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import os
import json
from dotenv import load_dotenv

load_dotenv()


class YoutubeApi:
    YOUTUBE_API_SERVICE_NAME = os.getenv("API_SERVICE_NAME")
    YOUTUBE_API_VERSION = os.getenv("API_VERSION")
    DEVELOPER_KEY = os.getenv("API_KEY")
    static_YoutubeApi = None

    def __init__(self):
        try:
            self.youtube = build(
                self.YOUTUBE_API_SERVICE_NAME, 
                self.YOUTUBE_API_VERSION, 
                developerKey=self.DEVELOPER_KEY
            )
        except Exception as e:
            print(f"Erro ao inicializar YouTube API: {e}")
            raise

    @staticmethod
    def get_instance() -> "YoutubeApi":
        if YoutubeApi.static_YoutubeApi == None:
            YoutubeApi.static_YoutubeApi = YoutubeApi()
        return YoutubeApi.static_YoutubeApi

    def make_api_request(self, method_func, **kwargs):
        try:
            request = method_func(self.youtube, **kwargs)
            return request.execute()
        except HttpError as e:
            print(f"Erro HTTP na requisição API: {e}")
            raise
        except Exception as e:
            print(f"Erro inesperado na requisição API: {e}")
            raise


def get_data_videos(video_id):
    try:
        api_youtube = YoutubeApi.get_instance()
        method_func = lambda client, **kwargs: client.videos().list(**kwargs)
        part = "contentDetails,id,snippet,statistics"
        
        video_response = api_youtube.make_api_request(method_func, id=video_id, part=part)
        return video_response
        
    except HttpError as error:
        try:
            jsonR = error.content if hasattr(error, 'content') else None
            dados_json = json.loads(jsonR)
            error_msg = f"Erro API {dados_json['error']['code']}"
            print(error_msg)
            return {"error": error_msg}
        except:
            return {"error": str(error)}
    except Exception as e:
        print(f"Erro ao buscar vídeo: {e}")
        return {"error": str(e)}


def get_data_comments(video_id):
    try:
        api_youtube = YoutubeApi.get_instance()
        method_func = lambda client, **kwargs: client.commentThreads().list(**kwargs)
        part = "snippet,replies"
        
        comments_response = api_youtube.make_api_request(
            method_func, 
            videoId=video_id, 
            part=part, 
            maxResults=100
        )
        
    except HttpError as error:
        try:
            jsonR = error.content if hasattr(error, 'content') else None
            dados_json = json.loads(jsonR)
            error_msg = f"Erro API {dados_json['error']['code']}"
            print(error_msg)
            return {"error": error_msg}
        except:
            return {"error": str(error)}
    except Exception as e:
        print(f"Erro ao buscar comentários: {e}")
        return {"error": str(e)}
    
    

def get_data_replies(video_id, comment_id):
    api_youtube = YoutubeApi.get_instance()
    next_page_token = None  # Mover para fora do loop
    all_replies = []  # Para armazenar as respostas
    
    while True:
        method_func = lambda client, **kwargs: client.comments().list(**kwargs)
        
        try:
            comment_response = api_youtube.make_api_request(
                method_func,
                part="snippet",
                parentId=comment_id,
                pageToken=next_page_token,
                maxResults=100
            )
            
            # Coletar os comentários desta página
            if 'items' in comment_response:
                all_replies.extend(comment_response['items'])
        
            next_page_token = comment_response.get('nextPageToken')
            if not next_page_token:
                break
                
        except Exception as e:
            print(f"Erro ao buscar respostas: {e}")
            break
    
    return all_replies

def get_transcription(video_id):
    try:
        ytt_api = YouTubeTranscriptApi().fetch(video_id, languages=['pt', 'en'])
        
        if not hasattr(ytt_api, 'snippets') or not ytt_api.snippets:
            print("Nenhum snippet de transcrição encontrado")
            return ""
        
        transcription = " ".join([snippet.text for snippet in ytt_api.snippets])
        
        print(f"Transcrição obtida: {len(ytt_api.snippets)} snippets, {len(transcription)} caracteres")
        
        return transcription
        
    except (TranscriptsDisabled, NoTranscriptFound):
        print("Transcrições desabilitadas ou não encontradas")
        return ""
    except Exception as e:
        print(f"Erro ao buscar transcrição: {e}")
        return ""