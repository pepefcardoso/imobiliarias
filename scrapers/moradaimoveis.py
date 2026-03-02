from scrapers.tecimob_base import TecimobScraper

BASE_URL = "https://moradaimoveis.com.br"
API_ENDPOINT = "https://api-sites2.gerenciarimoveis-cf.com.br/api/properties"

class MoradaImoveisScraper(TecimobScraper):
    name = "moradaimoveis"
    BASE_URL = BASE_URL
    API_ENDPOINT = API_ENDPOINT
    default_sort = "-is_price_shown,-calculated_price,id"
    _HEADERS = {
        "x-domain": "moradaimoveis.com.br",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }