# 🏠 Agregador de Imóveis (Web Scraper)

Este projeto é uma ferramenta de automação desenvolvida em Python para monitorizar e unificar pesquisas de imóveis de diferentes sites de imobiliárias.

O objetivo é simplificar a procura de casa, centralizando os resultados de várias fontes (que possuem estruturas HTML diferentes) numa única tabela padronizada. O projeto oferece agora uma **interface web** amigável e suporte a sites dinâmicos.

## 🚀 Funcionalidades

-   **Multi-site:** Extrai dados de diferentes imobiliárias (ex: KeyOn, QualAlugar).
-   **Interface Web:** Painel visual construído com Streamlit para iniciar pesquisas e visualizar resultados.
-   **Suporte a JavaScript:** Utiliza **Selenium** para carregar sites que dependem de renderização dinâmica.
-   **Padronização:** Converte dados heterogéneos num formato único (Título, Preço, Link, Área, Quartos, etc.).
-   **Exportação:** Gera dados prontos para análise (Pandas DataFrame) e permite exportação para CSV/Excel.

## 🛠️ Arquitetura e Tecnologias

O projeto segue os princípios de **Clean Code** e **SOLID**, garantindo escalabilidade e facilidade de manutenção:

-   **Linguagem:** Python 3.x
-   **Interface Gráfica:** `streamlit`
-   **Web Scraping:** `selenium` (navegação), `beautifulsoup4` (parsing HTML)
-   **Análise de Dados:** `pandas`
-   **Padrões de Projeto:**
    -   **Factory Method:** Para a criação dos scrapers adequados (`ScraperFactory`).
    -   **Repository Pattern:** Para abstrair a persistência/armazenamento dos dados (`ImovelRepository`).
    -   **Strategy Pattern:** Cada imobiliária possui a sua estratégia de extração.
    -   **Separation of Concerns:** Divisão clara entre *Scraping* (baixar dados) e *Parsing* (interpretar dados).

### Estrutura de Pastas

```text
imobiliarias/
├── app.py                  # Interface Web (Streamlit)
├── main.py                 # Orquestrador (Terminal/CLI)
├── config/                 # Configurações (URLs, variáveis)
├── domain/                 # Modelos de dados (Imovel, ScraperResult)
├── factories/              # Criação de instâncias dos scrapers
├── infrastructure/         # Clientes HTTP/Selenium
├── interfaces/             # Contratos (Protocolos/ABCs)
├── parsers/                # Lógica de extração de dados do HTML
├── repositories/           # Gestão e armazenamento dos dados extraídos
├── scrapers/               # Orquestração do fluxo de busca por site
└── services/               # Lógica de negócio (Logs, Manager)

```

## 📦 Como Instalar

1. **Clone o repositório** ou descarregue os ficheiros.
2. **Crie um ambiente virtual** (recomendado):
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


*(Nota: É necessário ter o Google Chrome instalado na máquina para o Selenium funcionar corretamente).*

## ▶️ Como Usar

Existem duas formas de utilizar a ferramenta:

### 1. Interface Web (Recomendado)

Para uma experiência visual mais agradável:

```bash
streamlit run imobiliarias/app.py

```

O navegador abrirá automaticamente com o painel "Monitor de Imóveis". Clique em **"🚀 Executar Monitorização"** para iniciar.

### 2. Terminal (CLI)

Para execução direta ou agendamento de tarefas:

```bash
python imobiliarias/main.py

```

Os resultados serão exibidos no terminal e guardados (se configurado).

## ⚙️ Configuração

As URLs de pesquisa e ativação de cada imobiliária são geridas no ficheiro `config/settings.py`:

```python
SCRAPERS = {
    'keyon': ScraperConfig(
        name='KeyOn',
        url="...", # Insira a sua URL de pesquisa aqui
        enabled=True
    ),
    # ...
}

```

## ➕ Como Adicionar Nova Imobiliária

Graças à arquitetura modular, para adicionar um novo site:

1. **Parser:** Crie um ficheiro em `parsers/` (ex: `nova_imob_parser.py`) implementando `IParser`. Use o `BeautifulSoup` aqui para extrair os dados.
2. **Scraper:** Crie um ficheiro em `scrapers/` (ex: `nova_imob.py`) implementando `IScraper`. Este usa o Parser criado acima.
3. **Factory:** Atualize o `factories/scraper_factory.py` para saber criar o novo scraper.
4. **Config:** Adicione a entrada no dicionário em `config/settings.py`.
5. **Registo:** No `main.py`, adicione a lógica para carregar esta nova configuração no `configurar_scrapers`.