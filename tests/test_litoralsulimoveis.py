import unittest
from unittest.mock import MagicMock
from scrapers.litoralsulimoveis import LitoralSulImoveisScraper
from core.models import Property

class TestLitoralSulNormalization(unittest.TestCase):
    def setUp(self):
        self.scraper = LitoralSulImoveisScraper()
        # Fixture baseada no JSON fornecido
        self.fixture = {
            "data": [
                {
                    "price": "R$284.900,00",
                    "title_formatted": "RESIDENCIAL VISTA",
                    "url": "apartamento-a-venda-sao-joao-tubarao-residencial-vista",
                    "address": {"formatted": "São João (Margem Esquerda) - Tubarão/SC"},
                    "areas": {"primary_area": {"value": "43,25"}},
                    "rooms": {
                        "garage": {"value": 1},
                        "bedroom": {"value": 2}
                    }
                },
                {
                    "price": "R$250.000,00",
                    "title_formatted": "Casa mista.",
                    "url": "casa-a-venda-2-dormitorios-bairro-fabio-silva-tubarao-sc-litoral-sul-imoveis/5774",
                    "address": {"formatted": "Fábio Silva - Tubarão/SC"},
                    "areas": {
                        "primary_area": {"value": "97,44"},
                        "total_area": {"value": "198"}
                    },
                    "rooms": {"bedroom": {"value": 2}, "garage": {"value": 1}}
                }
            ],
            "meta": {"pagination": {"total_pages": 1}}
        }

    def test_normalization_fields(self):
        """Verifica se os campos do snippet são mapeados corretamente."""
        self.scraper._fetch_page = MagicMock(return_value=self.fixture)
        results = self.scraper.scrape()
        
        self.assertEqual(len(results), 2)
        
        # Teste Apartamento (Residencial Vista)
        apt = results[0]
        self.assertEqual(apt.price, 284900.0)
        self.assertEqual(apt.area, 43.25)
        self.assertEqual(apt.neighborhood, "São João (Margem Esquerda)")
        self.assertEqual(apt.city, "Tubarão")
        self.assertIn("litoralsulimoveis.com.br/comprar/", apt.url)

        # Teste Casa (Fábio Silva) - Deve preferir total_area (198) sobre primary (97.44)
        casa = results[1]
        self.assertEqual(casa.area, 198.0)
        self.assertEqual(casa.neighborhood, "Fábio Silva")

    def test_empty_response(self):
        self.scraper._fetch_page = MagicMock(return_value={"data": [], "meta": {"pagination": {"total_pages": 1}}})
        self.assertEqual(self.scraper.scrape(), [])

if __name__ == "__main__":
    unittest.main()