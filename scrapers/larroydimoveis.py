from scrapers.tecimob_base import TecimobScraper

BASE_URL = "https://larroydimoveis.com.br"
API_ENDPOINT = "https://api-sites.gerenciarimoveis-cf.com.br/api/properties"

class LarroyImoveisScraper(TecimobScraper):
    name = "larroydimoveis"
    BASE_URL = BASE_URL
    API_ENDPOINT = API_ENDPOINT
    default_sort = "is_price_shown,calculated_price,id"
    use_city_slug_filter = False
    _HEADERS = {
        "x-domain": "larroydimoveis.com.br",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }