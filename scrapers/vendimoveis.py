from scrapers.tecimob_base import TecimobScraper

BASE_URL = "https://vendimoveis.com.br"
API_ENDPOINT = "https://api-sites2.gerenciarimoveis-cf.com.br/api/properties"

class VendimoveisScraper(TecimobScraper):
    name = "vendimoveis"
    BASE_URL = BASE_URL
    API_ENDPOINT = API_ENDPOINT
    default_sort = "-is_price_shown,-calculated_price,id"
    _HEADERS = {
        "x-domain": "vendimoveis.com.br",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }