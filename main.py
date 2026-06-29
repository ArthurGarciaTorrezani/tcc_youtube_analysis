from datetime import datetime
import logging
import os
import time
from apscheduler.schedulers.blocking import BlockingScheduler

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import (
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

from services import (
    get_data_comments,
    get_data_videos,
    save_video_data,
)

load_dotenv()

DURATION_HOURS = 1
TIME_BETWEEN_VIDEOS = 3
TIME_FOR_BROWSER_LOAD = 3

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

def go_to_next_video(driver, wait):
    url_atual = driver.current_url

    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_DOWN)
    wait.until(lambda d: d.current_url != url_atual)
    time.sleep(TIME_BETWEEN_VIDEOS)

def collect_video_data(driver, video_index, collection_folder, stats):
    logger = logging.getLogger("YoutubeCollector")

    try:
        url_atual = driver.current_url
        video_id = url_atual.split("/shorts/")[-1].split("?")[0]

        video_folder = os.path.join(collection_folder, f"video_{video_index+1}_{video_id}")
        os.makedirs(video_folder, exist_ok=True)

        video_data = {"video_id": video_id, "url": url_atual}

        data_video = get_data_videos(video_id)
        if "error" in data_video:
            stats["videos_com_erro"] += 1
            return False

        video_data["video_details"] = data_video

        data_comments = get_data_comments(video_id)

        if isinstance(data_comments, list):
            stats["total_comentarios"] += len(data_comments)
            stats["total_respostas"] += sum(len(c.get("replies", [])) for c in data_comments)

        video_data["comments_data"] = data_comments

        save_video_data(video_data, video_folder)

        stats["videos_coletados"] += 1

        return True

    except Exception as e:
        logger.error(f"Erro ao processar vídeo: {e}", exc_info=True)
        stats["videos_com_erro"] += 1
        return False

def process_videos(driver, wait, collection_folder, stats):
    logger = logging.getLogger("YoutubeCollector")

    duration_seconds = DURATION_HOURS * 3600
    end_time = stats["inicio"].timestamp() + duration_seconds
    video_index = 0

    while time.time() < end_time:
        success = collect_video_data(
            driver, video_index, collection_folder, stats
        )

        if not success:
            logger.warning(f"Erro no vídeo {video_index}")

        try:
            go_to_next_video(driver, wait)
        except Exception as e:
            logger.warning(f"Erro ao navegar: {e}")
            break

        video_index += 1

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
        options = Options()
        options.add_argument(r"--user-data-dir=C:\chrome_automation_profile")

        logger.info("Iniciando WebDriver Chrome...")
        driver = webdriver.Chrome(options=options)

        base_route = os.getenv("BASE_ROUTE")
        driver.get(base_route)
        wait = WebDriverWait(driver, 10)
        time.sleep(TIME_FOR_BROWSER_LOAD)

        base_dir = "dados"
        os.makedirs(base_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        collection_folder = os.path.join(base_dir, f"coleta_{timestamp}")
        os.makedirs(collection_folder, exist_ok=True)
        logger.info(f"Pasta da coleta criada: {collection_folder}")

        process_videos(driver, wait, collection_folder, stats)

    except WebDriverException as e:
        logger.error(f"Erro no WebDriver: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Erro fatal na coleta: {e}", exc_info=True)
    finally:
        if driver:
            logger.info("Fechando WebDriver...")
            driver.quit()

    duracao = datetime.now() - stats["inicio"]
    logger.info(f"\n{'='*60}")
    logger.info("RESUMO DA COLETA")
    logger.info("=" * 60)
    logger.info(f"Vídeos coletados com sucesso: {stats['videos_coletados']}")
    logger.info(f"Vídeos com erro: {stats['videos_com_erro']}")
    logger.info(f"Total de comentários: {stats['total_comentarios']}")
    logger.info(f"Total de respostas: {stats['total_respostas']}")
    logger.info(f"Tempo total: {duracao}")
    if collection_folder:
        logger.info(f"Dados salvos em: {collection_folder}")
    logger.info("Coleta finalizada!")


if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="America/Sao_Paulo")

    scheduler.add_job(main, "cron", hour="00,6,12,18", minute=0)

    print("Agendador rodando... (Ctrl+C para parar)")
    scheduler.start()
    #main()