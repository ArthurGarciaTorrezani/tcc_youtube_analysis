# %%
import pandas as pd
import matplotlib.pyplot as plt
from carregar_dados import carregar_dados
import matplotlib.dates as mdates
from wordcloud import WordCloud, ImageColorGenerator, STOPWORDS

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
                coletas.get("Carlos", [set()]*len(coletas)),
                coletas.get("Maria", [set()]*len(coletas))
            )
        ],
        "so_carlos": [
            len(c - m)
            for c, m in zip(
                coletas.get("Carlos", [set()]*len(coletas)),
                coletas.get("Maria", [set()]*len(coletas))
            )
        ],
        "so_maria": [
            len(m - c)
            for c, m in zip(
                coletas.get("Carlos", [set()]*len(coletas)),
                coletas.get("Maria", [set()]*len(coletas))
            )
        ],
    }).sort_values(coluna_grupo)

    print(resultado)

    resultado["label"] = resultado[coluna_grupo]

    fig, ax = plt.subplots(figsize=(14, 5))
    x = range(len(resultado))

    series = [
        ("em_comum",  "Em comum", "green"),
        ("so_carlos", "Só no Carlos", "blue"),
        ("so_maria",  "Só na Maria", "orange"),
    ]

    offsets = {"em_comum": -0.03, "so_carlos": -0.03, "so_maria": 0.05}

    for coluna, label, cor in series:
        x_offset = [i + offsets[coluna] for i in x]
        ax.scatter(x_offset, resultado[coluna], label=label, color=cor, s=80)

        for i, v in enumerate(resultado[coluna]):
            ax.text(i, v, str(v), ha="center", va="bottom", fontsize=8)

    ax.set_xticks(list(x))
    ax.set_xticklabels(resultado["label"], rotation=45)
    ax.set_ylabel(ylabel)
    ax.set_title(titulo)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.show()


def analise_metrica_temporal(dados: pd.DataFrame, coluna: str, titulo: str, ylabel: str):

    resultado = (
        dados[dados["pessoa"].isin(["Maria", "Carlos"])]
        .groupby(["coleta_dia", "pessoa"])[coluna]
        .mean()
        .unstack()
        .sort_index()
    )

    fig, ax = plt.subplots(figsize=(14, 5))

    cores = {"Carlos": "blue", "Maria": "orange"}
    for pessoa in resultado.columns:
        ax.plot(resultado.index, resultado[pessoa], marker="o", label=pessoa, color=cores.get(pessoa))
        for x, y in zip(resultado.index, resultado[pessoa]):
            if pd.notna(y):
                ax.text(x, y, f"{y:.0f}", ha="center", va="bottom", fontsize=8)

    ax.set_xlabel("Data")
    ax.set_ylabel(ylabel)
    ax.set_title(titulo)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def analise_por_dia(dados: pd.DataFrame):
    analise_intersecao(
        dados,
        "coleta_dia",
        "video_id",
        "Comparação de vídeos por dia — Carlos vs Maria",
        "Quantidade de vídeos"
    )


def analise_por_coleta(dados: pd.DataFrame):    
    analise_intersecao(
    dados,
    "coleta",
    "video_id",
    "Comparação de vídeos por coleta — Carlos vs Maria",
    "Quantidade de vídeos"
    )


def analise_made_for_kids(dados: pd.DataFrame):
    dados = dados.drop_duplicates(subset=['video_id', 'pessoa'])

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
    plt.legend([str(col) for col in resultado.columns])  # usa os valores reais True/False
    plt.xticks(rotation=0)
    plt.show()


def analise_tempo_por_video(dados: pd.DataFrame):
    dados = dados.drop_duplicates(subset=['video_id', 'pessoa'])

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

    plt.errorbar(
    x=resultado["pessoa"],           
    y=resultado["media"],            
    yerr=resultado["desvio_padrao"], 
    fmt="o",                         
    capsize=5,                       
    label="Média + desvio padão"
    )

    plt.scatter(resultado["pessoa"],resultado["mediana"],marker='s',label='Mediana',c='red')

    plt.legend()
    plt.show()


def analise_tipo_conteudo(dados: pd.DataFrame):

    dados = dados.drop_duplicates(subset=['video_id', 'pessoa'])

    res = dados.groupby('pessoa')['category_name'].value_counts().reset_index(name='quantidade')
    print(res)

    pessoas = res['pessoa'].unique()
    fig, axes = plt.subplots(1, len(pessoas), figsize=(12, 5), sharey=True)
    
    for ax, pessoa in zip(axes, pessoas):
        dados_pessoa = res[res['pessoa'] == pessoa]
        ax.bar(dados_pessoa['category_name'], dados_pessoa['quantidade'])
        ax.set_title(pessoa)
        ax.set_xlabel('Categoria')
        ax.tick_params(axis='x', rotation=45)

    axes[0].set_ylabel('Quantidade')
    plt.show()
    

def analise_canais_exibidos(dados: pd.DataFrame):
   analise_intersecao(
    dados,
    "coleta_dia",
    "channel_id",
    "Comparação de canais por dia — Carlos vs Maria",
    "Quantidade de canais"
    )


def analise_media_views(dados: pd.DataFrame):
    analise_metrica_temporal(dados, "view_count", "Média de visualizações ao longo do tempo", "Visualizações (média)")


def analise_media_likes(dados: pd.DataFrame):
    analise_metrica_temporal(dados, "like_count", "Média de likes ao longo do tempo", "Likes (média)")


def analise_media_comentarios(dados: pd.DataFrame):
    analise_metrica_temporal(dados, "comment_count", "Média de comentários ao longo do tempo", "Comentários (média)")


def analise_linguas(dados: pd.DataFrame):

    dados = dados.drop_duplicates(subset=['video_id', 'pessoa'])

    res = dados.groupby(['pessoa','language'])['language'].value_counts().reset_index(name='quantidade')
    print(res)

    pessoas = res['pessoa'].unique()
    fig, axes = plt.subplots(1, len(pessoas), figsize=(12, 5), sharey=True)
    
    for ax, pessoa in zip(axes, pessoas):
        dados_pessoa = res[res['pessoa'] == pessoa]
        ax.bar(dados_pessoa['language'], dados_pessoa['quantidade'])
        ax.set_title(pessoa)
        ax.set_xlabel('Categoria')
        ax.tick_params(axis='x', rotation=45)

    axes[0].set_ylabel('Quantidade')
    plt.show()


def nuvem_palavras(dados: pd.DataFrame):
    dados = dados.drop_duplicates(subset=['video_id', 'pessoa'])

    stopwords = set(STOPWORDS)    
    stopwords.update([
    # artigos / preposições
    "a","o","as","os","um","uma","uns","umas",
    "de","da","do","das","dos",
    "em","no","na","nos","nas",
    "para","pra","pro","por","com","sem",
    "ao","aos","à","às",

    # pronomes
    "eu","tu","ele","ela","nós","nos","vos","eles","elas",
    "me","te","se","nos","vos",
    "meu","minha","meus","minhas",
    "seu","sua","seus","suas",

    # conectivos
    "e","ou","mas","porque","porquê","por","que",
    "como","quando","onde","isso","isso","essa","esse",
    "isso","isto","aquilo",

    # verbos comuns
    "é","ser","foi","era","são","tá","ta","to","tô",
    "vai","vou","ir","tem","tenho","teve","tinha",
    "faz","fazer","feito","fazendo",

    # inglês comum
    "the","and","or","of","to","in","on","for",
    "is","are","was","were","be","been",
    "this","that","these","those",
    "with","from","by","about",

    # lixo de texto
    "http","https","www","com","br",
    "00","01","02","03","1","2","3"
])

    maria  = dados[dados["pessoa"] == "Maria"]
    carlos = dados[dados["pessoa"] == "Carlos"]

    texto_maria = " ".join(maria["description"].dropna().astype(str))
    texto_carlos = " ".join(carlos["description"].dropna().astype(str))

    plt.imshow(WordCloud(background_color="white",  stopwords=stopwords,).generate(texto_maria))
    plt.title("Maria")
    plt.axis("off")
    plt.show()

    plt.imshow(WordCloud(background_color="white",stopwords=stopwords).generate(texto_carlos))
    plt.title("Carlos")
    plt.axis("off")
    plt.show()
    

def main():
    print("Lendo dados...")
    
    arquivo = "../../dados/videos_mock_50.csv"
    arq = "../../../../Analise_Coletas/Coletas/todos_videos_p2.csv"

    df = carregar_dados(arq)

    df["coleta_dia"] = pd.to_datetime(df["coleta"].str[7:15], format="%Y%m%d")
    df.columns = df.columns.str.replace("madeForKids", "made_for_kids")
    
    #print(df["coleta_dia"])    

    analise_por_coleta(df)
    analise_por_dia(df)
    analise_made_for_kids(df)
    analise_tempo_por_video(df)
    #analise_tipo_conteudo(df)
    analise_canais_exibidos(df)
    analise_media_views(df)
    analise_media_likes(df)
    analise_media_comentarios(df)
    nuvem_palavras(df)
    analise_linguas(df)
    
if __name__ == "__main__":
    main()