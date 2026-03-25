from scrapers.tecimob_base import TecimobScraper

BASE_URL = "https://felixmarques.com.br"
API_ENDPOINT = "https://api-sites2.gerenciarimoveis-cf.com.br/api/properties"

class FelixMarquesScraper(TecimobScraper):
    name = "felixmarques"
    BASE_URL = BASE_URL
    API_ENDPOINT = API_ENDPOINT
    _HEADERS = {
        "x-domain": "felixmarques.com.br",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }