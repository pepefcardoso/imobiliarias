from scrapers.tecimob_base import TecimobScraper

BASE_URL = "https://carlosmarquescorretor.com.br"
API_ENDPOINT = "https://api-sites.gerenciarimoveis-cf.com.br/api/properties"

class CarlosMarquesScraper(TecimobScraper):
    name = "carlosmarques"
    BASE_URL = BASE_URL
    API_ENDPOINT = API_ENDPOINT
    default_sort = "-created_at,id"
    _HEADERS = {
        "x-domain": "carlosmarquescorretor.com.br",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }