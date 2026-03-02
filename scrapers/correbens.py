from scrapers.tecimob_base import TecimobScraper

BASE_URL = "https://correbens.com.br"
API_ENDPOINT = "https://api-sites2.gerenciarimoveis-cf.com.br/api/properties"

class CorrebensScraper(TecimobScraper):
    name = "correbens"
    BASE_URL = BASE_URL
    API_ENDPOINT = API_ENDPOINT
    default_sort = "-is_price_shown,-calculated_price,id"
    _HEADERS = {
        "x-domain": "correbens.com.br",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }