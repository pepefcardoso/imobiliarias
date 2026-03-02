from scrapers.tecimob_base import TecimobScraper

BASE_URL = "https://bitimoveis.com"
API_ENDPOINT = "https://api-sites2.gerenciarimoveis-cf.com.br/api/properties"


class BitImoveisScraper(TecimobScraper):
    name = "bitimoveis"
    BASE_URL = BASE_URL
    API_ENDPOINT = API_ENDPOINT
    _HEADERS = {
        "x-domain": "bitimoveis.com",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }