# imobiliarias/tests/test_bitimoveis.py

import unittest
from unittest.mock import MagicMock
from scrapers.bitimoveis import BitImoveisScraper
from core.models import Property

class TestBitImoveisNormalization(unittest.TestCase):
    def setUp(self):
        self.scraper = BitImoveisScraper()
        # Fixture baseada nos dados reais do data.txt 
        self.fixture = {
            "data": [{
                "id": "939d82c2-e1bf-4675-b174-1d6dcbf05686",
                "price": "R$220.000,00",
                "title_formatted": "Casa de 02 dormitórios",
                "url": "casa-a-venda-no-bairro-sao-joao-margem-direita-em-tubarao-sc/1074",
                "address": {"formatted": "São João (Margem Direita) - Tubarão/SC"},
                "areas": {
                    "private_area": {"value": "66"},
                    "total_area": {"value": "360"}
                },
                "rooms": {
                    "bedroom": {"value": "2"},
                    "bathroom": {"value": "1"},
                    "garage": {"value": "1"}
                }
            }],
            "meta": {"pagination": {"total_pages": 1}}
        }

    def test_normalization(self):
        """Verifica se os campos da Tecimob são mapeados corretamente para Property."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = self.fixture
        self.scraper.client._session.get = MagicMock(return_value=mock_resp)
        
        results = self.scraper.scrape()
        self.assertEqual(len(results), 1)
        prop = results[0]
        
        self.assertIsInstance(prop, Property)
        self.assertEqual(prop.agency, "bitimoveis")
        self.assertEqual(prop.price, 220000.0) # Normalizado via parse_price
        self.assertEqual(prop.area, 360.0) # Prefere total_area 
        self.assertEqual(prop.bedrooms, 2)
        self.assertEqual(prop.neighborhood, "São João (Margem Direita)")
        self.assertIn("bitimoveis.com/comprar/", prop.url)

if __name__ == "__main__":
    unittest.main()