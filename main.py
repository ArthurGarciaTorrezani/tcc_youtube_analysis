from datetime import datetime
import logging
import os
import time
from apscheduler.schedulers.blocking import BlockingScheduler

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
from selenium.webdriver.chrome.options import Options

from services import (
    get_data_comments,
    get_data_videos,
    save_video_data,
)

load_dotenv()

DURATION_HOURS = 1


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


def collect_video_data(driver, wait, video_index, collection_folder, stats):
    logger = logging.getLogger("YoutubeCollector")

    try:
        elapsed = (datetime.now() - stats["inicio"]).total_seconds() / 60
        logger.info(f"\n{'='*60}")
        logger.info(f"VÍDEO {video_index + 1} | Tempo decorrido: {elapsed:.1f} min / {DURATION_HOURS * 60} min")
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
            logger.error(f"Erro ao buscar vídeo: {data_video['error']}")
            stats["videos_com_erro"] += 1
            return False

        video_data["video_details"] = data_video
        logger.info("Informações do vídeo obtidas")

        logger.info("Buscando comentários e respostas...")
        data_comments = get_data_comments(video_id)

        if isinstance(data_comments, dict) and "error" in data_comments:
            logger.warning(
                f"Não foi possível coletar comentários: "
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
        time.sleep(3)

        return True

    except (TimeoutException, NoSuchElementException) as e:
        logger.warning(f"Não foi possível navegar para próximo vídeo: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro ao processar vídeo: {e}", exc_info=True)
        stats["videos_com_erro"] += 1
        return False


def process_videos(driver, wait, collection_folder, stats):
    logger = logging.getLogger("YoutubeCollector")

    duration_seconds = DURATION_HOURS * 3600
    end_time = stats["inicio"].timestamp() + duration_seconds
    video_index = 0

    logger.info(f"Coleta iniciada. Duração máxima: {DURATION_HOURS}h")
    logger.info(f"Término previsto: {datetime.fromtimestamp(end_time).strftime('%H:%M:%S')}")

    while time.time() < end_time:
        remaining = (end_time - time.time()) / 60
        logger.info(f"Tempo restante: {remaining:.1f} min")

        success = collect_video_data(driver, wait, video_index, collection_folder, stats)
        video_index += 1

        if not success:
            logger.warning(f"Erro no vídeo {video_index}. Continuando coleta...")
            continue

    logger.info("⏱Tempo limite de 1 hora atingido. Encerrando coleta.")


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
        time.sleep(3)

        base_dir = "dados"
        os.makedirs(base_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        collection_folder = os.path.join(base_dir, f"coleta_{timestamp}")
        os.makedirs(collection_folder, exist_ok=True)
        logger.info(f"📁 Pasta da coleta criada: {collection_folder}")

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

    scheduler.add_job(main, "cron", hour="3,9,15,21", minute=0)

    print("Agendador rodando... (Ctrl+C para parar)")
    scheduler.start()