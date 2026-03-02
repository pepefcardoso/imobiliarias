from scrapers.tecimob_base import TecimobScraper

BASE_URL = "https://sittuarimoveis.com.br"
API_ENDPOINT = "https://api-sites.gerenciarimoveis-cf.com.br/api/properties"


class SittuarImoveisScraper(TecimobScraper):
    name = "sittuarimoveis"
    BASE_URL = BASE_URL
    API_ENDPOINT = API_ENDPOINT
    _HEADERS = {
        "x-domain": "sittuarimoveis.com.br",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }