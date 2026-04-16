# %%
import pandas as pd
from IPython.display import display
from dataclasses import dataclass
from typing import List
from carregar_dados import carregar_dados


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
    repetidos: List[VideoDuplicado]
    repetidos_entre_pessoas: List[VideoDuplicado]


@dataclass
class ResultadoPorPessoa:
    pessoa: str
    likes: float
    comentarios: float


def videos_duplicados(df: pd.DataFrame) -> ResultadoAnalise:
    duplicados_df = df[df.duplicated("video_id", keep=False)]

    repetidos = []
    repetidos_entre_pessoas = []

    for video_id, grupo in duplicados_df.groupby("video_id"):
        ocorrencias = [
            VideoOcorrencia(**row._asdict())
            for row in grupo.itertuples(index=False)
        ]

        primeiro = grupo.iloc[0]

        duplicado = VideoDuplicado(
            video_id=video_id,
            title=primeiro.title,
            url=primeiro.url,
            channel_title=primeiro.channel_title,
            published_at=primeiro.published_at,
            aparece_em=ocorrencias,
        )

        repetidos.append(duplicado)

        if grupo["pessoa"].nunique() > 1:
            repetidos_entre_pessoas.append(duplicado)

    return ResultadoAnalise(
        repetidos=repetidos,
        repetidos_entre_pessoas=repetidos_entre_pessoas,
    )


def medias_metadados(df: pd.DataFrame) -> list[ResultadoPorPessoa]:
    df = df.drop_duplicates(subset="video_id")
    medias = df.groupby("pessoa")[["like_count", "comment_count"]].mean()

    return [
        ResultadoPorPessoa(
            pessoa=pessoa,
            likes=row["like_count"],
            comentarios=row["comment_count"],
        )
        for pessoa, row in medias.iterrows()
    ]


def print_medias(medias: list[ResultadoPorPessoa]):
    print("\nMédias por pessoa:")
    for r in medias:
        print(f"  {r.pessoa}: likes={r.likes:.1f}, comentários={r.comentarios:.1f}")


def print_analises(dados_gerais, resultado_duplicados, medias):
    total_linhas = len(dados_gerais)
    total_unicos = dados_gerais["video_id"].nunique()
    total_repetidos = len(resultado_duplicados.repetidos)
    nao_duplicados = total_unicos - total_repetidos

    print(f"\nTotal linhas (CSV): {total_linhas}")
    print(f"Total vídeos únicos: {total_unicos}")
    print(f"Não duplicados: {nao_duplicados}")
    print(f"\nVídeos repetidos: {total_repetidos}")
    print(f"Repetidos entre pessoas: {len(resultado_duplicados.repetidos_entre_pessoas)}")

    print_medias(medias)


def main():
    print("Lendo dados...")
    arquivo = "../../../../Analise_Coletas/Coletas/todos_videos.csv"
    df = carregar_dados(arquivo)
    display(df[["video_id", "view_count", "like_count", "comment_count", "madeForKids", "pessoa"]])

    print("\nAnalisando duplicados...")
    resultado = videos_duplicados(df)

    medias = medias_metadados(df)

    print_analises(df, resultado, medias)


if __name__ == "__main__":
    main()