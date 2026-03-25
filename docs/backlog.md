## Backlog do Projeto: Motor de Busca Imobiliário

# Épico 1: Estabilidade e Performance (Backend)

Task 1.1: Implementar Estratégia de Caching Em Memória (MVP)

Descrição: Atualizar o endpoint /properties para armazenar em cache os resultados de buscas recentes. Isso evitará que o sistema re-execute chamadas para dezenas de imobiliárias caso múltiplos usuários façam buscas com os mesmos filtros em um curto espaço de tempo.

Critérios de Aceite:

    [X] O cache deve ser baseado no hash dos parâmetros da busca (SearchQuery).

    [X] O Tempo de Vida (TTL) do cache deve ser de 15 a 30 minutos.

    [X] Logs devem indicar claramente quando um resultado foi servido via "CACHE HIT" vs "CACHE MISS".

Detalhes Técnicos:

    Utilizar a biblioteca cachetools (ex: TTLCache) no api/main.py.

    Atenção: Como o cache será em memória na instância da aplicação (FastAPI), o uso de memória RAM deve ser monitorado. Limitar o cache a no máximo 500 buscas simultâneas para não estourar a memória do Render/servidor.

# Épico 2: Experiência do Usuário (UX) e Qualidade dos Dados

Task 2.1: Desduplicação Inteligente de Imóveis (Fingerprinting)

Descrição: Imóveis idênticos anunciados por diferentes imobiliárias estão poluindo a tabela de resultados. Precisamos agrupar esses registros em um único item na visualização, mostrando as variações de preço e as opções de contato.

Critérios de Aceite:

    [X] A tabela de resultados deve exibir apenas 1 linha por imóvel único.

    [X] A coluna "Imobiliária" deve mostrar uma tag especial (ex: "Listado em 3 Imobiliárias") quando houver duplicidade.

    [X] Ao clicar na linha, o usuário deve conseguir ver os links de todas as imobiliárias que anunciaram aquele imóvel.

Detalhes Técnicos:

    Backend (services/aggregator.py): Criar uma função _deduplicate_properties.

    Heurística do Fingerprint: Agrupar imóveis que compartilhem a mesma Cidade + Bairro + Quartos + Banheiros, E que possuam Preço com variação máxima de ± 5% e Área com variação de ± 5%.

    Model (core/models.py): Adicionar um campo source_links: list[dict] no modelo Property para armazenar as URLs e Nomes das múltiplas imobiliárias agrupadas.

Task 2.2: Adicionar Extração e Coluna de "Taxa de Condomínio"

Descrição: O valor do condomínio é um fator de decisão crítico que atualmente não está visível para o usuário.

Critérios de Aceite:

    [X] O backend deve extrair o valor do condomínio da API da imobiliária (quando disponível) ou do texto do anúncio.

    [X] O modelo Property e o JSON da API devem incluir o campo condo_fee (float).

    [X] A UI (Tabela HTML) deve exibir uma nova coluna "Condomínio (R$)".

Detalhes Técnicos:

    Atualizar core/models.py com condo_fee: Optional[float] = None.

    Atualizar core/parsing_utils.py com uma nova função parse_condo_fee contendo Regex para varrer descrições (ex: r"(?i)condom[íi]nio[:\s]*R?\$?\s*([\d\.,]+)") caso a API não entregue o campo pronto.

    Ajustar os scrapers principais (ex: TecimobScraper) para buscar a chave correspondente no payload original.

# Épico 3: Visualização Geográfica (A Grande Feature)

Task 3.1: Lazy Geocoding no Frontend e Visualização em Mapa

Descrição: Para oferecer uma visualização em mapa sem derrubar a performance do backend (que faz scraping em tempo real) e sem sofrer bloqueios de IP, implementaremos a resolução de endereços (Geocoding) de forma "preguiçosa" (Lazy) diretamente no navegador do usuário. A conversão de "Rua + Bairro + Cidade" para Coordenadas só ocorrerá se, e somente se, o usuário abrir a aba do Mapa.

Critérios de Aceite:

    [ ] A interface deve possuir um botão/toggle para alternar entre "Visualização em Tabela" e "Visualização em Mapa".

    [ ] O backend não deve fazer requisições para descobrir coordenadas. Ele apenas repassa os campos street, neighborhood e city extraídos.

    [ ] Ao abrir o mapa, o frontend deve iniciar uma fila de requisições em background para a API do Nominatim (OpenStreetMap), processando no máximo 1 endereço por segundo (para respeitar o limite de uso gratuito e evitar bloqueio do IP do usuário).

    [ ] Os imóveis (pins) devem ir "pipocando" na tela gradativamente conforme as coordenadas são descobertas.

    [ ] Se o endereço exato (Rua) não for encontrado pelo Nominatim, o sistema deve fazer um fallback (tentativa secundária) buscando apenas pelo Centro do Bairro.

    [ ] O mapa deve utilizar agrupamento (Marker Clustering) para imóveis próximos ou no mesmo prédio.

Detalhes Técnicos & Implementação:

    Bibliotecas Frontend: Utilizar Leaflet.js para o mapa e Leaflet.markercluster para agrupar dezenas de marcações no mesmo bairro/rua.

    Serviço de Geocoding: API gratuita do Nominatim https://nominatim.openstreetmap.org/search?format=json&q={ENDERECO}.

    Fila de Requisições (Rate Limiting no Front): - Criar um array com os endereços únicos retornados na busca.

        Usar um setInterval ou setTimeout recursivo no script.js com atraso de 1000ms (1 segundo) entre as chamadas para não violar os Termos de Uso do OSM.

    Cache Local no Navegador (Otimização): - Antes de fazer o fetch para o Nominatim, o script deve verificar um objeto local (ex: const geocodeCache = {} ou sessionStorage).

        Se a "Rua Tubalcain Faraco, Centro, Tubarão" já foi buscada naquele mapa, reaproveita a coordenada, economizando requests da rede e acelerando a plotagem.

    Ajuste nos Scrapers (Oportunista): No backend (ex: TecimobScraper), tentar extrair o nome da rua para o model Property (campo street: Optional[str]) quando a informação estiver explicitamente disponível no payload ou HTML da imobiliária.
