from pytubefix import YouTube
from pytubefix.cli import on_progress


def download_video(url, output_path):
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        print(f"Título: {yt.title}")
        ys = yt.streams.get_highest_resolution()
        
        ys.download(output_path=output_path)
        print("Download concluído")
        
    except Exception as e:
        print(f"Erro ao fazer download: {e}")