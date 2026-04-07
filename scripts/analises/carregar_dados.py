import pandas as pd
from pathlib import Path
import csv

def extrair_numero_video(nome_dir: str) -> int:
    try:
        return int(nome_dir.split("_")[1])
    except:
        return 0


def extrair_data_hora(nome_coleta: str):
    try:
        partes = nome_coleta.split("_")
        data_raw = partes[1]
        hora_raw = partes[2]

        data = f"{data_raw[:4]}-{data_raw[4:6]}-{data_raw[6:]}"
        hora = f"{hora_raw[:2]}:{hora_raw[2:4]}:{hora_raw[4:]}"
        return data, hora
    except:
        return "desconhecida", "desconhecida"


def detectar_encoding(csv_path: Path) -> str:
    for enc in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            with open(csv_path, encoding=enc) as f:
                f.read(1)
            return enc
        except:
            continue
    return "utf-8"

def carregar_dataframe(pasta_raiz: str) -> pd.DataFrame:
    pasta_raiz = Path(pasta_raiz)
    linhas = []

    for pessoa_dir in pasta_raiz.iterdir():
        if not pessoa_dir.is_dir():
            continue

        pessoa = pessoa_dir.name
        dados_dir = pessoa_dir / "dados"

        if not dados_dir.exists():
            continue

        for coleta_dir in dados_dir.iterdir():
            if not coleta_dir.is_dir():
                continue

            coleta = coleta_dir.name
            data, hora = extrair_data_hora(coleta)

            for video_dir in sorted(coleta_dir.iterdir(), key=lambda d: extrair_numero_video(d.name)):
                csv_path = video_dir / "video.csv"
                if not csv_path.exists():
                    continue

                encoding = detectar_encoding(csv_path)

                with open(csv_path, encoding=encoding) as f:
                    reader = pd.read_csv(f,sep=",")

                    for row in reader:
                        video_id = row.get("video_id", "").strip()
                        if not video_id:
                            continue

                        like_count = row.get("like_count","")
                        if not like_count:
                            like_count = 0

                        comment_count = row.get("comment_count","")
                        if not comment_count:
                            comment_count = 0

                        linhas.append({
                            "video_id": video_id,
                            "pessoa": pessoa,
                            "like_count":like_count,
                            "comment_count":comment_count,
                            "coleta": coleta,
                            "data_coleta": data,
                            "hora_coleta": hora,
                            "numero_video": extrair_numero_video(video_dir.name),
                            "video_dir": video_dir.name,
                            "published_at": row.get("published_at", "").strip(),
                            "csv_path": str(csv_path),
                            "titulo": row.get("title", "").strip(),
                            "canal": row.get("channel_title", "").strip(),
                            "url": row.get("url", "").strip(),
                        })

    df = pd.DataFrame(linhas)

    df["like_count"] = pd.to_numeric(df["like_count"], errors="coerce")
    df["comment_count"] = pd.to_numeric(df["comment_count"], errors="coerce")

    return df
