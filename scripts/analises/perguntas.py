# %%
import pandas as pd
import matplotlib.pyplot as plt
from carregar_dados import carregar_dados
import matplotlib.dates as mdates
from wordcloud import WordCloud, ImageColorGenerator, STOPWORDS
from collections import Counter
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.corpus import stopwords as nltk_stopwords



def contar_palavras(texto, stopwords, top_n=20):
    palavras = re.findall(r'\b\w+\b', texto.lower())

    palavras_filtradas = [
        p for p in palavras
        if p not in stopwords and len(p) > 1
    ]

    contagem = Counter(palavras_filtradas)

    return pd.DataFrame(
        contagem.most_common(top_n),
        columns=["palavra", "frequencia"]
    )

def analise_intersecao_acumulada(
    dados: pd.DataFrame,
    coluna_grupo: str,
    coluna_valor: str,
    titulo: str,
    ylabel: str
):

    coletas = (
        dados.groupby([coluna_grupo, "pessoa"])[coluna_valor]
        .apply(set)
        .unstack(fill_value=set())
    )

    resultado = pd.DataFrame({
        coluna_grupo: coletas.index,

        "em_comum": [
            len(c & m)
            for c, m in zip(
                coletas.get("Menino", [set()] * len(coletas)),
                coletas.get("Menina", [set()] * len(coletas))
            )
        ],

        "so_Menino": [
            len(c - m)
            for c, m in zip(
                coletas.get("Menino", [set()] * len(coletas)),
                coletas.get("Menina", [set()] * len(coletas))
            )
        ],

        "so_Menina": [
            len(m - c)
            for c, m in zip(
                coletas.get("Menino", [set()] * len(coletas)),
                coletas.get("Menina", [set()] * len(coletas))
            )
        ],

    }).sort_values(coluna_grupo)

    # ==========================================
    # ACUMULADO
    # ==========================================
    resultado["em_comum"] = resultado["em_comum"].cumsum()
    resultado["so_Menino"] = resultado["so_Menino"].cumsum()
    resultado["so_Menina"] = resultado["so_Menina"].cumsum()

    print(resultado)

    # ==========================================
    # LABELS
    # ==========================================
    if coluna_grupo in ("coleta", "coleta_hora"):
        resultado["label"] = [
            f"Coleta {i+1}"
            for i in range(len(resultado))
        ]
    else:
        resultado["label"] = [
            f"Dia {i+1}"
            for i in range(len(resultado))
        ]

    # ==========================================
    # GRÁFICO
    # ==========================================
    fig, ax = plt.subplots(figsize=(14, 5))

    x = range(len(resultado))

    series = [
        ("em_comum", "Em comum acumulado", "green"),
        ("so_Menino", "Só no Menino acumulado", "blue"),
        ("so_Menina", "Só na Menina acumulado", "orange"),
    ]

    for coluna, label, cor in series:

        ax.plot(
            x,
            resultado[coluna],
            marker="o",
            linewidth=2,
            markersize=8,
            label=label,
            color=cor
        )

        for i, v in enumerate(resultado[coluna]):

            ax.text(
                i,
                v,
                str(v),
                ha="center",
                va="bottom",
                fontsize=8
            )

    ax.set_xticks(list(x))
    ax.set_xticklabels(resultado["label"], rotation=45)

    ax.set_ylabel(ylabel)
    ax.set_title(titulo)

    ax.legend()

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.5
    )

    plt.tight_layout()
    plt.show()

def analise_intersecao(
    dados: pd.DataFrame,
    coluna_grupo: str,
    coluna_valor: str,
    titulo: str,
    ylabel: str
):

    coletas = (
        dados.groupby([coluna_grupo, "pessoa"])[coluna_valor]
        .apply(set)
        .unstack(fill_value=set())
    )

    resultado = pd.DataFrame({
        coluna_grupo: coletas.index,

        "em_comum": [
            len(c & m)
            for c, m in zip(
                coletas.get("Menino", [set()] * len(coletas)),
                coletas.get("Menina", [set()] * len(coletas))
            )
        ],

        "so_Menino": [
            len(c - m)
            for c, m in zip(
                coletas.get("Menino", [set()] * len(coletas)),
                coletas.get("Menina", [set()] * len(coletas))
            )
        ],

        "so_Menina": [
            len(m - c)
            for c, m in zip(
                coletas.get("Menino", [set()] * len(coletas)),
                coletas.get("Menina", [set()] * len(coletas))
            )
        ],

    }).sort_values(coluna_grupo)

    print(resultado)

    # ==========================================
    # LABELS DO EIXO X
    # ==========================================
    if coluna_grupo in ("coleta", "coleta_hora"):
        resultado["label"] = [f"Coleta {i+1}" for i in range(len(resultado))]
    else:
        resultado["label"] = [f"Dia {i+1}" for i in range(len(resultado))]

    # ==========================================
    # GRÁFICO
    # ==========================================
    fig, ax = plt.subplots(figsize=(14, 5))

    x = range(len(resultado))

    series = [
        ("em_comum", "Em comum", "green"),
        ("so_Menino", "Só no Menino", "blue"),
        ("so_Menina", "Só na Menina", "orange"),
    ]

    # ==========================================
    # LINHAS
    # ==========================================
    for coluna, label, cor in series:

        ax.plot(
            x,
            resultado[coluna],

            marker="o",
            linewidth=2,
            markersize=8,

            label=label,
            color=cor
        )

        # valores nos pontos
        for i, v in enumerate(resultado[coluna]):

            ax.text(
                i,
                v,
                str(v),

                ha="center",
                va="bottom",

                fontsize=8
            )
    # ==========================================
    # CONFIGURAÇÕES
    # ==========================================
    ax.set_xticks(list(x))

    ax.set_xticklabels(
        resultado["label"],
        rotation=45
    )

    ax.set_ylabel(ylabel)

    ax.set_title(titulo)

    ax.legend()

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.5
    )

    plt.tight_layout()

    plt.show()


def analise_metrica_temporal(
    dados: pd.DataFrame,
    coluna: str,
    titulo: str,
    ylabel: str
):

    resultado = (
        dados[dados["pessoa"].isin(["Menina", "Menino"])]
        .groupby(["coleta_dia", "pessoa"])[coluna]
        .mean()
        .unstack()
        .sort_index()
    )

    fig, ax = plt.subplots(figsize=(14, 5))

    cores = {
        "Menino": "blue",
        "Menina": "orange"
    }

    # ==========================
    # NOVOS LABELS
    # ==========================
    x = range(len(resultado))

    labels = [
        f"Dia {i+1}"
        for i in range(len(resultado))
    ]

    for pessoa in resultado.columns:

        ax.plot(
            x,
            resultado[pessoa],
            marker="o",
            label=pessoa,
            color=cores.get(pessoa)
        )

        for i, y in enumerate(resultado[pessoa]):

            if pd.notna(y):

                ax.text(
                    i,
                    y,
                    f"{y:.0f}",
                    ha="center",
                    va="bottom",
                    fontsize=8
                )

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=45)

    ax.set_xlabel("Coletas")
    ax.set_ylabel(ylabel)

    ax.set_title(titulo)

    ax.legend()

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.5
    )

    plt.tight_layout()
    plt.show()


def analise_por_dia(dados: pd.DataFrame):

    analise_intersecao(
        dados,
        "coleta_dia",
        "video_id",
        "Comparação de vídeos por dia — Menino vs Menina",
        "Quantidade de vídeos"
    )


def analise_por_coleta(dados: pd.DataFrame):

    analise_intersecao(
        dados,
        "coleta_hora",
        "video_id",
        "Comparação de vídeos por coleta — Menino vs Menina",
        "Quantidade de vídeos"
    )


def analise_made_for_kids(dados: pd.DataFrame):

    dados = dados.drop_duplicates(
        subset=['video_id', 'pessoa']
    )

    resultado = (
        dados
        .groupby(["pessoa", "made_for_kids"])["video_id"]
        .nunique()
        .unstack(fill_value=0)
    )

    print(resultado)

    resultado.plot(kind="bar")

    plt.title("Vídeos para crianças vs não para crianças")
    plt.xlabel("Pessoa")
    plt.ylabel("Quantidade de vídeos")

    plt.legend(
        [str(col) for col in resultado.columns]
    )

    plt.xticks(rotation=0)

    plt.show()


def analise_tempo_por_video(dados: pd.DataFrame):

    dados = dados.drop_duplicates(
        subset=['video_id', 'pessoa']
    )

    resultado = (
        dados
        .groupby("pessoa")["duration_seconds"]
        .agg(
            media="mean",
            desvio_padrao="std",
            mediana="median"
        )
        .reset_index()
    )

    print(resultado)

    pessoas = resultado["pessoa"].tolist()
    medias = resultado["media"].tolist()
    desvios = resultado["desvio_padrao"].tolist()
    medianas = resultado["mediana"].tolist()

    cores = {"Menino": "#378ADD", "Menina": "#D85A30"}
    cores_borda = {"Menino": "#0C447C", "Menina": "#993C1D"}

    fig, ax = plt.subplots(figsize=(8, 3))  

    x = range(len(pessoas))
    largura = 0.45

    # ── Barras (alpha separado, não no hex) ─────────────────────
    for i, pessoa in enumerate(pessoas):
        ax.bar(
            i,
            medias[i],
            width=largura,
            color=cores.get(pessoa, "gray"),
            edgecolor=cores_borda.get(pessoa, "gray"),
            linewidth=1.5,
            alpha=0.7,
            zorder=3
        )

    # ── Barras de erro (desvio padrão) — uma por vez ─────────────
    for i, pessoa in enumerate(pessoas):
        ax.errorbar(
            i,
            medias[i],
            yerr=desvios[i],
            fmt="none",
            ecolor=cores_borda.get(pessoa, "gray"),
            elinewidth=2,
            capsize=10,
            capthick=2,
            zorder=4
        )

    # ── Linha de mediana ─────────────────────────────────────────
    for i, med in enumerate(medianas):
        ax.hlines(
            med,
            i - largura / 2,
            i + largura / 2,
            colors="black",
            linewidths=2.5,
            linestyles="dashed",
            label="Mediana" if i == 0 else "",
            zorder=5
        )

    # ── Rótulos ──────────────────────────────────────────────────
    for i, (pessoa, media, desvio, med) in enumerate(
        zip(pessoas, medias, desvios, medianas)
    ):
        ax.text(
            i,
            media + desvio + 5,
            f"μ={media:.0f}s\n±{desvio:.0f}s",
            ha="center",
            va="bottom",
            fontsize=11,
            color=cores_borda.get(pessoa, "gray")
        )
        ax.text(
            i + largura / 2 + 0.03,
            med,
            f"med={med:.0f}s",
            ha="left",
            va="center",
            fontsize=11,
            color="black",
            style="italic"
        )

    # ── Configurações ────────────────────────────────────────────
    ax.set_xticks(list(x))
    ax.set_xticklabels(pessoas, fontsize=12)
    ax.set_ylabel("Duração (segundos)")
    ax.set_title(
    "Duração dos vídeos — média, desvio padrão e mediana",
    pad=35  # espaço entre o título e o gráfico
    )

    ax.legend(
        handles=[
            plt.Rectangle((0, 0), 1, 1, color="gray", alpha=0.7, label="Média"),
            plt.Line2D([0], [0], color="black", lw=2.5, linestyle="dashed", label="Mediana"),
            plt.Line2D([0], [0], color="gray", lw=2, label="Desvio padrão"),
        ],
        loc="upper right",
        fontsize=11
    )

    ax.grid(axis="y", linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.show()


def analise_tipo_conteudo(dados: pd.DataFrame):

    dados = dados.drop_duplicates(subset=['video_id', 'pessoa'])

    res = (
        dados
        .groupby('pessoa')['category_name']
        .value_counts()
        .reset_index(name='quantidade')
    )

    pessoas = res['pessoa'].unique()

    fig, axes = plt.subplots(
        1,
        len(pessoas),
        figsize=(18, 6),   # mais largo
        sharey=True
    )

    for ax, pessoa in zip(axes, pessoas):
        dados_pessoa = res[res['pessoa'] == pessoa]

        x = range(len(dados_pessoa))

        ax.bar(
            x,
            dados_pessoa['quantidade'],
            width=0.6          # barras mais finas = mais espaço entre elas
        )

        ax.set_title(pessoa)
        ax.set_xlabel('Categoria')
        ax.set_xticks(x)
        ax.set_xticklabels(
            dados_pessoa['category_name'],
            rotation=90,       # vertical elimina sobreposição
            ha='center',
            fontsize=25
        )

    axes[0].set_ylabel('Quantidade')

    plt.tight_layout()         # evita cortar labels
    plt.show()


def analise_canais_exibidos(dados: pd.DataFrame):

    analise_intersecao(
        dados,
        "coleta_dia",
        "channel_id",
        "Comparação de canais por dia — Menino vs Menina",
        "Quantidade de canais"
    )


def analise_media_views(dados: pd.DataFrame):

    analise_metrica_temporal(
        dados,
        "view_count",
        "Média de visualizações ao longo do tempo",
        "Visualizações (média)"
    )


def analise_media_likes(dados: pd.DataFrame):

    analise_metrica_temporal(
        dados,
        "like_count",
        "Média de likes ao longo do tempo",
        "Likes (média)"
    )


def analise_media_comentarios(dados: pd.DataFrame):

    analise_metrica_temporal(
        dados,
        "comment_count",
        "Média de comentários ao longo do tempo",
        "Comentários (média)"
    )


def analise_linguas(dados: pd.DataFrame, top_n: int = 10):

    dados = dados.drop_duplicates(subset=['video_id', 'pessoa'])

    res = (
        dados
        .groupby(['pessoa', 'language'])
        .size()
        .reset_index(name='quantidade')
    )

    # Top N idiomas globais (união dos mais frequentes de ambos os grupos)
    top_linguas = (
        res.groupby('language')['quantidade']
        .sum()
        .nlargest(top_n)
        .index
    )

    res_filtrado = res[res['language'].isin(top_linguas)]

    # Pivot para barras agrupadas
    pivot = (
        res_filtrado
        .pivot(index='language', columns='pessoa', values='quantidade')
        .fillna(0)
        .sort_values(res_filtrado['pessoa'].iloc[0], ascending=False)
    )

    ax = pivot.plot(
        kind='bar',
        figsize=(12, 5),
        width=0.7
    )

    ax.set_title(f'Top {top_n} idiomas por pessoa')
    ax.set_xlabel('Idioma')
    ax.set_ylabel('Quantidade')
    ax.tick_params(axis='x', rotation=45)
    ax.legend(title='Pessoa')

    plt.tight_layout()
    plt.show()


def nuvem_palavras(dados: pd.DataFrame):

    dados = dados.drop_duplicates(subset=['video_id', 'pessoa'])

    stopwords = set(nltk_stopwords.words('portuguese'))
    stopwords.update(nltk_stopwords.words('english'))

    stopwords.update([
        "a","o","as","os","um","uma","uns","umas",
        "de","da","do","das","dos",
        "em","no","na","nos","nas",
        "para","pra","pro","por","com","sem",
        "youtube","vídeo","video","shorts","não",
        "www","https","http"
    ])

    Menina = dados[dados["pessoa"] == "Menina"]
    Menino = dados[dados["pessoa"] == "Menino"]

    texto_Menina = " ".join(Menina["description"].dropna().astype(str))
    texto_Menino = " ".join(Menino["description"].dropna().astype(str))

    tabela_menina = contar_palavras(texto_Menina, stopwords)
    tabela_menino = contar_palavras(texto_Menino, stopwords)

    display(tabela_menina)
    display(tabela_menino)

    plt.imshow(
        WordCloud(
            background_color="white",
            stopwords=stopwords,
        ).generate(texto_Menina)
    )

    plt.title("Menina")
    plt.axis("off")
    plt.show()

    plt.imshow(
        WordCloud(
            background_color="white",
            stopwords=stopwords
        ).generate(texto_Menino)
    )

    plt.title("Menino")
    plt.axis("off")
    plt.show()

def listar_categoria_descricao(dados: pd.DataFrame):

    dados = dados.drop_duplicates(
        subset=["video_id", "pessoa"]
    )

    linhas = []

    for i, row in enumerate(dados.itertuples(), start=1):

        categoria = row.category_name
        descricao = str(row.description)

        linhas.append(
            f"video{i}: category_name: {categoria} description: {descricao}"
        )

    return linhas

def analise_por_coleta_acumulada(dados: pd.DataFrame):

    analise_intersecao_acumulada(
        dados,
        "coleta_hora",
        "video_id",
        "Comparação acumulada de vídeos por coleta",
        "Quantidade acumulada de vídeos"
    )


def analise_por_dia_acumulada(dados: pd.DataFrame):

    analise_intersecao_acumulada(
        dados,
        "coleta_dia",
        "video_id",
        "Comparação acumulada de vídeos por dia",
        "Quantidade acumulada de vídeos"
    )

def main():

    print("Lendo dados...")

    arq = "../../../../Analise_Coletas/Coletas/todos_videos_p9.csv"

    df = carregar_dados(arq)

    df["coleta_dia"] = pd.to_datetime(
        df["coleta"].str[7:15],
        format="%Y%m%d"
    )

    df["coleta_hora"] = df["coleta"].str[7:17]  # "YYYYMMDD_HH"  <-- aqui

    df.columns = df.columns.str.replace(
        "madeForKids",
        "made_for_kids"
    )

    analise_por_coleta(df)

    analise_por_dia(df)

    analise_por_coleta_acumulada(df)

    analise_por_dia_acumulada(df)

    analise_made_for_kids(df)

    analise_tempo_por_video(df)

    analise_tipo_conteudo(df)

    analise_canais_exibidos(df)

    analise_media_views(df)

    analise_media_likes(df)

    analise_media_comentarios(df)

    nuvem_palavras(df)

    analise_linguas(df)

    #lista = listar_categoria_descricao(df)

    #for linha in lista[:5]:
        #print(linha)


if __name__ == "__main__":
    main()