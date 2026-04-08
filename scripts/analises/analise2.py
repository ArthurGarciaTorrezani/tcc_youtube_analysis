# %%
import csv
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict
import pandas as pd
from IPython.display import display
from carregar_dados import (
carregar_dados
)

@dataclass
class VideoOcorrencia:
    video_id: str
    url: str
    title: str
    description: str
    published_at: str
    channel_title: str
    channel_id: str
    view_count: float
    like_count: float
    comment_count: float
    duration_iso: str
    duration_seconds: float
    content_type: str
    language: str
    madeForKids: bool
    pessoa: str
    coleta: str
    pasta_video: str

@dataclass
class VideoDuplicado:
    video_id: str
    title: str
    url: str
    channel_title: str
    published_at: str
    aparece_em: List[VideoOcorrencia]

@dataclass
class ResultadoAnalise:
    unicos: List[VideoDuplicado]
    entre_pessoas: List[VideoDuplicado]

@dataclass
class ResultadoPorPessoa:
    pessoa: str
    likes: float
    comentarios: float

@dataclass
class Video:
    likes: float
    comentarios: float

def videos_duplicados(df: pd.DataFrame) -> ResultadoAnalise:

    duplicados_df = df[df.duplicated("video_id", keep=False)]

    resultado_unicos = []
    resultado_entre = []

    display(duplicados_df.groupby("video_id"))

    for video_id, grupo in duplicados_df.groupby("video_id"):
        ocorrencias = [
            VideoOcorrencia(**row._asdict())
            for row in grupo.itertuples(index=False)
        ]

        primeiro = ocorrencias[0]

        duplicado = VideoDuplicado(
            video_id=video_id,
            title=primeiro.title,
            url=primeiro.url,
            channel_title=primeiro.channel_title,
            published_at=primeiro.published_at,
            aparece_em=ocorrencias
        )

        resultado_unicos.append(duplicado)

        pessoas_distintas = grupo["pessoa"].nunique()

        if pessoas_distintas > 1:
            resultado_entre.append(duplicado)
    
    return ResultadoAnalise(
        unicos=resultado_unicos,
        entre_pessoas=resultado_entre,
    )

def medias_metadados(df: pd.DataFrame) -> list[ResultadoPorPessoa]:

    resultados = []

    for pessoa, grupo in df.groupby("pessoa"):
        videos = [
            Video(
                likes=row.like_count,
                comentarios=row.comment_count,
            )
            for row in grupo.itertuples(index=False)
        ]

        media_likes = sum(v.likes for v in videos) / len(videos)

        media_comentarios = sum(v.comentarios for v in videos) / len(videos)


        resultados.append(
            ResultadoPorPessoa(
                pessoa=pessoa,
                likes=media_likes,
                comentarios=media_comentarios,
            )
        )

    return resultados

def main():
    
    print("Lendo dados...")

    arquivo = "../../../../Analise_Coletas/Coletas/todos_videos.csv"

    res2 = carregar_dados(arquivo)
    display(res2[["video_id","view_count","like_count","comment_count","madeForKids","pessoa"]])


    print("Analisando duplicados...")
    resultado = videos_duplicados(res2)

    total_csvs = len(res2)
    total_unicos = res2["video_id"].nunique()
    total_duplicados = len(resultado.unicos)
    nao_duplicados = total_unicos - total_duplicados
    resultados_medios = medias_metadados(res2)

    print(f"\nTotal linhas (CSV): {total_csvs}")
    print(f"Total vídeos únicos: {total_unicos}")
    print(f"Não duplicados: {nao_duplicados}")

    print(f"\nDuplicados únicos: {total_duplicados}")
    print(f"Entre pessoas: {len(resultado.entre_pessoas)}")

    print(f"Resultados medios:",resultados_medios)


if __name__ == "__main__":
    main()