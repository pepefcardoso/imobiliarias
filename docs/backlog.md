# Backlog de Desenvolvimento: Agregador de Imóveis

## 1. Segurança e Legal (Prioridade Alta)

**Objetivo:** Remover alvos de scraping com alto risco comercial (OLX).

- [X] **Eliminar ficheiro do scraper:** Apagar completamente o ficheiro `scrapers/olx.py`.
- [X] **Limpar API e Registry:** No ficheiro `api/main.py`:
  - Remover a importação `from scrapers.olx import OlxScraper`.
  - Remover a chave `"olx": OlxScraper` do dicionário `SCRAPER_REGISTRY`.
- [X] **Limpar Configurações:** No ficheiro `config/settings.py`:
  - Remover o bloco `AgencyConfig` referente à `olx` na lista `settings.agencies`.

## 2. Novo Scraper: ChavesNaMao (Prioridade Alta)

**Objetivo:** Implementar a extração de dados do portal ChavesNaMao para expandir a base de imóveis do agregador.

- [X] **Criar o ficheiro do Scraper:** Criar `scrapers/chavesnamao.py` herdando da classe base `AgencyScraper`.
- [X] **Lógica de Tradução de URL:** Implementar a função `_build_url_and_params` para traduzir o `SearchQuery` na estrutura específica deles:
  - Mapear cidades para o formato da rota (ex: `sc-tubarao`).
  - Mapear quartos para a rota (ex: `1-quarto`).
  - Mapear os restantes parâmetros para a querystring `?filtro=` (ex: `pmin:100000,pmax:350000,amin:50,amax:300,ban:1,gar:1`).
- [X] **Extração de Dados:** Analisar a resposta HTML do ChavesNaMao. Como muitos portais modernos, é provável que os dados dos imóveis estejam embutidos num bloco JSON (como o `__NEXT_DATA__` ou similar) no código fonte. Extrair e normalizar para o objeto `Property`.
- [X] **Registo na API:** Adicionar o `ChavesNaMaoScraper` ao `SCRAPER_REGISTRY` em `api/main.py`.
- [X] **Configuração:** Adicionar o novo `AgencyConfig` com o URL base do ChavesNaMao em `config/settings.py`.

## 3. Filtros de Localização (Cidades e Bairros)

**Objetivo:** Transitar de pesquisa de cidade em texto livre para dropdowns estruturados.

- [X] **Backend - Atualizar Modelos (`core/models.py`):**
  - Adicionar `neighborhood: Optional[str] = field(default=None)` à classe `SearchQuery`.
- [X] **Backend - Atualizar API (`api/main.py`):**
  - Adicionar o parâmetro `neighborhood: Optional[str] = Query(default=None)` na função `get_properties`.
  - Passar este parâmetro na instanciação do objeto `SearchQuery`.
- [X] **Backend - Forçar Filtro de Bairro (`services/aggregator.py`):**
  - Na função `_apply_strict_filters`, adicionar lógica para filtrar bairros exatos (case-insensitive).
- [X] **Frontend - Atualizar UI de Cidade (`index.html`):**
  - Substituir o `<input type="text" id="filter-city">` por um `<select id="filter-city">`.
  - Adicionar as opções fixas (ex: "Todos", "Tubarão", "Capivari de Baixo", "Laguna").
- [X] **Frontend - Adicionar UI de Bairro (`index.html`):**
  - Criar um `<select id="filter-neighborhood">` ao lado da cidade.
  - Escrever função JavaScript para popular dinamicamente as opções de bairros dependendo da cidade selecionada.
  - Atualizar o envio e exibição dos filtros.

## 4. Imagens dos Imóveis

**Objetivo:** Exibir miniaturas na tabela de resultados.

- [ ] **Backend - Atualizar Modelos (`core/models.py` e `api/main.py`):**
  - Adicionar `image_url: Optional[str] = field(default=None)` ao `Property` e `PropertyResponse`.
- [ ] **Backend - Atualizar Tecimob (`scrapers/tecimob_base.py`):**
  - Adicionar `"photos"` ao parâmetro `include`. Extrair a URL da primeira foto no `_normalize()`.
- [ ] **Backend - Atualizar Scrapers Customizados:**
  - Extrair imagem principal em `dubettuimoveis.py`, `keyonimoveis.py` e no novo `chavesnamao.py`.
- [ ] **Frontend - Renderizar Imagens (`index.html`):**
  - Adicionar a coluna de Imagem no array `COLUMNS`. Injetar a tag `<img>` no `renderTable()`.

## 5. Melhorias de UI/UX

**Objetivo:** Dar melhor feedback visual ao utilizador.

- [ ] **Frontend - Estado de Carregamento (Skeleton):**
  - Criar "Skeleton Loader" animado enquanto aguarda a API.
- [ ] **Frontend - Estados Vazios e Erros:**
  - Melhorar visualmente a mensagem de tabela vazia.
- [ ] **Frontend - Botão Limpar Filtros:**
  - Atualizar `applyDefaults()` para suportar os novos dropdowns.

## 6. Verificações de Ordenação e Paginação

**Objetivo:** Garantir manipulação de dados perfeita no lado do cliente.

- [ ] **Frontend - Corrigir Lógica de Ordenação (`sortData`):**
  - Garantir que comparações de Preço/Área/Quartos são feitas matematicamente (`a - b`) e não alfabeticamente.
- [ ] **Frontend - Revisão da Paginação (`renderPagination`):**
  - Validar bloqueios nos limites de página e resets de página ao filtrar/ordenar.
