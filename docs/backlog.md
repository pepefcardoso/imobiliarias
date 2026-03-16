#### **[SCRAP-03]** Refatoração dos Scrapers Customizados (`KeyOnImoveis`, `DubettuImoveis`)

- **Descrição Detalhada:** Assim como o Tecimob, os scrapers que herdam diretamente de `AgencyScraper` precisam ser atualizados. Por exemplo, em `KeyOnImoveisScraper._build_payload`, valores como `"numeroquartos": 1` e `"valorate": 320000` estão fixos.
- **Critério de Aceite:** Os métodos `scrape()` destas classes devem aceitar o parâmetro `query: SearchQuery` e utilizá-lo para montar o payload JSON ou Form-Data correto.
- **Complexidade:** Média
- **Prioridade:** Média
