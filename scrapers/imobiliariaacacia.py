from scrapers.tecimob_base import TecimobScraper

BASE_URL = "https://imobiliariaacacia.com.br"
API_ENDPOINT = "https://api-sites2.gerenciarimoveis-cf.com.br/api/properties"

class ImobiliariaAcaciaScraper(TecimobScraper):
    name = "imobiliariaacacia"
    BASE_URL = BASE_URL
    API_ENDPOINT = API_ENDPOINT
    _HEADERS = {
        "x-domain": "imobiliariaacacia.com.br",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }