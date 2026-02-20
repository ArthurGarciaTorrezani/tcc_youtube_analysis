# %%
from datetime import datetime
import logging
import os
import time


from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from utils import (
    get_data_comments,
    get_data_videos,
    get_transcription,
    save_video_data,
)

load_dotenv()


def setup_logging(log_dir="logs"):
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"coleta_{timestamp}.log")

    logger = logging.getLogger("YoutubeCollector")
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def validate_credentials():
    logger = logging.getLogger("YoutubeCollector")

    required_vars = {
        "API_SERVICE_NAME": "Nome do serviço YouTube",
        "API_VERSION": "Versão da API",
        "API_KEY_YOUTUBE": "Chave de API do YouTube",
        "BASE_ROUTE": "URL base do YouTube",
    }

    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")

    if missing_vars:
        logger.error("Variáveis de ambiente faltando:")
        for var in missing_vars:
            logger.error(f"  - {var}")
        return False

    logger.info("✓ Todas as credenciais validadas")
    return True


def collect_video_data(driver, wait, video_index, num_videos,
                       collection_folder, stats):
    logger = logging.getLogger("YoutubeCollector")

    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"VÍDEO {video_index + 1}/{num_videos}")
        logger.info("=" * 60)

        url_atual = driver.current_url
        video_id = url_atual.split("/shorts/")[-1].split("?")[0]
        logger.info(f"Video ID: {video_id}")

        video_folder = os.path.join(collection_folder, f"video_{video_index+1}_{video_id}")

        os.makedirs(video_folder, exist_ok=True)

        video_data = {"video_id": video_id, "url": url_atual}

        logger.info("Buscando informações do vídeo...")
        data_video = get_data_videos(video_id)
        if "error" in data_video:
            logger.error(f"❌ Erro ao buscar vídeo: {data_video['error']}")
            stats["videos_com_erro"] += 1
            return False

        video_data["video_details"] = data_video
        logger.info("✓ Informações do vídeo obtidas")

        logger.info("Buscando comentários e respostas...")
        data_comments = get_data_comments(video_id)

        if isinstance(data_comments, dict) and "error" in data_comments:
            logger.warning(
                f"⚠️  Não foi possível coletar comentários: "
                f"{data_comments['error']}"
            )
            data_comments = []
        elif isinstance(data_comments, list):
            logger.info(f"✓ {len(data_comments)} comentários coletados")
            total_replies = sum(len(c.get("replies", [])) for c in data_comments)
            logger.info(f"✓ {total_replies} respostas coletadas")
            stats["total_comentarios"] += len(data_comments)
            stats["total_respostas"] += total_replies

        video_data["comments_data"] = data_comments

        logger.info("Buscando transcrição...")
        transcription = get_transcription(video_id)
        if transcription:
            logger.info(f"✓ Transcrição obtida ({len(transcription)} caracteres)")
        else:
            logger.warning("⚠️  Transcrição não disponível")
        video_data["transcription"] = transcription

        logger.info("Salvando dados coletados...")
        save_video_data(video_data, video_folder)
        logger.info("✓ Dados salvos com sucesso")

        stats["videos_coletados"] += 1

        logger.info("Navegando para próximo vídeo...")
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_DOWN)
        wait.until(lambda d: d.current_url != url_atual)
        time.sleep(2)

        return True

    except (TimeoutException, NoSuchElementException) as e:
        logger.warning(f"⚠️  Não foi possível navegar para próximo vídeo: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erro ao processar vídeo: {e}", exc_info=True)
        stats["videos_com_erro"] += 1
        return False


def process_videos(driver, wait, num_videos, collection_folder, stats):
    logger = logging.getLogger("YoutubeCollector")

    for i in range(num_videos):
        success = collect_video_data(driver, wait, i, num_videos, collection_folder, stats)
        if not success:
            logger.warning(f"Interrompendo coleta após erro no vídeo {i + 1}")
            break


def main():
    logger = setup_logging()
    driver = None

    stats = {
        "videos_coletados": 0,
        "videos_com_erro": 0,
        "total_comentarios": 0,
        "total_respostas": 0,
        "inicio": datetime.now(),
    }

    try:
        logger.info("Iniciando validação de credenciais...")
        if not validate_credentials():
            logger.error("❌ Falha na validação de credenciais")
            return

        logger.info("Iniciando WebDriver Chrome...")
        driver = webdriver.Chrome()

        base_route = os.getenv("BASE_ROUTE")
        driver.get(base_route)
        wait = WebDriverWait(driver, 10)
        time.sleep(3)

        base_dir = "dados"
        os.makedirs(base_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        collection_folder = os.path.join(base_dir, f"coleta_{timestamp}")
        os.makedirs(collection_folder, exist_ok=True)
        logger.info(f"📁 Pasta da coleta criada: {collection_folder}")

        num_videos = 2
        process_videos(driver, wait, num_videos, collection_folder, stats)

        duracao = datetime.now() - stats["inicio"]
        logger.info(f"\n{'='*60}")
        logger.info("RESUMO DA COLETA")
        logger.info("=" * 60)
        logger.info(f"✓ Vídeos coletados com sucesso: {stats['videos_coletados']}")
        logger.info(f"❌ Vídeos com erro: {stats['videos_com_erro']}")
        logger.info(f"📝 Total de comentários: {stats['total_comentarios']}")
        logger.info(f"💬 Total de respostas: {stats['total_respostas']}")
        logger.info(f"⏱️  Tempo total: {duracao}")
        logger.info(f"📁 Dados salvos em: {collection_folder}")
        logger.info("✓ Coleta finalizada com sucesso!")

    except WebDriverException as e:
        logger.error(f"❌ Erro no WebDriver: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}", exc_info=True)
    finally:
        if driver:
            logger.info("Fechando WebDriver...")
            driver.quit()


if __name__ == "__main__":
    main()