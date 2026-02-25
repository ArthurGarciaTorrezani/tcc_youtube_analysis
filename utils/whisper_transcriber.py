# %%

import logging
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.add_dll_directory(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin")

from faster_whisper import WhisperModel

logger = logging.getLogger("YoutubeCollector")

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


