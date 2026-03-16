#### **[CORE-01]** Criação do Contrato de Busca (`SearchQuery`)

- **Descrição Detalhada:** O sistema precisa de um objeto unificado para trafegar os parâmetros de busca do usuário desde a requisição na API até os Scrapers. Devemos criar o `dataclass` `SearchQuery` no arquivo `core/models.py`.
- **Critério de Aceite:** O arquivo `core/models.py` deve exportar a classe `SearchQuery` contendo campos opcionais e tipados (ex: `min_price`, `max_price`, `min_bedrooms`, etc.).
- **Complexidade:** Baixa
- **Prioridade:** Crítica

#### **[API-01]** Refatoração do Endpoint de Busca (`api/main.py`)

- **Descrição Detalhada:** A API atualmente coleta todos os imóveis e filtra depois. O objetivo é transformar os _query parameters_ (parâmetros da URL) diretamente em um objeto `SearchQuery` e passá-lo para o `Aggregator`. A lógica de `if min_price is not None: properties = [...]` deve ser removida deste arquivo.
- **Critério de Aceite:** O endpoint `GET /properties` deve instanciar um `SearchQuery` e chamar `_state.aggregator.search(query)`. O retorno será apenas a conversão dos objetos `Property` para `PropertyResponse`.
- **Complexidade:** Baixa
- **Prioridade:** Alta

#### **[AGG-01]** Implementação do "Safety Net" no Aggregator (`services/aggregator.py`)

- **Descrição Detalhada:** O `Aggregator` já usa o `ThreadPoolExecutor` corretamente, mas o método `collect()` não recebe a requisição do usuário. Precisamos alterar o método para `search(self, query: SearchQuery) -> list[Property]`. Além disso, ele deve implementar o método privado `_apply_strict_filters(properties, query)` para garantir a regra lógica de inclusão mínima (ex: garantir programaticamente que os imóveis retornados tenham $\ge$ quartos do que o pedido).
- **Critério de Aceite:** O `Aggregator` deve repassar o objeto `query` para os scrapers no _Thread Pool_. Ao final, a lista unificada deve passar pelo filtro de segurança programático antes de ser retornada.
- **Complexidade:** Média
- **Prioridade:** Crítica

#### **[SCRAP-01]** Atualização da Interface Base dos Scrapers (`scrapers/base.py`)

- **Descrição Detalhada:** A classe abstrata `AgencyScraper` atualmente define `def scrape(self) -> list[Property]:`. Devemos atualizá-la para exigir a _query_ do usuário.
- **Critério de Aceite:** O método na interface abstrata deve ser atualizado para `@abstractmethod def scrape(self, query: SearchQuery) -> list[Property]:`.
- **Complexidade:** Baixa
- **Prioridade:** Alta

#### **[SCRAP-02]** Dinamização dos Filtros no `TecimobScraper` (`scrapers/tecimob_base.py`)

- **Descrição Detalhada:** Esta é a classe mãe de dezenas de imobiliárias. Atualmente, o método `_build_params` usa constantes como `DEFAULT_MIN_BEDROOMS`. Devemos alterar o método para `scrape(self, query: SearchQuery)` e passar essa `query` para `_build_params`.
- **Critério de Aceite:** Os parâmetros HTTP (`filter[bedroom_gte]`, `filter[price_lte]`, etc.) devem ser preenchidos com os valores oriundos do `query: SearchQuery`. Caso o usuário não informe um valor (seja `None`), o scraper não deve enviar o filtro correspondente na requisição (ou deve enviar o padrão do site, se obrigatório).
- **Complexidade:** Média
- **Prioridade:** Alta

#### **[SCRAP-03]** Refatoração dos Scrapers Customizados (`KeyOnImoveis`, `DubettuImoveis`)

- **Descrição Detalhada:** Assim como o Tecimob, os scrapers que herdam diretamente de `AgencyScraper` precisam ser atualizados. Por exemplo, em `KeyOnImoveisScraper._build_payload`, valores como `"numeroquartos": 1` e `"valorate": 320000` estão fixos.
- **Critério de Aceite:** Os métodos `scrape()` destas classes devem aceitar o parâmetro `query: SearchQuery` e utilizá-lo para montar o payload JSON ou Form-Data correto.
- **Complexidade:** Média
- **Prioridade:** Média
