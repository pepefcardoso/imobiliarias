from scrapers.tecimob_base import TecimobScraper

BASE_URL = "https://rodneimoveis.com.br"
API_ENDPOINT = "https://api-sites2.gerenciarimoveis-cf.com.br/api/properties"

class RFNegociosScraper(TecimobScraper):
    name = "rfnegocios"
    BASE_URL = BASE_URL
    API_ENDPOINT = API_ENDPOINT
    _HEADERS = {
        "x-domain": "www.rodneimoveis.com.br",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }