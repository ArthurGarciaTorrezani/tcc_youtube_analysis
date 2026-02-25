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

        logger.info("Salvando dados coletados (sem transcrição)...")
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
            continue

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

    collection_folder = None

    try:
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

    except WebDriverException as e:
        logger.error(f"❌ Erro no WebDriver: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"❌ Erro fatal na coleta: {e}", exc_info=True)
    finally:
        if driver:
            logger.info("Fechando WebDriver...")
            driver.quit()

    duracao = datetime.now() - stats["inicio"]
    logger.info(f"\n{'='*60}")
    logger.info("RESUMO DA COLETA")
    logger.info("=" * 60)
    logger.info(f"✓ Vídeos coletados com sucesso: {stats['videos_coletados']}")
    logger.info(f"❌ Vídeos com erro: {stats['videos_com_erro']}")
    logger.info(f"📝 Total de comentários: {stats['total_comentarios']}")
    logger.info(f"💬 Total de respostas: {stats['total_respostas']}")
    logger.info(f"⏱️  Tempo total: {duracao}")
    if collection_folder:
        logger.info(f"📁 Dados salvos em: {collection_folder}")
    logger.info("✓ Coleta finalizada!")


if __name__ == "__main__":
    main()