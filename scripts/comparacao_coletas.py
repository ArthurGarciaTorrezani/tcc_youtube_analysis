import csv
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, asdict


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


@dataclass
class VideoDuplicado:
    video_id: str
    titulo: str
    url: str
    canal: str
    published_at: str
    aparece_em: list


def extrair_numero_video(nome_dir):
    try:
        return int(nome_dir.split("_")[1])
    except:
        return 0


def extrair_data_hora(nome_coleta):
    try:
        partes = nome_coleta.split("_")
        data_raw = partes[1]
        hora_raw = partes[2]

        data = f"{data_raw[:4]}-{data_raw[4:6]}-{data_raw[6:]}"
        hora = f"{hora_raw[:2]}:{hora_raw[2:4]}:{hora_raw[4:]}"

        return data, hora
    except:
        return "desconhecida", "desconhecida"


def detectar_encoding(csv_path):
    for enc in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            with open(csv_path, encoding=enc) as f:
                f.read(1)
            return enc
        except:
            continue
    return "utf-8"


def carregar_videos(pasta_raiz):
    pasta_raiz = Path(pasta_raiz)
    videos = defaultdict(lambda: defaultdict(list))

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
                    reader = csv.DictReader(f)

                    for row in reader:
                        video_id = row.get("video_id", "").strip()
                        if not video_id:
                            continue

                        videos[pessoa][video_id].append(
                            VideoOcorrencia(
                                video_id=video_id,
                                pessoa=pessoa,
                                coleta=coleta,
                                data_coleta=data,
                                hora_coleta=hora,
                                numero_video=extrair_numero_video(video_dir.name),
                                video_dir=video_dir.name,
                                published_at=row.get("published_at", "").strip(),
                                csv_path=str(csv_path),
                                titulo=row.get("title", "").strip(),
                                canal=row.get("channel_title", "").strip(),
                                url=row.get("url", "").strip(),
                            )
                        )

    return videos


def remover_duplicatas(ocorrencias):
    seen = set()
    unicas = []

    for oc in ocorrencias:
        chave = (oc.pessoa, oc.coleta, oc.video_dir)
        if chave not in seen:
            seen.add(chave)
            unicas.append(oc)

    return unicas


def analisar(videos_por_pessoa):
    mapa_global = defaultdict(list)

    for pessoa, videos in videos_por_pessoa.items():
        for video_id, ocorrencias in videos.items():
            mapa_global[video_id].extend(ocorrencias)

    duplicados_unicos = []
    duplicados_entre_pessoas = []
    duplicados_mesma_pessoa = []
    duplicados_mesma_coleta = []

    for video_id, ocorrencias in mapa_global.items():
        if len(ocorrencias) <= 1:
            continue

        ocorrencias = remover_duplicatas(ocorrencias)
        primeiro = ocorrencias[0]

        pessoas_distintas = set(oc.pessoa for oc in ocorrencias)
        coletas_distintas = set((oc.pessoa, oc.coleta) for oc in ocorrencias)
        mesma_coleta_map = defaultdict(list)

        for oc in ocorrencias:
            mesma_coleta_map[(oc.pessoa, oc.coleta)].append(oc)

        # lista base (únicos)
        duplicado_obj = VideoDuplicado(
            video_id=video_id,
            titulo=primeiro.titulo,
            url=primeiro.url,
            canal=primeiro.canal,
            published_at=primeiro.published_at,
            aparece_em=ocorrencias
        )

        duplicados_unicos.append(duplicado_obj)

        # entre pessoas
        if len(pessoas_distintas) > 1:
            duplicados_entre_pessoas.append(duplicado_obj)

        # mesma pessoa em coletas diferentes
        if len(coletas_distintas) > 1:
            duplicados_mesma_pessoa.append(duplicado_obj)

        # mesma coleta
        for _, lista in mesma_coleta_map.items():
            if len(lista) > 1:
                duplicados_mesma_coleta.append(duplicado_obj)
                break

    return {
        "unicos": duplicados_unicos,
        "entre_pessoas": duplicados_entre_pessoas,
        "mesma_pessoa": duplicados_mesma_pessoa,
        "mesma_coleta": duplicados_mesma_coleta
    }


def main():
    pasta = "../Analise_Coletas/Coletas"

    print("Lendo dados...")
    dados = carregar_videos(pasta)

    total_csvs = 0
    total_unicos_set = set()

    for pessoa, videos in dados.items():
        for video_id, ocorrencias in videos.items():
            total_unicos_set.add(video_id)
            total_csvs += len(ocorrencias)

    total_unicos = len(total_unicos_set)

    print("Analisando duplicados...")
    resultado_analise = analisar(dados)

    total_duplicados_unicos = len(resultado_analise['unicos'])
    nao_duplicados = total_unicos - total_duplicados_unicos

    print(f"\nTotal de arquivos video.csv lidos: {total_csvs}")
    print(f"Total de vídeos únicos: {total_unicos}")
    print(f"Não duplicados: {nao_duplicados}")

    print(f"\nDuplicados únicos: {total_duplicados_unicos}")
    print(f"Entre pessoas: {len(resultado_analise['entre_pessoas'])}")
    print(f"Mesma pessoa (coletas diferentes): {len(resultado_analise['mesma_pessoa'])}")
    print(f"Mesma coleta: {len(resultado_analise['mesma_coleta'])}")

    resultado = {
        "gerado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "totais": {
            "csvs_lidos": total_csvs,
            "videos_unicos": total_unicos,
            "nao_duplicados": nao_duplicados,
            "duplicados_unicos": total_duplicados_unicos,
            "entre_pessoas": len(resultado_analise['entre_pessoas']),
            "mesma_pessoa": len(resultado_analise['mesma_pessoa']),
            "mesma_coleta": len(resultado_analise['mesma_coleta'])
        },
        "dados": {
            "unicos": [asdict(d) for d in resultado_analise['unicos']],
            "entre_pessoas": [asdict(d) for d in resultado_analise['entre_pessoas']],
            "mesma_pessoa": [asdict(d) for d in resultado_analise['mesma_pessoa']],
            "mesma_coleta": [asdict(d) for d in resultado_analise['mesma_coleta']]
        }
    }

    with open("../Analise_Coletas/Coletas/resultado.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    print("\nResultado salvo em resultado.json")


if __name__ == "__main__":
    main()
