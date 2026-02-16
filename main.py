from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
import time
import os
from dotenv import load_dotenv
from datetime import datetime

from utils import (
    get_data_videos,
    get_data_comments,
    get_transcription,
    save_video_data,
    download_video
)

load_dotenv()


def main():
    driver = None
    
    try:
        driver = webdriver.Chrome()
        
        base_route = os.getenv("BASE_ROUTE")
        if not base_route:
            print("BASE_ROUTE não configurado")
            return
        
        driver.get(base_route)
        wait = WebDriverWait(driver, 10)
        time.sleep(3)
        
        # Criar estrutura de pastas
        base_dir = "dados"
        os.makedirs(base_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        collection_folder = os.path.join(base_dir, f"coleta_{timestamp}")
        os.makedirs(collection_folder, exist_ok=True)
        print(f"Pasta da coleta criada: {collection_folder}")
        
        num_videos = 2
        
        for i in range(num_videos):
            try:
                print(f"\n{'='*60}")
                print(f"VÍDEO {i+1}/{num_videos}")
                print('='*60)
                
                url_atual = driver.current_url
                video_id = url_atual.split("/shorts/")[-1].split("?")[0]
                
                video_folder = os.path.join(collection_folder, f"video_{i+1}_{video_id}")
                os.makedirs(video_folder, exist_ok=True)
                
                video_data = {
                    "video_id": video_id,
                    "url": url_atual
                }
                
                data_video = get_data_videos(video_id)
                if "error" in data_video:
                    print("Erro ao buscar vídeo, pulando...")
                    continue
                video_data["video_details"] = data_video
                
                data_comments = get_data_comments(video_id)
                video_data["comments_data"] = data_comments
                
                transcription = get_transcription(video_id)
                video_data["transcription"] = transcription
                
                # Salvar todos os dados
                save_video_data(video_data, video_folder)
                
                print("Dados coletados")
                
                # Download do vídeo
                download_video(url_atual, video_folder)
                
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_DOWN)
                wait.until(lambda d: d.current_url != url_atual)
                time.sleep(2)
                
            except (TimeoutException, NoSuchElementException):
                print("Não foi possível navegar para próximo vídeo")
                break
            except Exception as e:
                print(f"Erro: {e}")
                continue
        
        print("\nFinalizado")
            
    except WebDriverException as e:
        print(f"Erro no WebDriver: {e}")
    except Exception as e:
        print(f"Erro fatal: {e}")
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()