from scrapers.tecimob_base import TecimobScraper

BASE_URL = "https://imobiliariaconquista.log.br"
API_ENDPOINT = "https://api-sites2.gerenciarimoveis-cf.com.br/api/properties"

class ImobiliariaConquistaScraper(TecimobScraper):
    name = "imobiliariaconquista"
    BASE_URL = BASE_URL
    API_ENDPOINT = API_ENDPOINT
    _HEADERS = {
        "x-domain": "imobiliariaconquista.log.br",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }