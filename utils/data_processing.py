import pandas as pd
import json
import os


def save_video_data(video_data, video_folder):
    """
    Salva TODOS os dados do vídeo em formatos separados:
    - JSON completo com vídeo, comentários e respostas
    - TXT formatado
    - CSVs estruturados
    - Transcrição
    """
    try:
        video_details = video_data.get('video_details', {})
        comments_data = video_data.get('comments_data', [])
        transcription = video_data.get('transcription', '')
        
        video_info = {}
        
        # Extrair informações do vídeo
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
        
        # Processar comentários com respostas
        comments_estruturados = []
        if isinstance(comments_data, list):
            for thread in comments_data:
                comment_obj = thread.get('comment', {})
                replies = thread.get('replies', [])
                
                comment_snippet = comment_obj.get('snippet', {})
                item_data = {
                    'comment_id': comment_obj.get('id', ''),
                    'author': comment_snippet.get('authorDisplayName', ''),
                    'text': comment_snippet.get('textOriginal', ''),
                    'like_count': int(comment_snippet.get('likeCount', 0)),
                    'published_at': comment_snippet.get('publishedAt', ''),
                    'replies': []
                }
                
                # Adicionar respostas
                for reply in replies:
                    reply_snippet = reply.get('snippet', {})
                    item_data['replies'].append({
                        'reply_id': reply.get('id', ''),
                        'author': reply_snippet.get('authorDisplayName', ''),
                        'text': reply_snippet.get('textOriginal', ''),
                        'like_count': int(reply_snippet.get('likeCount', 0)),
                        'published_at': reply_snippet.get('publishedAt', ''),
                    })
                
                comments_estruturados.append(item_data)
        
        # 1. JSON completo com TUDO
        json_data = {
            'video': video_info,
            'comments': comments_estruturados,
            'transcription': transcription
        }
        json_file = os.path.join(video_folder, "dados.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        # 2. TXT com informações formatadas e completas
        txt_file = os.path.join(video_folder, "dados.txt")
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write("="*60 + "\n")
            f.write("INFORMAÇÕES DO VÍDEO\n")
            f.write("="*60 + "\n")
            for key, value in video_info.items():
                f.write(f"{key}: {value}\n")
            
            f.write("\n" + "="*60 + "\n")
            f.write("COMENTÁRIOS E RESPOSTAS\n")
            f.write("="*60 + "\n")
            for i, comment in enumerate(comments_estruturados, 1):
                f.write(f"\nComentário {i}:\n")
                f.write(f"ID: {comment['comment_id']}\n")
                f.write(f"Autor: {comment['author']}\n")
                f.write(f"Texto: {comment['text']}\n")
                f.write(f"Likes: {comment['like_count']}\n")
                f.write(f"Data: {comment['published_at']}\n")
                
                if comment['replies']:
                    f.write(f"\n  Respostas ({len(comment['replies'])}):\n")
                    for j, reply in enumerate(comment['replies'], 1):
                        f.write(f"  {j}. {reply['author']}: {reply['text']}\n")
                        f.write(f"     Likes: {reply['like_count']} | Data: {reply['published_at']}\n")
                
                f.write("-"*60 + "\n")
        
        # 3. CSV do vídeo
        df_video = pd.DataFrame([video_info])
        csv_video_file = os.path.join(video_folder, "video.csv")
        df_video.to_csv(csv_video_file, index=False, encoding='utf-8-sig')
        
        # 4. CSV de comentários (sem respostas para manter formato tabular)
        if comments_estruturados:
            comments_csv = []
            for comment in comments_estruturados:
                comments_csv.append({
                    'comment_id': comment['comment_id'],
                    'author': comment['author'],
                    'text': comment['text'],
                    'like_count': comment['like_count'],
                    'published_at': comment['published_at'],
                    'reply_count': len(comment['replies'])
                })
            df_comments = pd.DataFrame(comments_csv)
            csv_comments_file = os.path.join(video_folder, "comentarios.csv")
            df_comments.to_csv(csv_comments_file, index=False, encoding='utf-8-sig')
        
        # 5. CSV de respostas (todas as respostas em um arquivo)
        if comments_estruturados:
            all_replies = []
            for comment in comments_estruturados:
                for reply in comment['replies']:
                    all_replies.append({
                        'comment_id': comment['comment_id'],
                        'comment_author': comment['author'],
                        'reply_id': reply['reply_id'],
                        'reply_author': reply['author'],
                        'reply_text': reply['text'],
                        'reply_like_count': reply['like_count'],
                        'reply_published_at': reply['published_at']
                    })
            
            if all_replies:
                df_replies = pd.DataFrame(all_replies)
                csv_replies_file = os.path.join(video_folder, "respostas.csv")
                df_replies.to_csv(csv_replies_file, index=False, encoding='utf-8-sig')
        
        # 6. Transcrição separada
        if transcription:
            trans_file = os.path.join(video_folder, "transcricao.txt")
            with open(trans_file, "w", encoding="utf-8") as f:
                f.write(transcription)
        
        print(f"✓ Dados salvos em: {video_folder}")
        print(f"  - dados.json (completo)")
        print(f"  - dados.txt (formatado)")
        print(f"  - video.csv")
        print(f"  - comentarios.csv ({len(comments_estruturados)} comentários)")
        if any(c['replies'] for c in comments_estruturados):
            print(f"  - respostas.csv (todas as respostas)")
        if transcription:
            print(f"  - transcricao.txt")
        
    except Exception as e:
        print(f"Erro ao salvar dados do vídeo: {e}")