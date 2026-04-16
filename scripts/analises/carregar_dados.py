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

def carregar_dados(pasta_raiz: str) -> pd.DataFrame:
    pasta_raiz = Path(pasta_raiz)
    df = pd.read_csv(pasta_raiz)
    df
    df.head()
    return df