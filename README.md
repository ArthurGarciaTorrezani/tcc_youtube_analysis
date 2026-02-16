# tcc_youtube_analysis
Beginning of collect and analysis about some data youtube videos about inadequate content for kids


# YouTube Scraper

Ferramenta para coletar dados de vídeos do YouTube (shorts), incluindo informações, comentários e transcrições.

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o arquivo `.env`:
```env
API_SERVICE_NAME=youtube
API_VERSION=v3
API_KEY=sua_chave_api_aqui
BASE_ROUTE=https://www.youtube.com/shorts/VIDEO_ID
```

4. Obtenha uma chave de API do YouTube:
   - Acesse: https://console.cloud.google.com/
   - Crie um projeto
   - Ative a YouTube Data API v3
   - Crie credenciais (API Key)

## Uso

Execute o script principal:
```bash
python main.py
```

## Estrutura de Dados Gerados
```
dados/
└── coleta_YYYYMMDD_HHMMSS/
    ├── video_1_VIDEO_ID/
    │   ├── dados.json          # JSON completo
    │   ├── dados.txt           # Texto formatado
    │   ├── video.csv           # Informações do vídeo
    │   ├── comentarios.csv     # Comentários
    │   ├── transcricao.txt     # Transcrição
    │   └── video.mp4           # Vídeo baixado
    └── video_2_VIDEO_ID/
        └── ...
```

## Funcionalidades

- Coleta de informações do vídeo (título, descrição, estatísticas)
- Extração de comentários
- Download de transcrições
- Download do vídeo
- Salvamento em múltiplos formatos (JSON, CSV, TXT)
- Organização automática em pastas

## Requisitos

- Python 3.8+
- Google Chrome
- ChromeDriver
- Chave de API do YouTube Data API v3