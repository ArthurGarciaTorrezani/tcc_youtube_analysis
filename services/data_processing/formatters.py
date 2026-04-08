import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger("YoutubeCollector")


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
                logger.error(f"Erro ao processar resposta: {exc}")
                continue

        return item_data
    except Exception as exc:
        logger.error(f"Erro ao extrair dados do comentário: {exc}")
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
        dislike_count = statistics.get('dislikeCount')
        favorite_count = statistics.get('favoriteCount')
        comment_count = statistics.get('commentCount')
        url = video_data.get('url', '')

        video_info = {
            'video_id': video_data.get('video_id'),
            'url': url,
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'published_at': snippet.get('publishedAt', ''),
            'channel_title': snippet.get('channelTitle', ''),
            'category_id': snippet.get('categoryId', 0),
            'tags': snippet.get('tags', []),
            'channel_id': snippet.get('channelId', ''),
            'view_count': (int(view_count) if view_count is not None else None),
            'like_count': (int(like_count) if like_count is not None else None),
            'dislike_count': (int(dislike_count) if dislike_count is not None else None),
            'favorite_count': (int(favorite_count) if favorite_count is not None else None),
            'comment_count': (int(comment_count) if comment_count is not None else None),
            'duration_iso': duration_iso,
            'duration_seconds': duration_seconds,
            'content_type': detect_content_type(url, duration_seconds),
            'language': snippet.get('defaultAudioLanguage', 'unknown'),
            'madeForKids': status.get('madeForKids')
        }
    except Exception as e:
        logger.error(f"Erro ao extrair dados do vídeo: {e}")

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
