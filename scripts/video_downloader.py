import os
import csv
from pytubefix import YouTube

BASE_DIR = "sua_rota"

def download_video(url, output_path):
    yt = YouTube(url)
    print(f"Baixando: {yt.title}")
    ys = yt.streams.get_highest_resolution()
    ys.download(output_path=output_path)
    print(f"Salvo em: {output_path}")


def download_all_videos(base_path=BASE_DIR):
    """
    Percorre todas as pastas de coleta dentro de 'dados',
    encontra cada pasta de vídeo (video_X_...), lê o video.csv
    e faz o download do vídeo na própria pasta do vídeo.
    """

    print(f"Buscando vídeos em: {base_path}")

    for coleta_folder in os.listdir(base_path):
        coleta_path = os.path.join(base_path, coleta_folder)

        if not os.path.isdir(coleta_path):
            continue

        for video_folder in os.listdir(coleta_path):
            video_path = os.path.join(coleta_path, video_folder)

            if not os.path.isdir(video_path):
                continue

            video_csv = os.path.join(video_path, "video.csv")

            if not os.path.exists(video_csv):
                print(f"[AVISO] video.csv não encontrado em: {video_path}")
                continue

            with open(video_csv, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Ajuste o nome da coluna conforme o seu CSV
                    video_id = row.get("id") or row.get("video_id") or list(row.values())[0]
                    video_id = video_id.strip()

                    url = f"https://www.youtube.com/shorts/{video_id}"
                    print(f"\nProcessando: {url}")

                    try:
                        download_video(url, output_path=video_path)
                    except Exception as e:
                        print(f"[ERRO] Falha ao baixar {url}: {e}")


if __name__ == "__main__":
    download_all_videos()