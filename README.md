# 🏠 Agregador de Imóveis (Web Scraper com Pipelines)

Este projeto é uma ferramenta de automação e monitorização de imóveis desenvolvida em Python. O sistema centraliza resultados de múltiplas fontes (imobiliárias) numa interface única, normalizando dados e permitindo exportação para análise.

A arquitetura foi modernizada para utilizar **Pipelines de Processamento**, facilitando a escalabilidade e a adição de novos sites.

## 🚀 Funcionalidades

-   **Multi-site:** Suporte a múltiplas imobiliárias (atualmente configurado para *KeyOn* e *QualAlugar*).
-   **Arquitetura Híbrida:**
    -   *HTML Parsing:* Extração via seletores CSS (ex: KeyOn).
    -   *JSON Extraction:* Extração de dados ocultos em tags `<script>` (ex: QualAlugar).
-   **Sistema de Caching Inteligente:** Evita pedidos repetidos à rede guardando o HTML localmente (hash MD5 da URL), ideal para desenvolvimento e testes.
-   **Interface Web:** Painel construído com **Streamlit** para visualização rápida e links diretos.
-   **Suporte a JavaScript:** Utiliza **Selenium** (headless) para carregar sites dinâmicos.
-   **Exportação:** Gera relatórios em CSV e Excel.

## 🛠️ Arquitetura e Tecnologias

O projeto segue princípios de **Clean Architecture** e **Design Patterns**:

-   **Linguagem:** Python 3.x
-   **Bibliotecas Principais:** `pandas`, `beautifulsoup4`, `selenium`, `streamlit`.
-   **Padrões de Projeto Implementados:**
    -   **Pipeline Pattern:** O fluxo de extração é dividido em passos (`FetchStep`, `ParseStep`, `LogStep`), geridos por um `ScraperManager`.
    -   **Factory Method:** A `ScraperFactory` cria instâncias e regista novas estratégias de extração dinamicamente.
    -   **Adapter Pattern:** O `PipelineScraperAdapter` permite que qualquer configuração de pipeline seja tratada como um Scraper padrão.
    -   **Repository Pattern:** Abstração da persistência dos dados (`ImovelRepository`).

### Estrutura de Pastas

```text
imobiliarias/
├── app.py                      # Interface Web (Streamlit)
├── main.py                     # Entry point (CLI / Orquestrador)
├── cache_data/                 # Armazenamento de HTMLs em cache
├── config/                     # Configurações (URLs, Features flags)
├── domain/                     # Modelos (Imovel, ScraperResult)
├── factories/                  # Criação e registo de Scrapers
├── infrastructure/             # Clientes HTTP/Selenium
├── interfaces/                 # Contratos (Protocolos/ABCs)
├── parsers/                    # Lógica de extração (BeautifulSoup)
├── pipeline_steps/             # Passos reutilizáveis (Caching, Fetch, Parse)
├── repositories/               # Gestão de dados em memória/exportação
├── scrapers/                   # Adaptadores e lógica específica
└── services/                   # Casos de uso e Logger

```

## 📦 Instalação

1. **Clone o repositório:**
```bash
git clone <url-do-repositorio>
cd imobiliarias

```


2. **Crie o ambiente virtual:**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

```


3. **Instale as dependências:**
```bash
pip install pandas beautifulsoup4 selenium webdriver-manager streamlit openpyxl

```


*(Nota: O Selenium fará a gestão automática do driver do Chrome).*

## ▶️ Como Usar

### 1. Interface Web (Recomendado)

Para uma experiência visual e interativa:

```bash
streamlit run imobiliarias/app.py

```

Clique em **"🚀 Executar Monitorização"** para iniciar a recolha de dados.

### 2. Terminal (CLI)

Para execução direta ou agendamento (cron jobs):

```bash
python imobiliarias/main.py

```

## ⚙️ Configuração

As URLs de pesquisa e a ativação de cada imobiliária são geridas em `config/settings.py`.

```python
SCRAPERS = {
    'keyon': ScraperConfig(
        name='KeyOn',
        url="...", 
        enabled=True
    ),
    # ...
}

```

## ➕ Como Adicionar Nova Imobiliária

Graças à `ScraperFactory` e ao padrão Pipeline, adicionar um novo site é simples:

1. **Criar Parser:** Crie um ficheiro em `parsers/` (ex: `nova_imob_parser.py`) implementando `IParser`.
2. **Registar na Factory:** No ficheiro `main.py` (função `configurar_scrapers`), registe a nova imobiliária:

```python
# Exemplo em main.py
from parsers.nova_imob_parser import NovaImobParser

ScraperFactory.register(
    key='novaimob', 
    parser_cls=NovaImobParser, 
    wait_selector="div.classe-do-cartao", 
    source_name="Nova Imobiliária"
)

```

3. **Adicionar Configuração:** Adicione a URL e a chave correspondente em `config/settings.py`.

O sistema encarregar-se-á de criar a Pipeline, gerir o cache e o Selenium automaticamente.
