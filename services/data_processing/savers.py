import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, List

import pandas as pd

from .formatters import compute_engagement, extract_video_info, structure_comments

logger = logging.getLogger("YoutubeCollector")


def save_json(video_info: Dict, comments: List[Dict], video_folder: str) -> None:
    try:
        json_data = {
            '_metadata': {
                'source': 'youtube_data_api_v3',
                'collected_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'schema_version': '2.0',
            },
            'video': video_info,
            'comments': comments,
            'engagement': compute_engagement(video_info, comments),
        }
        json_file = os.path.join(video_folder, "dados.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        json_raw = {
            'video': video_info,
            'comments': comments,
        }
        json_raw_file = os.path.join(video_folder, "dados_raw.json")
        with open(json_raw_file, "w", encoding="utf-8") as f:
            json.dump(json_raw, f, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Erro ao salvar JSON: {e}")


def save_txt(video_info: Dict, comments: List[Dict], video_folder: str) -> None:
    try:
        txt_file = os.path.join(video_folder, "dados.txt")
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("INFORMAÇÕES DO VÍDEO\n")
            f.write("=" * 60 + "\n")
            for key, value in video_info.items():
                f.write(f"{key}: {value}\n")

            f.write("\n" + "=" * 60 + "\n")
            f.write(f"COMENTÁRIOS E RESPOSTAS ({len(comments)})\n")
            f.write("=" * 60 + "\n")

            if comments:
                for i, comment in enumerate(comments, 1):
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

                    f.write("-" * 60 + "\n")
            else:
                f.write("Nenhum comentário encontrado\n")
    except Exception as e:
        logger.error(f"Erro ao salvar TXT: {e}")


def save_video_csv(video_info: Dict, video_folder: str) -> None:
    if not video_info:
        return

    try:
        df_video = pd.DataFrame([video_info])
        csv_video_file = os.path.join(video_folder, "video.csv")
        df_video.to_csv(csv_video_file, index=False, encoding='utf-8-sig')
    except Exception as e:
        logger.error(f"Erro ao salvar CSV de vídeo: {e}")


def save_comments_csv(comments: List[Dict], video_folder: str) -> None:
    if not comments:
        return

    try:
        comments_csv = []
        for comment in comments:
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
    except Exception as e:
        logger.error(f"Erro ao salvar CSV de comentários: {e}")


def save_replies_csv(comments: List[Dict], video_folder: str) -> None:
    all_replies = []
    for comment in comments:
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

    if not all_replies:
        return

    try:
        df_replies = pd.DataFrame(all_replies)
        csv_replies_file = os.path.join(video_folder, "respostas.csv")
        df_replies.to_csv(csv_replies_file, index=False, encoding='utf-8-sig')
    except Exception as e:
        logger.error(f"Erro ao salvar CSV de respostas: {e}")


def print_summary(video_info: Dict, comments: List[Dict], video_folder: str) -> None:
    logger.info(f"✓ Dados salvos em: {video_folder}")
    saved_files = ["dados.json", "dados_raw.json", "dados.txt"]

    if video_info:
        saved_files.append("video.csv")

    if comments:
        saved_files.append(f"comentarios.csv ({len(comments)} comentários)")

    if any(c['replies'] for c in comments):
        total_respostas = sum(len(c['replies']) for c in comments)
        saved_files.append(f"respostas.csv ({total_respostas} respostas)")

    for file in saved_files:
        logger.info(f"  - {file}")


def save_video_data(video_data: Dict, video_folder: str) -> None:
    try:
        video_details = video_data.get('video_details', {})
        comments_data = video_data.get('comments_data', [])

        video_info = extract_video_info(video_data, video_details)
        comments = structure_comments(comments_data)

        if not video_info and not comments:
            logger.warning(f"⚠ Nenhum dado coletado para {video_folder}")

        save_json(video_info, comments, video_folder)
        save_txt(video_info, comments, video_folder)
        save_video_csv(video_info, video_folder)
        save_comments_csv(comments, video_folder)
        save_replies_csv(comments, video_folder)

        print_summary(video_info, comments, video_folder)

    except json.JSONDecodeError as e:
        logger.error(f"Erro ao processar JSON dos dados: {e}")
    except Exception as e:
        logger.error(f"Erro ao salvar dados do vídeo: {e}")
