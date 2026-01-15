# 🏠 Agregador de Imóveis (Web Scraper)

Este projeto é uma ferramenta de automação desenvolvida em Python para monitorizar e unificar pesquisas de imóveis de diferentes sites de imobiliárias.

O objetivo é simplificar a procura de casa, centralizando os resultados de várias fontes (que possuem estruturas HTML diferentes) numa única tabela padronizada.

## 🚀 Funcionalidades

- **Multi-site:** Capaz de extrair dados de diferentes imobiliárias simultaneamente.
- **Padronização:** Converte dados heterogéneos em um formato único (Título, Preço, Link, Origem).
- **Exportação:** Gera uma estrutura de dados pronta para análise (Pandas DataFrame) ou exportação (Excel/CSV).

## 🛠️ Arquitetura e Tecnologias

O projeto segue os princípios de **Clean Code** e **SOLID**, utilizando Design Patterns para garantir escalabilidade:

- **Linguagem:** Python 3.x
- **Bibliotecas:** `requests`, `BeautifulSoup4`, `pandas`
- **Padrões de Projeto:**
    - **Strategy Pattern:** Cada imobiliária é uma estratégia de extração isolada.
    - **Interface:** Contrato `IScraper` garante consistência entre os "robôs".
    - **Single Responsibility Principle:** Separação clara entre domínio, lógica de extração e orquestração.

### Estrutura de Pastas

```text
projeto_imoveis/
├── main.py                 # Orquestrador principal
├── domain/                 # Definição dos dados (Modelos)
├── interfaces/             # Contratos (Interfaces)
├── scrapers/               # Implementações das imobiliárias
└── services/               # Lógica de negócio e gerenciamento

```

## 📦 Como Instalar

1. Clone o repositório ou baixe os arquivos.
2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

```


3. Instale as dependências:
```bash
pip install requests beautifulsoup4 pandas openpyxl

```



## ▶️ Como Usar

1. Abra o arquivo `main.py`.
2. Adicione ou configure as URLs de pesquisa nas instâncias dos scrapers:
```python
manager.adicionar_scraper(ImobiliariaAScraper("URL_DA_PESQUISA_REAL"))

```


3. Execute o programa:
```bash
python main.py

```



## ➕ Como Adicionar Nova Imobiliária

Graças à arquitetura modular, para adicionar um novo site:

1. Crie um novo arquivo em `scrapers/` (ex: `imobiliaria_c.py`).
2. Crie uma classe que herde de `IScraper`.
3. Implemente o método `buscar_imoveis` com a lógica específica do `BeautifulSoup` para aquele site.
4. Importe e adicione a nova classe no `main.py`.