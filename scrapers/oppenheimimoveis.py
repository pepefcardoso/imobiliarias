from scrapers.tecimob_base import TecimobScraper

BASE_URL = "https://oppenheimimoveis.com.br"
API_ENDPOINT = "https://api-sites2.gerenciarimoveis-cf.com.br/api/properties"

class OppenheimImoveisScraper(TecimobScraper):
    name = "oppenheimimoveis"
    BASE_URL = BASE_URL
    API_ENDPOINT = API_ENDPOINT
    _HEADERS = {
        "x-domain": "oppenheimimoveis.com.br",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }