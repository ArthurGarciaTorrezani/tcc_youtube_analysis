import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

import pandas as pd


def iso_duration_to_seconds(duration_iso: str) -> Optional[int]:
    if not duration_iso:
        return None

    pattern = re.compile(r"P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")
    match = pattern.fullmatch(duration_iso)
    if not match:
        return None

    days, hours, minutes, seconds = (int(v) if v else 0 for v in match.groups())

    return (
        days * 86400
        + hours * 3600
        + minutes * 60
        + seconds
    )


def detect_content_type(url: str, duration_seconds: Optional[int]) -> str:
    if url and "shorts" in url:
        return "short"

    if duration_seconds is not None and duration_seconds <= 60:
        return "short"

    return "video"


def flag_comment(text: str) -> List[str]:
    flags: List[str] = []
    if not text or not text.strip():
        return ["empty"]

    clean = re.sub(r"[^\w\s]", "", text, flags=re.UNICODE).strip()

    if not clean:
        flags.append("emoji_only")
        return flags

    words = clean.split()

    if len(words) == 1 and words[0].isdigit():
        flags.append("spam")
        return flags

    spam_patterns = [r"\bme\s+fix[ao]\b", r"\bprimeiro\b", r"\bsegundo\b", r"\bcedoo+\b", r"\bchegamos cedo\b"]

    if any(re.search(p, text, re.IGNORECASE) for p in spam_patterns):
        flags.append("spam")
        return flags

    if len(words) <= 2:
        flags.append("low_quality")
        return flags

    if len(words) >= 15:
        flags.append("narrative")

    return flags


def compute_engagement(video_info: Dict, comments: List[Dict]) -> Dict:
    view_count = video_info.get("view_count") or 0
    like_count = video_info.get("like_count") or 0
    comment_count = video_info.get("comment_count") or 0

    comments_with_replies = sum(1 for c in comments if c.get("replies"))
    total_replies = sum(len(c.get("replies", [])) for c in comments)

    like_view_ratio = round(like_count / view_count, 4) if view_count else None
    comment_view_ratio = round(comment_count / view_count, 6) if view_count else None

    return {
        "like_view_ratio": like_view_ratio,
        "comment_view_ratio": comment_view_ratio,
        "comments_with_replies": comments_with_replies,
        "total_replies": total_replies,
    }


def extract_comment_data(comment_obj: Dict, replies: List[Dict]) -> Optional[Dict]:
    try:
        comment_snippet = comment_obj.get("snippet", {})
        text = comment_snippet.get("textOriginal", "")
        item_data = {
            "comment_id": comment_obj.get("id", ""),
            "author": comment_snippet.get("authorDisplayName", ""),
            "text": text,
            "like_count": (int(comment_snippet["likeCount"]) if "likeCount" in comment_snippet else None),
            "published_at": comment_snippet.get("publishedAt", ""),
            "flags": flag_comment(text),
            "replies": [],
        }

        for reply in replies:
            try:
                reply_snippet = reply.get("snippet", {})
                item_data["replies"].append(
                    {
                        "reply_id": reply.get("id", ""),
                        "author": reply_snippet.get("authorDisplayName", ""),
                        "text": reply_snippet.get("textOriginal", ""),
                        "like_count": (int(reply_snippet["likeCount"]) if "likeCount" in reply_snippet else None),
                        "published_at": reply_snippet.get("publishedAt", ""),
                    }
                )
            except Exception as exc:
                print(f"Erro ao processar resposta: {exc}")
                continue

        return item_data
    except Exception as exc:
        print(f"Erro ao extrair dados do comentário: {exc}")
        return None


def extract_video_info(video_data: Dict, video_details: Dict) -> Dict:
    video_info = {}

    if 'items' not in video_details or len(video_details['items']) == 0:
        return video_info

    try:
        item = video_details['items'][0]
        snippet = item.get('snippet', {})
        statistics = item.get('statistics', {})
        content_details = item.get('contentDetails', {})
        status = item.get('status', {})
        duration_iso = content_details.get('duration', '')
        duration_seconds = iso_duration_to_seconds(duration_iso)
        view_count = statistics.get('viewCount')
        like_count = statistics.get('likeCount')
        comment_count = statistics.get('commentCount')
        url = video_data.get('url', '')

        video_info = {
            'video_id': video_data.get('video_id'),
            'url': url,
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'published_at': snippet.get('publishedAt', ''),
            'channel_title': snippet.get('channelTitle', ''),
            'channel_id': snippet.get('channelId', ''),
            'view_count': (int(view_count) if view_count is not None else None),
            'like_count': (int(like_count) if like_count is not None else None),
            'comment_count': (int(comment_count) if comment_count is not None else None),
            'duration_iso': duration_iso,
            'duration_seconds': duration_seconds,
            'content_type': detect_content_type(url, duration_seconds),
            'language': snippet.get('defaultAudioLanguage', 'unknown'),
            'madeForKids': status.get('madeForKids')
        }
    except Exception as e:
        print(f"Erro ao extrair dados do vídeo: {e}")

    return video_info


def structure_comments(comments_data: List[Dict]) -> List[Dict]:
    comments_estruturados = []

    if not isinstance(comments_data, list) or len(comments_data) == 0:
        return comments_estruturados

    for thread in comments_data:
        comment_obj = thread.get('comment', {})
        replies = thread.get('replies', [])

        comment_item = extract_comment_data(comment_obj, replies)
        if comment_item:
            comments_estruturados.append(comment_item)

    return comments_estruturados


def save_json(video_info: Dict, comments: List[Dict], transcription: str, video_folder: str) -> None:
    try:
        word_count = len(transcription.split()) if transcription and transcription.strip() else 0
        json_data = {
            '_metadata': {
                'source': 'youtube_data_api_v3',
                'collected_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'schema_version': '2.0',
            },
            'video': video_info,
            'transcription': {
                'text': transcription or '',
                'language': video_info.get('language', 'unknown'),
                'source': 'auto_generated',
                'word_count': word_count,
                'has_timestamps': False,
            },
            'comments': comments,
            'engagement': compute_engagement(video_info, comments),
        }
        json_file = os.path.join(video_folder, "dados.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        json_raw = {
            'video': video_info,
            'comments': comments,
            'transcription': transcription,
        }
        json_raw_file = os.path.join(video_folder, "dados_raw.json")
        with open(json_raw_file, "w", encoding="utf-8") as f:
            json.dump(json_raw, f, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"Erro ao salvar JSON: {e}")


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
        print(f"Erro ao salvar TXT: {e}")


def save_video_csv(video_info: Dict, video_folder: str) -> None:
    if not video_info:
        return

    try:
        df_video = pd.DataFrame([video_info])
        csv_video_file = os.path.join(video_folder, "video.csv")
        df_video.to_csv(csv_video_file, index=False, encoding='utf-8-sig')
    except Exception as e:
        print(f"Erro ao salvar CSV de vídeo: {e}")


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
        print(f"Erro ao salvar CSV de comentários: {e}")


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
        print(f"Erro ao salvar CSV de respostas: {e}")


def save_transcription(transcription: str, video_folder: str) -> None:
    if not transcription or not transcription.strip():
        return

    try:
        trans_file = os.path.join(video_folder, "transcricao.txt")
        with open(trans_file, "w", encoding="utf-8") as f:
            f.write(transcription)
    except Exception as e:
        print(f"Erro ao salvar transcrição: {e}")


def print_summary(video_info: Dict, comments: List[Dict], transcription: str, video_folder: str) -> None:
    print(f"✓ Dados salvos em: {video_folder}")
    saved_files = ["dados.json", "dados_raw.json", "dados.txt"]

    if video_info:
        saved_files.append("video.csv")

    if comments:
        saved_files.append(f"comentarios.csv ({len(comments)} comentários)")

    if any(c['replies'] for c in comments):
        total_respostas = sum(len(c['replies']) for c in comments)
        saved_files.append(f"respostas.csv ({total_respostas} respostas)")

    if transcription and transcription.strip():
        saved_files.append("transcricao.txt")

    for file in saved_files:
        print(f"  - {file}")


def save_video_data(video_data: Dict, video_folder: str) -> None:
    try:
        video_details = video_data.get('video_details', {})
        comments_data = video_data.get('comments_data', [])
        transcription = video_data.get('transcription', '')

        video_info = extract_video_info(video_data, video_details)
        comments = structure_comments(comments_data)

        if not video_info and not comments and not transcription:
            print(f"⚠ Nenhum dado coletado para {video_folder}")

        save_json(video_info, comments, transcription, video_folder)
        save_txt(video_info, comments, video_folder)
        save_video_csv(video_info, video_folder)
        save_comments_csv(comments, video_folder)
        save_replies_csv(comments, video_folder)
        save_transcription(transcription, video_folder)

        print_summary(video_info, comments, transcription, video_folder)

    except json.JSONDecodeError as e:
        print(f"Erro ao processar JSON dos dados: {e}")
    except Exception as e:
        print(f"Erro ao salvar dados do vídeo: {e}")