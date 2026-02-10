import googleapiclient.discovery
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from youtube_transcript_api import YouTubeTranscriptApi
from pytubefix import YouTube
from pytubefix.cli import on_progress
import time
import os
from dotenv import load_dotenv
import json


load_dotenv()

def format_dict_to_lines(data, indent=0):
    lines = []
    prefix = "  " * indent
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.extend(format_dict_to_lines(value, indent + 1))
            else:
                lines.append(f"{prefix}{key}: {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}[{i}]:")
                lines.extend(format_dict_to_lines(item, indent + 1))
            else:
                lines.append(f"{prefix}[{i}]: {item}")
    else:
        lines.append(f"{prefix}{data}")
    
    return lines

def download_video(url):
     yt = YouTube(url, on_progress_callback = on_progress)
     print(yt.title)
     ys = yt.streams.get_highest_resolution()
     ys.download(output_path=os.getenv("DOWNLOAD_OUTPUT"))
     
def get_data_videos(video_id, youtube):
    request = youtube.videos().list(
        part="contentDetails,id,liveStreamingDetails,localizations,"
             "player,recordingDetails,snippet,statistics,status,topicDetails",
        id=video_id
        )
    
    return request.execute()

def get_data_comments(video_id, youtube):
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=1
        )
    
    return request.execute()

def get_transcription(video_id):
    ytt_api = YouTubeTranscriptApi().fetch(video_id, languages=['pt', 'en'])
    
    return " ".join([snippet.text for snippet in ytt_api.snippets])

def get_youtube_instance():
    api_service_name = os.getenv("API_SERVICE_NAME")
    api_version = os.getenv("API_VERSION")
    api_key = os.getenv("API_KEY")

    return googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key
    )

def main():
    youtube = get_youtube_instance()

    driver = webdriver.Chrome()
    driver.get(os.getenv("BASE_ROUTE"))

    wait = WebDriverWait(driver, 10)
    time.sleep(3) 

    all_videos_data = []

    for i in range(2):
        print(f"\n{'='*60}")
        print(f"VÍDEO {i+1}")
        print('='*60)

        url_atual = driver.current_url

        video_id = url_atual.split("/shorts/")[-1].split("?")[0]
        
        video_data = {
            "video_number": i + 1,
            "video_id": video_id,
            "url": url_atual
        }

        data_video = get_data_videos(video_id, youtube)
        video_data["video_details"] = data_video

        data_comments = get_data_comments(video_id, youtube)
        video_data["comments_data"] = data_comments

        transcription = get_transcription(video_id)
        video_data["transcription"] = transcription

        all_videos_data.append(video_data)

        print("\n--- DADOS FORMATADOS ---\n")
        formatted_lines = format_dict_to_lines(video_data)
        formatted_text = "\n".join(formatted_lines)
        print(formatted_text)
        
        print("\n--- DOWNLOAD ---")
        download_video(url_atual)

        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_DOWN)
        wait.until(lambda d: d.current_url != url_atual)
        time.sleep(2) 

    driver.quit()

    output_file = "videos_data_formatted.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        for video in all_videos_data:
            f.write("="*60 + "\n")
            f.write(f"VÍDEO {video['video_number']}\n")
            f.write("="*60 + "\n\n")
            formatted_lines = format_dict_to_lines(video)
            f.write("\n".join(formatted_lines))
            f.write("\n\n")
    
    print(f"\n✓ Dados salvos em '{output_file}'")

    with open("videos_data.json", "w", encoding="utf-8") as f:
        json.dump(all_videos_data, f, indent=2, ensure_ascii=False)
    
    print("✓ Dados salvos em 'videos_data.json'")

if __name__ == "__main__":
    main()