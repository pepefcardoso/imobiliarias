from scrapers.tecimob_base import TecimobScraper

BASE_URL = "https://pauloemayer.com"
API_ENDPOINT = "https://api-sites2.gerenciarimoveis-cf.com.br/api/properties"

class PauloEMayerScraper(TecimobScraper):
    name = "pauloemayer"
    BASE_URL = BASE_URL
    API_ENDPOINT = API_ENDPOINT
    _HEADERS = {
        "x-domain": "pauloemayer.com",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }