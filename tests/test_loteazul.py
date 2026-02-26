import unittest
from unittest.mock import MagicMock
from scrapers.loteazul import LoteAzulScraper
from core.models import Property

class TestLoteAzulNormalization(unittest.TestCase):
    def setUp(self):
        self.scraper = LoteAzulScraper()
        # Fixture baseada no JSON real fornecido para o Vista Residence
        self.fixture = {
            "data": [{
                "id": "4d1728c7-c4c2-4f6f-b5a0-789bb4709aea",
                "price": "R$285.900",
                "title_formatted": "Vista Residence",
                "url": "vista-residence-tubarao-sc/20601",
                "address": {"formatted": "São João (Margem Esquerda) - Tubarão/SC"},
                "areas": {
                    "primary_area": {"value": "43,25", "measure": "m²"}
                },
                "rooms": {
                    "bedroom": {"value": 2},
                    "bathroom": {"value": 1},
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
        
        self.assertEqual(prop.agency, "loteazul")
        self.assertEqual(prop.price, 285900.0)
        self.assertEqual(prop.area, 43.25)
        self.assertEqual(prop.bedrooms, 2)
        self.assertEqual(prop.neighborhood, "São João (Margem Esquerda)")
        self.assertEqual(prop.city, "Tubarão")
        self.assertIn("loteazul.com.br/imovel/vista-residence", prop.url)

if __name__ == "__main__":
    unittest.main()