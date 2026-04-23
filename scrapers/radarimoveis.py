from scrapers.tecimob_base import TecimobScraper

BASE_URL = "https://imobiliariaradar.com.br"
API_ENDPOINT = "https://api-sites2.gerenciarimoveis-cf.com.br/api/properties"

class RadarImoveisScraper(TecimobScraper):
    name = "radarimoveis"
    BASE_URL = BASE_URL
    API_ENDPOINT = API_ENDPOINT
    _HEADERS = {
        "x-domain": "imobiliariaradar.com.br",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }