from scrapers.tecimob_base import TecimobScraper

BASE_URL = "https://citymoveis.com.br"
API_ENDPOINT = "https://api-sites2.gerenciarimoveis-cf.com.br/api/properties"

class CityMoveisScraper(TecimobScraper):
    name = "citymoveis"
    BASE_URL = BASE_URL
    API_ENDPOINT = API_ENDPOINT
    _HEADERS = {
        "x-domain": "citymoveis.com.br",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }