# %%
import csv
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict
import pandas as pd

from carregar_dados import (
carregar_dataframe
)

@dataclass
class VideoOcorrencia:
    video_id: str
    pessoa: str
    coleta: str
    data_coleta: str
    hora_coleta: str
    numero_video: int
    video_dir: str
    published_at: str
    csv_path: str
    titulo: str
    canal: str
    url: str
    like_count:float
    comment_count:float



@dataclass
class VideoDuplicado:
    video_id: str
    titulo: str
    url: str
    canal: str
    published_at: str
    aparece_em: List[VideoOcorrencia]


@dataclass
class ResultadoAnalise:
    unicos: List[VideoDuplicado]
    entre_pessoas: List[VideoDuplicado]
    mesma_pessoa: List[VideoDuplicado]
    mesma_coleta: List[VideoDuplicado]

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
    resultado_mesma_pessoa = []
    resultado_mesma_coleta = []

    for video_id, grupo in duplicados_df.groupby("video_id"):
        ocorrencias = [
            VideoOcorrencia(**row._asdict())
            for row in grupo.itertuples(index=False)
        ]

        primeiro = ocorrencias[0]

        duplicado = VideoDuplicado(
            video_id=video_id,
            titulo=primeiro.titulo,
            url=primeiro.url,
            canal=primeiro.canal,
            published_at=primeiro.published_at,
            aparece_em=ocorrencias
        )

        resultado_unicos.append(duplicado)

        pessoas_distintas = grupo["pessoa"].nunique()
        coletas_distintas = grupo[["pessoa", "coleta"]].drop_duplicates().shape[0]

        mesma_coleta_flag = (
            grupo.groupby(["pessoa", "coleta"]).size() > 1
        ).any()

        if pessoas_distintas > 1:
            resultado_entre.append(duplicado)

        if coletas_distintas > 1:
            resultado_mesma_pessoa.append(duplicado)

        if mesma_coleta_flag:
            resultado_mesma_coleta.append(duplicado)
    
    return ResultadoAnalise(
        unicos=resultado_unicos,
        entre_pessoas=resultado_entre,
        mesma_pessoa=resultado_mesma_pessoa,
        mesma_coleta=resultado_mesma_coleta
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
    pasta = "../../../../Analise_Coletas/Coletas"
    
    print("Lendo dados...")
    df = carregar_dataframe(pasta)
    print(df)
    print("Analisando duplicados...")
    resultado = videos_duplicados(df)

    total_csvs = len(df)
    total_unicos = df["video_id"].nunique()
    total_duplicados = len(resultado.unicos)
    nao_duplicados = total_unicos - total_duplicados
    resultados_medios = medias_metadados(df)

    print(f"\nTotal linhas (CSV): {total_csvs}")
    print(f"Total vídeos únicos: {total_unicos}")
    print(f"Não duplicados: {nao_duplicados}")

    print(f"\nDuplicados únicos: {total_duplicados}")
    print(f"Entre pessoas: {len(resultado.entre_pessoas)}")
    print(f"Mesma pessoa: {len(resultado.mesma_pessoa)}")
    print(f"Mesma coleta: {len(resultado.mesma_coleta)}")

    print(f"Resultados medios:",resultados_medios)


if __name__ == "__main__":
    main()