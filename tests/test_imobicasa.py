import unittest
from unittest.mock import MagicMock
from scrapers.imobicasa import ImobicasaScraper
from core.models import Property

class TestImobicasaNormalization(unittest.TestCase):
    def setUp(self):
        self.scraper = ImobicasaScraper()
        # Fixture baseada nos dados reais fornecidos
        self.fixture = {
            "data": [{
                "price": "R$259.000,00",
                "title_formatted": "Casa Mista no São João  - Em frente ao KOMPRÃO",
                "url": "casa-a-venda-no-bairro-sao-joao-margem-esquerda-em-tubarao-sc/357",
                "address": {"formatted": "São João (Margem Esquerda) - Tubarão/SC"},
                "areas": {
                    "primary_area": {"value": "150"},
                    "total_area": {"value": "218,60"}
                },
                "rooms": {
                    "bedroom": {"value": 2},
                    "bathroom": {"value": 2},
                    "garage": {"value": 1}
                }
            }],
            "meta": {"pagination": {"total_pages": 1}}
        }

    def test_normalization(self):
        """Valida se os dados da API Imobicasa são convertidos corretamente."""
        self.scraper._fetch_page = MagicMock(return_value=self.fixture)
        
        results = self.scraper.scrape()
        self.assertEqual(len(results), 1)
        prop = results[0]
        
        self.assertEqual(prop.agency, "imobicasa")
        self.assertEqual(prop.price, 259000.0)
        self.assertEqual(prop.area, 218.6) # Verifica se pegou a total_area
        self.assertEqual(prop.bedrooms, 2)
        self.assertEqual(prop.neighborhood, "São João (Margem Esquerda)")
        self.assertEqual(prop.city, "Tubarão")
        self.assertIn("imobicasa.com.br/comprar/", prop.url)

if __name__ == "__main__":
    unittest.main()