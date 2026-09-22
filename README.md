# CasaSul

Um motor de busca de imóveis em tempo real que traduz os critérios do usuário para os sistemas de dezenas de imobiliárias diferentes, normaliza os dados e apresenta resultados unificados com filtragem programática garantida.

---

## 🚀 Propósito do Projeto

Este projeto é um **buscador ativo em tempo real**. Ao realizar uma busca, o sistema:

- **Roteia a busca:** Traduz filtros globais (cidade, faixa de preço, número de quartos, banheiros, etc.) em parâmetros específicos de cada site ou API alvo.
- **Executa em paralelo:** Consulta dezenas de imobiliárias simultaneamente via `ThreadPoolExecutor` para retorno rápido.
- **Garante a lógica:** Aplica filtragem programática rigorosa (ex: assegura que "2 quartos" retorne resultados $\ge$ 2, mesmo que o site original use busca exata ou inconsistente).
- **Unifica a experiência:** Apresenta uma interface limpa e responsiva utilizando **Django + HTMX**, com atualizações parciais de tela e *caching* inteligente via **Redis**.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.12, Django 5.2
- **Gerenciador de Pacotes:** [uv](https://github.com/astral-sh/uv)
- **Frontend & Reatividade:** Django Templates, HTMX, Tailwind CSS
- **Autenticação:** Django Allauth
- **Banco de Dados & Cache:** SQLite (desenvolvimento) / PostgreSQL 16 (produção), Redis 7 (`django-redis`)
- **Scraping & Automação:** BeautifulSoup4, Requests, Playwright
- **Servidor & Deploy:** Gunicorn, WhiteNoise, Docker, Docker Compose, Traefik Reverse Proxy

---

## 🏗️ Arquitetura de Busca

### Fluxo de Dados On-Demand

```mermaid
flowchart TD
    UI[Entrada do Usuário / Django View] --> SearchQuery[SearchQuery (Objeto de Critérios)]
    SearchQuery --> CacheCheck{Cache Redis}
    CacheCheck -- Hit --> UI
    CacheCheck -- Miss --> Aggregator[Aggregator (ThreadPoolExecutor)]
    Aggregator --> Scrapers[Scrapers (HTML/JSON Real-time)]
    Scrapers --> PostFilter[Filtro Local de Segurança]
    PostFilter --> CacheSave[Salva Cache Redis]
    CacheSave --> UI
```

---

## 📁 Estrutura do Projeto

```text
.
├── apps/
│   ├── accounts/          # Autenticação e gestão de usuários (Django Allauth)
│   └── search/            # View principal, formulários, rotas HTMX e registro de scrapers
├── config/
│   └── settings.py        # Configuração central dos scrapers (URLs, timeouts, limites)
├── docs/                  # Guias de arquitetura, refatoração e documentação interna
├── domain/
│   ├── models.py          # Dataclasses de domínio (Property, SearchQuery)
│   └── parsing_utils.py   # Utilitários de sanitização e extração de dados
├── infrastructure/
│   ├── browser_client.py  # Automação via Playwright para sites com JS
│   └── http_client.py     # Cliente HTTP resiliente para requisições diretas
├── scrapers/              # Motor de drivers de scraping por imobiliária
│   ├── base.py            # Classe abstrata AgencyScraper
│   ├── imogestao_base.py  # Classe base para imobiliárias no sistema ImoGestão
│   ├── tecimob_base.py    # Classe base para imobiliárias no sistema TecImob
│   └── [drivers].py       # Implementações específicas (ex: chavesnamao, keyonimoveis, etc.)
├── services/
│   └── aggregator.py      # Orquestrador paralelo de buscas e filtro local
├── templates/             # Templates HTML (base.html, search/index.html, partials HTMX)
├── tests/
│   └── test_scrapers_health.py # Script de verificação de integridade dos scrapers
├── webapp/                # Configuração do projeto Django (settings, urls, wsgi)
├── docker-compose.yml     # Orquestração de contêineres (App, Postgres, Redis)
├── Dockerfile             # Containerização otimizada com uv
├── pyproject.toml         # Dependências do projeto
└── manage.py              # Script CLI do Django
```

---

## 💡 Conceitos Chave

### Modelos de Dados (Contratos de Domínio)

O sistema é guiado por modelos imutáveis e tipados em `domain/models.py`:

1. **`SearchQuery`**: Critérios desejados pelo usuário (Preço mín/máx, Quartos $\ge$ X, Banheiros $\ge$ X, Área mín/máx, Cidade, Bairro).
2. **`Property`**: Estrutura de dados normalizada unificada (Título, Preço, Cidade, Quartos, Vagas, URL, Agência, Imagens).

### Estratégia de Filtragem ($\ge$)

Para resolver divergências na busca de diferentes sites:
- **Filtro Remoto:** O scraper tenta aplicar os parâmetros na URL/payload original para reduzir tráfego.
- **Filtro Local (Segurança):** O `Aggregator` (`services/aggregator.py`) valida novamente cada imóvel programaticamente, garantindo stritamente os mínimos solicitados.

### Registrador de Scrapers (`registry.py`)

Todos os scrapers ativos estão centralizados no mapa `SCRAPER_REGISTRY` em `apps/search/registry.py`. Adicionar uma nova imobiliária requer apenas implementar a subclasse em `scrapers/` e registrar seu identificador.

---

## 💻 Desenvolvimento Local

### 1. Pré-requisitos
- Python 3.12+
- Gerenciador de pacotes [uv](https://docs.astral.sh/uv/)

### 2. Instalação de Dependências
```bash
uv sync
```

### 3. Migrações e Banco de Dados
```bash
uv run python manage.py migrate
```

### 4. Executar o Servidor de Desenvolvimento
```bash
uv run python manage.py runserver
```
Acesse `http://127.0.0.1:8000` no navegador.

### 5. Executar Verificação de Saúde dos Scrapers (Health Check)
Para testar a saúde e resposta de todos os scrapers registrados de forma isolada:
```bash
uv run python tests/test_scrapers_health.py
```

---

## 🐳 Executando com Docker

O projeto possui suporte completo a Docker Compose com PostgreSQL, Redis e proxy reverso Traefik.

### Subir os serviços:
```bash
docker compose up -d --build
```

---

## 🎯 Filosofia de Código

- **Desacoplamento:** Cada scraper é isolado e autônomo. Falhas em um site não interrompem a busca global.
- **Transparência e Resiliência:** Log detalhado e tratamentos de exceção evitam que timeouts de terceiros travem a requisição do usuário.
- **Desempenho Primário:** Caching inteligente no Redis evita consultas repetidas a sites externos para pesquisas idênticas.

