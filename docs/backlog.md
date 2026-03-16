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
