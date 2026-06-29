# %%
import os
import pandas as pd


def carregar_videos(base_path, pessoa):
    todas_linhas = []

    print(f"Buscando vídeos de '{pessoa}' em: {base_path}")

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

                # adiciona informações extras
                df["pessoa"] = pessoa
                df["coleta"] = coleta_folder
                df["pasta_video"] = video_folder

                todas_linhas.append(df)

            except Exception as e:
                print(f"[ERRO] Falha ao ler {video_csv}: {e}")

    return todas_linhas


if __name__ == "__main__":

    OUTPUT = r"C:\Users\Arthur\Desktop\Arthur\TCC\Analise_Coletas\Coletas\todos_videos_p9.csv"

    coletas = [
        (
            "Menino",
            r"C:\Users\Arthur\Desktop\Arthur\TCC\Analise_Coletas\Coletas\Coletas Menino"
        ),
        (
            "Menina",
            r"C:\Users\Arthur\Desktop\Arthur\TCC\Analise_Coletas\Coletas\Coletas Menina"
        ),
    ]

    todos_dataframes = []

    # =========================================================
    # Carrega todos os CSVs
    # =========================================================
    for pessoa, caminho in coletas:

        dfs = carregar_videos(caminho, pessoa)

        todos_dataframes.extend(dfs)

    if not todos_dataframes:
        print("Nenhum CSV encontrado.")
        exit()

    # =========================================================
    # Junta tudo
    # =========================================================
    df_final = pd.concat(todos_dataframes, ignore_index=True)

    # =========================================================
    # Cria numeração das coletas
    # mesma coleta temporal = mesmo número
    # =========================================================
    coletas_ordenadas = sorted(df_final["coleta"].unique())

    coleta_map = {
        coleta_nome: f"coleta{i + 1}"
        for i, coleta_nome in enumerate(coletas_ordenadas)
    }


    # =========================================================
    # Mostra mapeamento
    # =========================================================
    print("\nMapeamento das coletas:")

    for original, novo in coleta_map.items():
        print(f"{original} -> {novo}")

    # =========================================================
    # Salva CSV final
    # =========================================================
    df_final.to_csv(
        OUTPUT,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nCSV salvo em:")
    print(OUTPUT)

    print(f"\nTotal de linhas: {len(df_final)}")

    # =========================================================
    # Exibe apenas coletas únicas
    # =========================================================
    print("\nResumo das coletas:")

    print(
        df_final[
            ["pessoa", "coleta"]
        ]
        .drop_duplicates()
        .sort_values(["pessoa"])
    )