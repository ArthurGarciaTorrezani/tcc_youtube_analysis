#%%
import pandas as pd
import matplotlib.pyplot as plt

from carregar_dados import carregar_dados


# ==========================================================
# FUNÇÃO AUXILIAR
# ==========================================================
def adicionar_rotulos(ax, bars):

    for bar in bars:
        altura = bar.get_height()

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            altura,
            f"{int(altura)}",
            ha="center",
            va="bottom"
        )


# ==========================================================
# 1. TOTAL DE RECOMENDAÇÕES COLETADAS
# ==========================================================
def total_videos_coletados(df):

    total_geral = len(df)

    total_por_pessoa = (
        df.groupby("pessoa")
        .size()
        .reset_index(name="quantidade")
    )

    print("\n=== TOTAL DE RECOMENDAÇÕES COLETADAS ===")
    print(f"Total geral: {total_geral}")
    print(total_por_pessoa)

    return total_por_pessoa


def grafico_total_videos(df):

    resultado = total_videos_coletados(df)

    fig, ax = plt.subplots(figsize=(6, 4))

    bars = ax.bar(
        resultado["pessoa"],
        resultado["quantidade"]
    )

    ax.set_title("Total de recomendações coletadas")
    ax.set_ylabel("Quantidade")

    adicionar_rotulos(ax, bars)

    plt.tight_layout()
    plt.show()


# ==========================================================
# 2. VÍDEOS ÚNICOS POR PERFIL
# ==========================================================
def videos_unicos_por_perfil(df):

    resultado = (
        df.groupby("pessoa")["video_id"]
        .nunique()
        .reset_index(name="videos_unicos")
    )

    print("\n=== VÍDEOS ÚNICOS POR PERFIL ===")
    print(resultado)

    return resultado


def grafico_videos_unicos(df):

    resultado = videos_unicos_por_perfil(df)

    fig, ax = plt.subplots(figsize=(6, 4))

    bars = ax.bar(
        resultado["pessoa"],
        resultado["videos_unicos"]
    )

    ax.set_title("Vídeos únicos por perfil")
    ax.set_ylabel("Quantidade")

    adicionar_rotulos(ax, bars)

    plt.tight_layout()
    plt.show()


# ==========================================================
# 3. VÍDEOS COMPARTILHADOS
# ==========================================================
def videos_compartilhados(df):

    videos_por_pessoa = (
        df.groupby("pessoa")["video_id"]
        .apply(set)
    )

    p0, p1 = videos_por_pessoa.index
    s0, s1 = videos_por_pessoa.iloc[0], videos_por_pessoa.iloc[1]

    compartilhados = s0.intersection(s1)

    print("\n=== VÍDEOS COMPARTILHADOS ===")
    print(f"{p0} x {p1}: {len(compartilhados)}")

    return compartilhados


# ==========================================================
# 4. VÍDEOS EXCLUSIVOS
# ==========================================================
def videos_exclusivos(df):

    videos_por_pessoa = (
        df.groupby("pessoa")["video_id"]
        .apply(set)
    )

    p0, p1 = videos_por_pessoa.index
    s0, s1 = videos_por_pessoa.iloc[0], videos_por_pessoa.iloc[1]

    exclusivos_p0 = s0 - s1
    exclusivos_p1 = s1 - s0

    print("\n=== VÍDEOS EXCLUSIVOS ===")
    print(f"{p0}: {len(exclusivos_p0)}")
    print(f"{p1}: {len(exclusivos_p1)}")

    return {
        p0: exclusivos_p0,
        p1: exclusivos_p1
    }


def grafico_videos_compartilhados(df):

    videos_por_pessoa = (
        df.groupby("pessoa")["video_id"]
        .apply(set)
    )

    p0, p1 = videos_por_pessoa.index
    s0, s1 = videos_por_pessoa.iloc[0], videos_por_pessoa.iloc[1]

    exclusivos_p0 = len(s0 - s1)
    compartilhados = len(s0 & s1)
    exclusivos_p1 = len(s1 - s0)

    labels = [
        f"Somente\n{p0}",
        "Compartilhados",
        f"Somente\n{p1}"
    ]

    valores = [
        exclusivos_p0,
        compartilhados,
        exclusivos_p1
    ]

    fig, ax = plt.subplots(figsize=(7, 4))

    bars = ax.bar(labels, valores)

    ax.set_title("Vídeos exclusivos e compartilhados")
    ax.set_ylabel("Quantidade")

    adicionar_rotulos(ax, bars)

    plt.tight_layout()
    plt.show()


# ==========================================================
# 5. CANAIS ÚNICOS POR PERFIL
# ==========================================================
def canais_unicos_por_perfil(df):

    resultado = (
        df.groupby("pessoa")["channel_id"]
        .nunique()
        .reset_index(name="canais_unicos")
    )

    print("\n=== CANAIS ÚNICOS POR PERFIL ===")
    print(resultado)

    return resultado


def grafico_canais_unicos(df):

    resultado = canais_unicos_por_perfil(df)

    fig, ax = plt.subplots(figsize=(6, 4))

    bars = ax.bar(
        resultado["pessoa"],
        resultado["canais_unicos"]
    )

    ax.set_title("Canais únicos por perfil")
    ax.set_ylabel("Quantidade")

    adicionar_rotulos(ax, bars)

    plt.tight_layout()
    plt.show()


# ==========================================================
# 6. CANAIS COMPARTILHADOS
# ==========================================================
def canais_compartilhados(df):

    canais_por_pessoa = (
        df.groupby("pessoa")["channel_id"]
        .apply(set)
    )

    p0, p1 = canais_por_pessoa.index
    s0, s1 = canais_por_pessoa.iloc[0], canais_por_pessoa.iloc[1]

    compartilhados = s0.intersection(s1)

    print("\n=== CANAIS COMPARTILHADOS ===")
    print(f"{p0} x {p1}: {len(compartilhados)}")

    return compartilhados


def grafico_canais_compartilhados(df):

    canais_por_pessoa = (
        df.groupby("pessoa")["channel_id"]
        .apply(set)
    )

    p0, p1 = canais_por_pessoa.index
    s0, s1 = canais_por_pessoa.iloc[0], canais_por_pessoa.iloc[1]

    exclusivos_p0 = len(s0 - s1)
    compartilhados = len(s0 & s1)
    exclusivos_p1 = len(s1 - s0)

    labels = [
        f"Somente\n{p0}",
        "Compartilhados",
        f"Somente\n{p1}"
    ]

    valores = [
        exclusivos_p0,
        compartilhados,
        exclusivos_p1
    ]

    fig, ax = plt.subplots(figsize=(7, 4))

    bars = ax.bar(labels, valores)

    ax.set_title("Canais exclusivos e compartilhados")
    ax.set_ylabel("Quantidade")

    adicionar_rotulos(ax, bars)

    plt.tight_layout()
    plt.show()


# ==========================================================
# 7. METADADOS
# ==========================================================
def estatisticas_metadados(df):

    resultado = (
        df.drop_duplicates(
            subset=["video_id", "pessoa"]
        )
        .groupby("pessoa")[
            [
                "view_count",
                "like_count",
                "comment_count"
            ]
        ]
        .mean()
        .round(2)
        .reset_index()
    )

    print("\n=== MÉDIAS DOS METADADOS ===")
    print(resultado)

    return resultado


def grafico_metadados(df):

    medias = estatisticas_metadados(df)

    largura = 0.25

    x = range(len(medias))

    fig, ax = plt.subplots(figsize=(8, 4))

    b1 = ax.bar(
        [i - largura for i in x],
        medias["view_count"],
        largura,
        label="Views"
    )

    b2 = ax.bar(
        x,
        medias["like_count"],
        largura,
        label="Likes"
    )

    b3 = ax.bar(
        [i + largura for i in x],
        medias["comment_count"],
        largura,
        label="Comentários"
    )

    ax.set_xticks(list(x))
    ax.set_xticklabels(medias["pessoa"])

    ax.set_title("Média dos metadados")
    ax.legend()

    plt.tight_layout()
    plt.show()



# ==========================================================
# MAIN
# ==========================================================
def main():

    arquivo = "../../../../Analise_Coletas/Coletas/todos_videos_p9.csv"

    df = carregar_dados(arquivo)

    # MÉTRICAS
    #total_videos_coletados(df)
    #videos_unicos_por_perfil(df)
    #videos_compartilhados(df)
    #videos_exclusivos(df)

    #canais_unicos_por_perfil(df)
    #canais_compartilhados(df)

    #estatisticas_metadados(df)

    # GRÁFICOS
    grafico_total_videos(df)
    grafico_videos_unicos(df)
    grafico_videos_compartilhados(df)

    grafico_canais_unicos(df)
    grafico_canais_compartilhados(df)

    grafico_metadados(df)


if __name__ == "__main__":
    main()