# %%
import os
import pandas as pd

def juntar_todos_videos_csv(base_path, pessoa, output_file):
    print(f"Buscando vídeos de '{pessoa}' em: {base_path}")

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
                print(f"  [AVISO] video.csv não encontrado em: {video_path}")
                continue

            try:
                df = pd.read_csv(video_csv)
                df["pessoa"]      = pessoa         # ← vem do parâmetro
                df["coleta"]      = coleta_folder
                df["pasta_video"] = video_folder
                todas_linhas.append(df)
            except Exception as e:
                print(f"  [ERRO] Falha ao ler {video_csv}: {e}")

    if not todas_linhas:
        print("Nenhum CSV encontrado.")
        return

    df_final = pd.concat(todas_linhas, ignore_index=True)

    arquivo_existe = os.path.exists(output_file)
    df_final.to_csv(
        output_file,
        mode="a",
        index=False,
        encoding="utf-8-sig",
        header=not arquivo_existe  # evita header duplicado
    )

    print(f"  {len(df_final)} linhas adicionadas.")
    print(f"  CSV salvo em: {output_file}")


if __name__ == "__main__":
    OUTPUT = r"C:\Users\Arthur\Desktop\Arthur\TCC\Analise_Coletas\Coletas\todos_videos_p2.csv"

    # Basta adicionar cada pessoa aqui
    coletas = [
        ("Carlos", r"C:\Users\Arthur\Desktop\Arthur\TCC\Analise_Coletas\Coletas\Coletas Carlos\dados"),
        ("Maria", r"C:\Users\Arthur\Desktop\Arthur\TCC\Analise_Coletas\Coletas\Coletas Maria\dados"),
    ]

    for pessoa, caminho in coletas:
        juntar_todos_videos_csv(
            base_path=caminho,
            pessoa=pessoa,
            output_file=OUTPUT
        )