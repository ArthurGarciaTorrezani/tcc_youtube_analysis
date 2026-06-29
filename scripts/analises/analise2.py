#%% 
from matplotlib import pyplot as plt
import pandas as pd
from IPython.display import display
from carregar_dados import carregar_dados


def videos_duplicados(df: pd.DataFrame) -> dict:
    dup = df[df.duplicated("video_id", keep=False)]
    repetidos = dup.groupby("video_id").apply(lambda g: g.to_dict("records")).to_dict()
    entre_pessoas = {
        vid: rows
        for vid, rows in repetidos.items()
        if len(set(r["pessoa"] for r in rows)) > 1
    }
    return {"repetidos": repetidos, "entre_pessoas": entre_pessoas}


def canais_duplicados(df: pd.DataFrame) -> dict:
    df_c = df.drop_duplicates(subset=["channel_id", "pessoa", "coleta"])
    dup = df_c[df_c.duplicated("channel_id", keep=False)]
    repetidos = dup.groupby("channel_id").apply(lambda g: g.to_dict("records")).to_dict()
    entre_pessoas = {
        cid: rows
        for cid, rows in repetidos.items()
        if len(set(r["pessoa"] for r in rows)) > 1
    }
    return {"repetidos": repetidos, "entre_pessoas": entre_pessoas}


def medias_metadados(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.drop_duplicates(subset=["video_id", "pessoa"])
        .groupby("pessoa")[["like_count", "comment_count"]]
        .mean()
        .reset_index()
    )


def print_analises(df: pd.DataFrame, videos: dict, canais: dict, medias: pd.DataFrame):
    total_unicos = df["video_id"].nunique()

    ids_repetidos = len(videos["repetidos"])

    ids_unicos_sem_repeticao = total_unicos - ids_repetidos

    print(f"Total de recomendações coletadas: {len(df)}")    
    print(f"Total vídeos únicos: {total_unicos}")

    print(
        f"Vídeos que apareceram mais de uma vez: "
        f"{ids_repetidos}"
    )

    print(
        f"Vídeos que apareceram exatamente uma vez: "
        f"{ids_unicos_sem_repeticao}"
    )

    print(
        f"Vídeos repetidos entre pessoas: "
        f"{len(videos['entre_pessoas'])}"
    )

    print(f"\nTotal canais únicos: {df['channel_id'].nunique()}")
    print(f"Canais repetidos: {len(canais['repetidos'])}")
    print(f"Canais repetidos entre pessoas: {len(canais['entre_pessoas'])}")

    print("\nMédias por pessoa:")
    for _, row in medias.iterrows():
        print(f"  {row['pessoa']}: likes={row['like_count']:.1f}, comentários={row['comment_count']:.1f}")


def plot_analise_duplicados(df: pd.DataFrame, videos: dict, canais: dict, medias: pd.DataFrame):

    # ==========================================
    # PRÉ-CÁLCULOS — vídeos
    # ==========================================
    total_unicos = df["video_id"].nunique()
    total_repetidos = len(videos["repetidos"])
    nao_duplicados = total_unicos - total_repetidos
    entre_pessoas_v = len(videos["entre_pessoas"])
    largura = 0.35

    repetidos_proprios_v = {}
    for vid, rows in videos["repetidos"].items():
        pessoas = set(r["pessoa"] for r in rows)
        if len(pessoas) == 1:
            p = list(pessoas)[0]
            repetidos_proprios_v[p] = repetidos_proprios_v.get(p, 0) + 1

    repetidos_entre_v = {}
    for vid, rows in videos["entre_pessoas"].items():
        for p in set(r["pessoa"] for r in rows):
            repetidos_entre_v[p] = repetidos_entre_v.get(p, 0) + 1

    # ==========================================
    # PRÉ-CÁLCULOS — canais
    # ==========================================
    total_canais = df["channel_id"].nunique()
    total_canais_rep = len(canais["repetidos"])
    canais_nao_dup = total_canais - total_canais_rep
    entre_pessoas_c = len(canais["entre_pessoas"])

    repetidos_proprios_c = {}
    for cid, rows in canais["repetidos"].items():
        pessoas = set(r["pessoa"] for r in rows)
        if len(pessoas) == 1:
            p = list(pessoas)[0]
            repetidos_proprios_c[p] = repetidos_proprios_c.get(p, 0) + 1

    repetidos_entre_c = {}
    for cid, rows in canais["entre_pessoas"].items():
        for p in set(r["pessoa"] for r in rows):
            repetidos_entre_c[p] = repetidos_entre_c.get(p, 0) + 1

    pessoas_v = sorted(set(list(repetidos_proprios_v.keys()) + list(repetidos_entre_v.keys())))
    pessoas_c = sorted(set(list(repetidos_proprios_c.keys()) + list(repetidos_entre_c.keys())))
    pessoas_medias = medias["pessoa"].tolist()
    likes = medias["like_count"].tolist()
    comentarios = medias["comment_count"].tolist()

    # ==========================================
    # LAYOUT
    # ==========================================
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle("Análise de vídeos e canais duplicados", fontsize=13, fontweight="bold")

    def rotular(ax, bars, valores, fmt="{}", fontsize=10):
        for bar, v in zip(bars, valores):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                fmt.format(v),
                ha="center", va="bottom", fontsize=fontsize
            )

    # ==========================================
    # [0,0] Composição dos vídeos
    # ==========================================
    labels = ["Total\nlinhas", "Vídeos\núnicos", "Apenas\n1 vez", "Repetidos", "Entre\npessoas"]
    valores = [len(df), total_unicos, nao_duplicados, total_repetidos, entre_pessoas_v]
    cores = ["steelblue", "steelblue", "orange", "tomato", "tomato"]

    bars = axes[0, 0].bar(labels, valores, color=cores)
    axes[0, 0].set_title("Composição dos vídeos únicos")
    axes[0, 0].set_ylabel("Quantidade")
    axes[0, 0].grid(axis="y", linestyle="--", alpha=0.4)
    rotular(axes[0, 0], bars, valores)

    # ==========================================
    # [0,0] Composição dos vídeos únicos
    # ==========================================
    labels = [
        "2+\nvezes",
        "Entre\npessoas"
    ]

    valores = [

        total_repetidos,
        entre_pessoas_v
    ]

    cores = [
        "orange",
        "steelblue",
        "tomato"
    ]

    bars = axes[0, 0].bar(
        labels,
        valores,
        color=cores
    )

    axes[0, 0].set_title(
        f"Composição dos {total_unicos} vídeos únicos"
    )

    axes[0, 0].set_ylabel("Quantidade de vídeos")
    axes[0, 0].grid(axis="y", linestyle="--", alpha=0.4)

    rotular(
        axes[0, 0],
        bars,
        valores
    )

    # ==========================================
    # [0,1] Vídeos repetidos por pessoa
    # ==========================================
    labels_v = ["Entre pessoas"] + pessoas_v
    valores_v = [entre_pessoas_v] + [repetidos_proprios_v.get(p, 0) for p in pessoas_v]
    cores_v = ["orange"] + ["mediumpurple"] * len(pessoas_v)

    bars = axes[0, 1].bar(labels_v, valores_v, color=cores_v)
    axes[0, 1].set_title("Vídeos repetidos")
    axes[0, 1].set_ylabel("Quantidade")
    axes[0, 1].grid(axis="y", linestyle="--", alpha=0.4)
    rotular(axes[0, 1], bars, valores_v)

    # ==========================================
    # [0,2] Médias de likes e comentários
    # ==========================================
    x_m = range(len(pessoas_medias))
    b3 = axes[0, 2].bar([i - largura/2 for i in x_m], likes,       largura, label="Likes",       color="steelblue")
    b4 = axes[0, 2].bar([i + largura/2 for i in x_m], comentarios, largura, label="Comentários", color="mediumseagreen")
    axes[0, 2].set_xticks(list(x_m))
    axes[0, 2].set_xticklabels(pessoas_medias)
    axes[0, 2].set_title("Médias de likes e comentários")
    axes[0, 2].set_ylabel("Média")
    axes[0, 2].legend(fontsize=8)
    axes[0, 2].grid(axis="y", linestyle="--", alpha=0.4)
    rotular(axes[0, 2], b3, likes,       fmt="{:.0f}", fontsize=8)
    rotular(axes[0, 2], b4, comentarios, fmt="{:.0f}", fontsize=8)

    # ==========================================
    # [1,0] Composição dos canais
    # ==========================================
    labels_cc = ["Canais\núnicos", "Não\nduplicados", "Repetidos", "Entre\npessoas"]
    valores_cc = [total_canais, canais_nao_dup, total_canais_rep, entre_pessoas_c]
    cores_cc = ["steelblue", "orange", "tomato", "tomato"]

    bars = axes[1, 0].bar(labels_cc, valores_cc, color=cores_cc)
    axes[1, 0].set_title("Composição dos canais únicos")
    axes[1, 0].set_ylabel("Quantidade")
    axes[1, 0].grid(axis="y", linestyle="--", alpha=0.4)
    rotular(axes[1, 0], bars, valores_cc)

    # ==========================================
    # [1,1] Canais repetidos por pessoa
    # ==========================================
    labels_cp = ["Entre pessoas"] + pessoas_c
    valores_cp = [entre_pessoas_c] + [repetidos_proprios_c.get(p, 0) for p in pessoas_c]
    cores_cp = ["orange"] + ["mediumpurple"] * len(pessoas_c)

    bars = axes[1, 1].bar(labels_cp, valores_cp, color=cores_cp)
    axes[1, 1].set_title("Canais repetidos")
    axes[1, 1].set_ylabel("Quantidade")
    axes[1, 1].grid(axis="y", linestyle="--", alpha=0.4)
    rotular(axes[1, 1], bars, valores_cp)

    # ==========================================
    # [1,2] Canais exclusivos vs em comum
    # ==========================================
    canais_por_pessoa = (
        df.drop_duplicates(subset=["channel_id", "pessoa"])
        .groupby("pessoa")["channel_id"]
        .apply(set)
    )

    if len(canais_por_pessoa) >= 2:
        p0, p1 = canais_por_pessoa.index[0], canais_por_pessoa.index[1]
        s0, s1 = canais_por_pessoa.iloc[0], canais_por_pessoa.iloc[1]

        labels_venn = [f"Só {p0}", "Em comum", f"Só {p1}"]
        valores_venn = [len(s0 - s1), len(s0 & s1), len(s1 - s0)]
        cores_venn = ["steelblue", "mediumseagreen", "tomato"]

        bars = axes[1, 2].bar(labels_venn, valores_venn, color=cores_venn)
        axes[1, 2].set_title("Canais exclusivos vs em comum")
        axes[1, 2].set_ylabel("Quantidade de canais")
        axes[1, 2].grid(axis="y", linestyle="--", alpha=0.4)
        rotular(axes[1, 2], bars, valores_venn)

    plt.tight_layout()
    plt.show()


def analise_quantidade_videos(df: pd.DataFrame):

    resultado = (
        df.groupby("pessoa")["video_id"]
        .count()
        .reset_index(name="quantidade")
    )

    print(resultado)

    fig, ax = plt.subplots(figsize=(6, 4))

    bars = ax.bar(
        resultado["pessoa"],
        resultado["quantidade"],
        color=["steelblue", "tomato"]
    )

    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height(),
            f"{int(bar.get_height())}",
            ha="center",
            va="bottom"
        )

    ax.set_title("Quantidade total de vídeos por perfil")
    ax.set_ylabel("Quantidade de vídeos")

    plt.tight_layout()
    plt.show()

def analise_videos_unicos(df: pd.DataFrame):

    resultado = (
        df.groupby("pessoa")["video_id"]
        .nunique()
        .reset_index(name="quantidade")
    )

    print(resultado)

    fig, ax = plt.subplots(figsize=(6, 4))

    bars = ax.bar(
        resultado["pessoa"],
        resultado["quantidade"],
        color=["steelblue", "tomato"]
    )

    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height(),
            f"{int(bar.get_height())}",
            ha="center",
            va="bottom"
        )

    ax.set_title("Quantidade de vídeos únicos por perfil")
    ax.set_ylabel("Quantidade de vídeos únicos")

    plt.tight_layout()
    plt.show()

def analise_videos_exclusivos(df: pd.DataFrame):

    videos_por_pessoa = (
        df.groupby("pessoa")["video_id"]
        .apply(set)
    )

    p0, p1 = videos_por_pessoa.index
    s0, s1 = videos_por_pessoa.iloc[0], videos_por_pessoa.iloc[1]

    labels = [
        f"Só {p0}",
        "Em comum",
        f"Só {p1}"
    ]

    valores = [
        len(s0 - s1),
        len(s0 & s1),
        len(s1 - s0)
    ]

    fig, ax = plt.subplots(figsize=(7, 4))

    bars = ax.bar(
        labels,
        valores,
        color=["steelblue", "mediumseagreen", "tomato"]
    )

    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height(),
            f"{int(bar.get_height())}",
            ha="center",
            va="bottom"
        )

    ax.set_title("Vídeos exclusivos e compartilhados")
    ax.set_ylabel("Quantidade de vídeos")

    plt.tight_layout()
    plt.show()

def main():
    print("Lendo dados...")
    arquivo = "../../../../Analise_Coletas/Coletas/todos_videos_p9.csv"
    df = carregar_dados(arquivo)
    display(df[["video_id", "view_count", "like_count", "comment_count", "made_for_kids", "pessoa"]])

    print("\nAnalisando duplicados...")
    videos = videos_duplicados(df)
    canais = canais_duplicados(df)
    medias = medias_metadados(df)

    print_analises(df, videos, canais, medias)
    plot_analise_duplicados(df, videos, canais, medias)
    analise_quantidade_videos(df)
    analise_videos_unicos(df)
    analise_videos_exclusivos(df)
    

if __name__ == "__main__":
    main()