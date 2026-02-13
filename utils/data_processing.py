import pandas as pd
import json
import os


def save_video_data(video_data, video_folder):
    """
    Salva todos os dados do vídeo em formatos separados
    """
    try:
        video_details = video_data.get('video_details', {})
        comments_data = video_data.get('comments_data', {})
        transcription = video_data.get('transcription', '')
        
        video_info = {}
        comments_list = []
        
        if 'items' in video_details and len(video_details['items']) > 0:
            item = video_details['items'][0]
            snippet = item.get('snippet', {})
            statistics = item.get('statistics', {})
            content_details = item.get('contentDetails', {})
            
            video_info = {
                'video_id': video_data.get('video_id'),
                'url': video_data.get('url'),
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'published_at': snippet.get('publishedAt', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'channel_id': snippet.get('channelId', ''),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'duration': content_details.get('duration', ''),
            }
        
        if 'items' in comments_data:
            for item in comments_data['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                comments_list.append({
                    'author': comment.get('authorDisplayName', ''),
                    'text': comment.get('textOriginal', ''),
                    'like_count': int(comment.get('likeCount', 0)),
                    'published_at': comment.get('publishedAt', ''),
                })
        
        # 1. JSON com dados completos
        json_data = {
            'video': video_info,
            'comments': comments_list,
            'transcription': transcription
        }
        json_file = os.path.join(video_folder, "dados.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        # 2. TXT com informações formatadas
        txt_file = os.path.join(video_folder, "dados.txt")
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write("="*60 + "\n")
            f.write("INFORMAÇÕES DO VÍDEO\n")
            f.write("="*60 + "\n")
            for key, value in video_info.items():
                f.write(f"{key}: {value}\n")
            
            f.write("\n" + "="*60 + "\n")
            f.write("COMENTÁRIOS\n")
            f.write("="*60 + "\n")
            for i, comment in enumerate(comments_list, 1):
                f.write(f"\nComentário {i}:\n")
                f.write(f"Autor: {comment['author']}\n")
                f.write(f"Texto: {comment['text']}\n")
                f.write(f"Likes: {comment['like_count']}\n")
                f.write(f"Data: {comment['published_at']}\n")
                f.write("-"*40 + "\n")
        
        # 3. CSV do vídeo
        df_video = pd.DataFrame([video_info])
        csv_video_file = os.path.join(video_folder, "video.csv")
        df_video.to_csv(csv_video_file, index=False, encoding='utf-8-sig')
        
        # 4. CSV de comentários
        if comments_list:
            df_comments = pd.DataFrame(comments_list)
            csv_comments_file = os.path.join(video_folder, "comentarios.csv")
            df_comments.to_csv(csv_comments_file, index=False, encoding='utf-8-sig')
        
        # 5. Transcrição separada
        if transcription:
            trans_file = os.path.join(video_folder, "transcricao.txt")
            with open(trans_file, "w", encoding="utf-8") as f:
                f.write(transcription)
        
        print(f"Dados salvos em: {video_folder}")
        
    except Exception as e:
        print(f"Erro ao salvar dados do vídeo: {e}")