import unittest
from unittest.mock import MagicMock
from scrapers.vendimoveis import VendimoveisScraper
from core.models import Property

class TestVendimoveisNormalization(unittest.TestCase):
    def setUp(self):
        self.scraper = VendimoveisScraper()
        # Fixture baseada no JSON real fornecido
        self.fixture = {
            "data": [{
                "id": "66db1f18-f284-41bd-9b0d-39b89edbbea8",
                "price": "R$298.000,00",
                "title_formatted": "Apartamento em Centro, Tubarão/SC",
                "url": "apartamento-a-venda-no-bairro-centro-em-tubarao-sc/2494",
                "address": {"formatted": "Centro - Tubarão/SC"},
                "areas": {
                    "primary_area": {"value": "66,95"},
                    "total_area": {"value": "77,37"}
                },
                "rooms": {
                    "bedroom": {"value": 2},
                    "bathroom": {"value": 2},
                    "garage": {"value": 1}
                }
            }],
            "meta": {"pagination": {"total_pages": 1}}
        }

    def test_normalization_maps_fields_correctly(self):
        """Verifica se os campos da Tecimob são mapeados corretamente para Property."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = self.fixture
        mock_resp.raise_for_status = MagicMock()
        self.scraper.client._session.get = MagicMock(return_value=mock_resp)
        
        results = self.scraper.scrape()
        self.assertEqual(len(results), 1)
        prop = results[0]
        
        self.assertEqual(prop.agency, "vendimoveis")
        self.assertEqual(prop.price, 298000.0) # parse_price
        self.assertEqual(prop.area, 77.37) # Prefere total_area
        self.assertEqual(prop.bedrooms, 2)
        self.assertEqual(prop.neighborhood, "Centro")
        self.assertEqual(prop.city, "Tubarão")
        self.assertIn("vendimoveis.com.br/comprar/", prop.url)

if __name__ == "__main__":
    unittest.main()