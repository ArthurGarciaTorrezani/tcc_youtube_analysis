import pandas as pd
import json
import os


def _extract_comment_data(comment_obj, replies):
    """
    Extrai e estrutura dados de um comentário e suas respostas.
    
    Função auxiliar para evitar duplicação de lógica na extração de comentários.
    
    Args:
        comment_obj (dict): Objeto do comentário da API
        replies (list): Lista de respostas do comentário
        
    Returns:
        dict: Dados estruturados do comentário com respostas
    """
    try:
        comment_snippet = comment_obj.get('snippet', {})
        item_data = {
            'comment_id': comment_obj.get('id', ''),
            'author': comment_snippet.get('authorDisplayName', ''),
            'text': comment_snippet.get('textOriginal', ''),
            'like_count': int(comment_snippet.get('likeCount', 0)),
            'published_at': comment_snippet.get('publishedAt', ''),
            'replies': []
        }
        
        for reply in replies:
            try:
                reply_snippet = reply.get('snippet', {})
                item_data['replies'].append({
                    'reply_id': reply.get('id', ''),
                    'author': reply_snippet.get('authorDisplayName', ''),
                    'text': reply_snippet.get('textOriginal', ''),
                    'like_count': int(reply_snippet.get('likeCount', 0)),
                    'published_at': reply_snippet.get('publishedAt', ''),
                })
            except Exception as e:
                print(f"Erro ao processar resposta: {e}")
                continue
        
        return item_data
    except Exception as e:
        print(f"Erro ao extrair dados do comentário: {e}")
        return None


def save_video_data(video_data, video_folder):
    """
    Salva TODOS os dados do vídeo em múltiplos formatos com validação e tratamento de erros.
    
    Arquivos gerados:
    - dados.json: Dados completos estruturados
    - dados.txt: Formato legível
    - video.csv: Metadados do vídeo
    - comentarios.csv: Comentários (se houver)
    - respostas.csv: Respostas (se houver)
    - transcricao.txt: Transcrição (se disponível)
    
    Args:
        video_data (dict): Dados do vídeo coletados
        video_folder (str): Caminho da pasta para salvar dados
    """
    try:
        video_details = video_data.get('video_details', {})
        comments_data = video_data.get('comments_data', [])
        transcription = video_data.get('transcription', '')
        
        video_info = {}
        
        if 'items' in video_details and len(video_details['items']) > 0:
            try:
                item = video_details['items'][0]
                snippet = item.get('snippet', {})
                statistics = item.get('statistics', {})
                content_details = item.get('contentDetails', {})
                status = item.get('status',{})
                
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
                    'madeForKids': status.get('madeForKids')
                }
            except Exception as e:
                print(f"Erro ao extrair dados do vídeo: {e}")
        
        comments_estruturados = []
        if isinstance(comments_data, list) and len(comments_data) > 0:
            for thread in comments_data:
                comment_obj = thread.get('comment', {})
                replies = thread.get('replies', [])
                
                comment_item = _extract_comment_data(comment_obj, replies)
                if comment_item:
                    comments_estruturados.append(comment_item)
        
        if not video_info and not comments_estruturados and not transcription:
            print(f"⚠ Nenhum dado coletado para {video_folder}")
        
        json_data = {
            'video': video_info,
            'comments': comments_estruturados,
            'transcription': transcription
        }
        json_file = os.path.join(video_folder, "dados.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        txt_file = os.path.join(video_folder, "dados.txt")
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write("="*60 + "\n")
            f.write("INFORMAÇÕES DO VÍDEO\n")
            f.write("="*60 + "\n")
            for key, value in video_info.items():
                f.write(f"{key}: {value}\n")
            
            f.write("\n" + "="*60 + "\n")
            f.write(f"COMENTÁRIOS E RESPOSTAS ({len(comments_estruturados)})\n")
            f.write("="*60 + "\n")
            
            if comments_estruturados:
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
            else:
                f.write("Nenhum comentário encontrado\n")
        
        if video_info:
            df_video = pd.DataFrame([video_info])
            csv_video_file = os.path.join(video_folder, "video.csv")
            df_video.to_csv(csv_video_file, index=False, encoding='utf-8-sig')
        
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
            
            if comments_csv:
                df_comments = pd.DataFrame(comments_csv)
                csv_comments_file = os.path.join(video_folder, "comentarios.csv")
                df_comments.to_csv(csv_comments_file, index=False, encoding='utf-8-sig')
        
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
        
        if transcription and transcription.strip():
            trans_file = os.path.join(video_folder, "transcricao.txt")
            with open(trans_file, "w", encoding="utf-8") as f:
                f.write(transcription)
        
        print(f"✓ Dados salvos em: {video_folder}")
        saved_files = ["dados.json", "dados.txt"]
        if video_info:
            saved_files.append("video.csv")
        if comments_estruturados:
            saved_files.append(f"comentarios.csv ({len(comments_estruturados)} comentários)")
        if any(c['replies'] for c in comments_estruturados):
            total_respostas = sum(len(c['replies']) for c in comments_estruturados)
            saved_files.append(f"respostas.csv ({total_respostas} respostas)")
        if transcription and transcription.strip():
            saved_files.append("transcricao.txt")
        
        for file in saved_files:
            print(f"  - {file}")
        
    except json.JSONDecodeError as e:
        print(f"Erro ao processar JSON dos dados: {e}")
    except Exception as e:
        print(f"Erro ao salvar dados do vídeo: {e}")