import logging
import os

from yt_dlp import YoutubeDL

logger = logging.getLogger("YoutubeCollector")


def download_video(video_id: str, output_folder: str) -> str:
    try:
        video_url = f"https://www.youtube.com/shorts/{video_id}"
        output_template = os.path.join(output_folder, f"{video_id}.%(ext)s")

        logger.info(f"Iniciando download do vídeo: {video_id}")

        ydl_opts = {
            "outtmpl": output_template,
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)

        if filename and os.path.exists(filename):
            logger.info(f"✓ Vídeo baixado: {filename}")
            return filename

        downloaded = _find_downloaded_file(output_folder, video_id)
        if downloaded:
            logger.info(f"✓ Vídeo baixado: {downloaded}")
            return downloaded

        logger.warning(f"⚠️  Arquivo baixado não encontrado para {video_id}")
        return ""

    except Exception as e:
        logger.error(f"Erro ao baixar vídeo {video_id}: {e}")
        return ""


def _find_downloaded_file(folder: str, video_id: str) -> str:
    try:
        for filename in os.listdir(folder):
            if filename.startswith(video_id) and not filename.endswith(".part"):
                filepath = os.path.join(folder, filename)
                if os.path.isfile(filepath):
                    return filepath
    except Exception as e:
        logger.error(f"Erro ao procurar arquivo baixado: {e}")
    return ""


