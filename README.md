Um motor de busca de imóveis em tempo real que traduz os critérios do usuário para os sistemas de 30–40 imobiliárias diferentes, normaliza os dados e apresenta resultados unificados com filtragem programática garantida.

---

# Propósito do Projeto

Este projeto deixou de ser um rastreador passivo para se tornar um **buscador ativo**. Ao clicar em "Buscar", o sistema:

- **Roteia a busca:** Traduz filtros globais para parâmetros específicos de cada site alvo.
- **Executa em paralelo:** Consulta dezenas de imobiliárias simultaneamente para retorno imediato.
- **Garante a lógica:** Aplica filtragem programática rigorosa (ex: assegura que "2 quartos" retorne resultados $\ge$ 2, mesmo que o site original use busca exata).
- **Unifica a experiência:** Apresenta uma tabela única, paginada e limpa para o usuário.

---

# Arquitetura de Busca

Sistema de Fluxo On-Demand:

```text
Entrada do Usuário (UI)
    ↓
SearchQuery (Objeto de Critérios)
    ↓
Aggregator (ThreadPoolExecutor)
    ↓
Scrapers (Tradução e Extração Real-time)
    ↓
Post-Processing (Filtro de Segurança Programático)
    ↓
UI (Tabela Paginada)

```

---

# Estrutura do Projeto

```text
project/
│
├── core/
│   ├── models.py          # Definição de Property e SearchQuery
│   └── parsing_utils.py   # Helpers de normalização de dados
│
├── scrapers/
│   ├── base.py            # Classe abstrata AgencyScraper
│   ├── agency_a.py        # Implementações específicas
│   └── ...
│
├── services/
│   └── aggregator.py      # Orquestrador de busca e filtro final
│
├── infrastructure/
│   ├── http_client.py     # Requisições estáticas rápidas
│   └── browser_client.py  # Automação para sites com JS
│
├── api/
│   └── main.py            # Endpoints FastAPI
│
├── config/
│   └── settings.py        # URLs, timeouts e limites de página
│
└── tests/

```

---

# Conceitos Chave

## Modelos de Dados (Contratos)

O sistema é guiado por dois modelos estáveis no `core/models.py`:

1. **SearchQuery:** O que o usuário deseja (Quartos $\ge$ X, Banheiros $\ge$ X, Preço Min/Max).
2. **Property:** O dado normalizado que retorna de cada agência.

## Estratégia de Filtragem ($\ge$)

Para resolver a inconsistência entre sites (ex: busca exata vs. busca "ou mais"), adotamos:

- **Filtro Remoto:** O scraper tenta usar o filtro do site para reduzir o tráfego.
- **Filtro Local (Segurança):** O `Aggregator` re-valida cada imóvel programaticamente antes de enviar à UI, garantindo que os requisitos de "mínimo de quartos/banheiros" sejam estritamente atendidos.

---

# API

Utilizando **FastAPI**.

**Endpoint Principal:**
`GET /properties?min_bedrooms=2&max_price=500000&city=Tubarao`

**Resposta:**

```json
[
  {
    "agency": "exemplo_imobiliaria",
    "title": "Apartamento Central",
    "price": 450000.0,
    "bedrooms": 3,
    "url": "https://..."
  }
]
```

---

# Configuração e Escalabilidade

- **Concorrência:** Gerenciada por `ThreadPoolExecutor` para busca simultânea em 40 agências.
- **Timeouts:** Limite rigoroso por scraper (ex: 15s) para evitar travamento da busca global.
- **Configuração Central:** `config/settings.py` guarda todos os seletores e URLs, evitando _hardcoding_ nos scrapers.

---

# Desenvolvimento Local

1. **Instalar dependências:** `pip install -r requirements.txt`
2. **Rodar API:** `uvicorn api.main:app --reload`
3. **Testar:** Acesse `http://localhost:8000/docs` para testar os filtros de busca.

---

# Filosofia de Código

- **Simplicidade:** Não use bancos de dados ou camadas complexas até que a persistência seja um requisito.
- **Isolamento:** Se o site de uma imobiliária mudar, apenas um arquivo em `/scrapers` deve ser editado.
- **Resiliência:** O sistema deve ignorar falhas individuais de scrapers e entregar o máximo de resultados possível.
