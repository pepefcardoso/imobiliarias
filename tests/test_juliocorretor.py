import unittest
from unittest.mock import MagicMock
from scrapers.juliocorretor import JulioCorretorScraper
from core.models import Property

class TestJulioCorretorNormalization(unittest.TestCase):
    def setUp(self):
        self.scraper = JulioCorretorScraper()
        # Fixture baseada no JSON real fornecido pelo usuário
        self.fixture = {
            "data": [
                {
                    "price": "R$299.000,00",
                    "title_formatted": "Casa Geminada",
                    "url": "casa-a-venda-no-bairro-nova-congonha-em-tubarao-sc/726",
                    "address": {"formatted": "Nova Congonha - Tubarão/SC"},
                    "areas": {"private_area": {"value": "55"}},
                    "rooms": {
                        "garage": {"value": 1},
                        "bedroom": {"value": 2}
                    }
                },
                {
                    "price": "R$140.000,00",
                    "title_formatted": "Casa de Madeira",
                    "url": "casa-a-venda-no-bairro-km-60-em-tubarao-sc/626",
                    "address": {"formatted": "Km 60 - Tubarão/SC"},
                    "areas": {"total_area": {"value": "308"}},
                    "rooms": {"bedroom": {"value": 2}, "garage": {"value": 1}}
                }
            ],
            "meta": {"pagination": {"total_pages": 1}}
        }

    def test_normalization(self):
        """Verifica se os campos da Tecimob são mapeados corretamente para Property."""
        self.scraper._fetch_page = MagicMock(return_value=self.fixture)
        results = self.scraper.scrape()
        
        self.assertEqual(len(results), 2)
        
        # Teste item 1 (Casa Geminada)
        casa = results[0]
        self.assertEqual(casa.agency, "juliocorretor")
        self.assertEqual(casa.price, 299000.0)
        self.assertEqual(casa.area, 55.0)
        self.assertEqual(casa.neighborhood, "Nova Congonha")
        self.assertEqual(casa.city, "Tubarão")
        self.assertIn("juliocorretor.com.br/comprar/", casa.url)

        # Teste item 2 (Km 60)
        km60 = results[1]
        self.assertEqual(km60.neighborhood, "Km 60")
        self.assertEqual(km60.area, 308.0)

if __name__ == "__main__":
    unittest.main()