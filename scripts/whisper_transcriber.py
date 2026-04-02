# %%
import logging
import os


os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.add_dll_directory(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin")

from faster_whisper import WhisperModel

logger = logging.getLogger("YoutubeCollector")

BASE_DIR = "sua_rota"

# Extensões de vídeo aceitas
VIDEO_EXTENSIONS = (".mp4", ".webm", ".mkv", ".avi", ".mov")

model = WhisperModel("base", device="cuda", compute_type="float32")

def get_whisper_transcription(audio_file_path: str) -> str:
    try:
        segments, info = model.transcribe(audio_file_path)

        full_text = ""
        for segment in segments:
            full_text += segment.text

        return full_text.strip()

    except Exception as e:
        logger.error(f"Erro ao obter transcrição via Whisper: {e}")
        return ""


def find_video_file(video_path: str) -> str | None:
    for file in os.listdir(video_path):
        if file.lower().endswith(VIDEO_EXTENSIONS):
            return os.path.join(video_path, file)
    return None


def transcribe_all_videos(base_path=BASE_DIR):
    print(f"Buscando vídeos em: {base_path}")

    for coleta_folder in os.listdir(base_path):
        coleta_path = os.path.join(base_path, coleta_folder)

        if not os.path.isdir(coleta_path):
            continue

        for video_folder in os.listdir(coleta_path):
            video_path = os.path.join(coleta_path, video_folder)

            if not os.path.isdir(video_path):
                continue

            transcricao_path = os.path.join(video_path, "transcricao.txt")
            if os.path.exists(transcricao_path):
                print(f"[PULANDO] Transcrição já existe em: {video_path}")
                continue

            video_file = find_video_file(video_path)

            if not video_file:
                print(f"[AVISO] Nenhum vídeo encontrado em: {video_path}")
                continue

            print(f"\nTranscrevendo: {video_file}")
            transcricao = get_whisper_transcription(video_file)

            if transcricao:
                with open(transcricao_path, "w", encoding="utf-8") as f:
                    f.write(transcricao)
                print(f"[OK] Transcrição salva em: {transcricao_path}")
            else:
                print(f"[ERRO] Transcrição vazia para: {video_file}")


if __name__ == "__main__":
    transcribe_all_videos()