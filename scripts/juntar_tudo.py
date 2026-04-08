import os
import csv
import pandas as pd

BASE_DIR = r"C:\Users\Arthur\Desktop\Arthur\TCC\Analise_Coletas\Coletas\Coletas Maria\dados"
# juntar as coletas de cada usuario em um lugar só, ate o momento é manual, altero a rota para pegar o de cada um e salvar n caminho que quero
def juntar_todos_videos_csv(base_path=BASE_DIR, output_file="todos_videos.csv"):

    print(f"Buscando vídeos em: {base_path}")

    todas_linhas = []

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

            try:
                df = pd.read_csv(video_csv)

                # opcional: adicionar origem do arquivo
                df["pessoa"] = "Maria"
                df["coleta"] = coleta_folder
                df["pasta_video"] = video_folder

                todas_linhas.append(df)

            except Exception as e:
                print(f"[ERRO] Falha ao ler {video_csv}: {e}")

    if not todas_linhas:
        print("Nenhum CSV encontrado.")
        return

    df_final = pd.concat(todas_linhas, ignore_index=True)

    output_path = os.path.join(r"C:\Users\Arthur\Desktop\Arthur\TCC\Analise_Coletas\Coletas", output_file)
    df_final.to_csv(output_path, mode="a",index=False, encoding="utf-8-sig")

    print(f"\nCSV final salvo em: {output_path}")
    print(f"Total de vídeos: {len(df_final)}")

if __name__ == "__main__":
    juntar_todos_videos_csv(base_path=BASE_DIR)