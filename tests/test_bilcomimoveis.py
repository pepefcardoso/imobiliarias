import unittest
from unittest.mock import MagicMock
from scrapers.bilcomimoveis import BilcomImoveisScraper
from core.models import Property

class TestBilcomNormalization(unittest.TestCase):
    def setUp(self):
        self.scraper = BilcomImoveisScraper()
        # Mock fixture based on provided data.txt [cite: 423]
        self.fixture = {
            "data": [{
                "id": "3942c425-7191-43d0-ae9e-ab47573f89bc",
                "price": "R$150.000,00",
                "title_formatted": "Casa à venda no bairro Guarda, em Tubarão/SC",
                "url": "casa-a-venda-no-bairro-guarda-em-tubarao-sc/741",
                "address": {"formatted": "Guarda - Tubarão/SC"},
                "areas": {
                    "primary_area": {"value": "50"},
                    "total_area": {"value": "360"}
                },
                "rooms": {
                    "bedroom": {"value": 2},
                    "bathroom": {"value": 1},
                    "garage": {"value": 2}
                }
            }],
            "meta": {"pagination": {"total_pages": 1}}
        }

    def test_normalization(self):
        # Mock the API response
        mock_resp = MagicMock()
        mock_resp.json.return_value = self.fixture
        self.scraper.client._session.get = MagicMock(return_value=mock_resp)
        
        results = self.scraper.scrape()
        self.assertEqual(len(results), 1)
        prop = results[0]
        
        self.assertEqual(prop.agency, "bilcomimoveis")
        self.assertEqual(prop.price, 150000.0)
        self.assertEqual(prop.area, 360.0) # Prefers total_area if available
        self.assertEqual(prop.bedrooms, 2)
        self.assertEqual(prop.neighborhood, "Guarda")
        self.assertIn("bilcomimoveis.com.br/comprar/", prop.url)

if __name__ == "__main__":
    unittest.main()