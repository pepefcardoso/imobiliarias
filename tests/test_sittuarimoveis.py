import unittest
from unittest.mock import MagicMock
from scrapers.sittuarimoveis import SittuarImoveisScraper
from core.models import Property

# ... (Mantenha o código da classe SittuarImoveisScraper e o helper _split_address aqui se eles estiverem no mesmo arquivo)

# ---------------------------------------------------------------------------
# Unit Tests for Sittuar Scraper
# ---------------------------------------------------------------------------

class TestSittuarNormalization(unittest.TestCase):
    def setUp(self):
        self.scraper = SittuarImoveisScraper()
        # Fixture baseada no formato real da API Tecimob/Gerenciar Imóveis
        self.fixture = {
            "data": [{
                "id": "3942c425-7191-43d0-ae9e-ab47573f89bc",
                "reference": "741",
                "price": "R$150.000,00",
                "title_formatted": "Casa à venda no bairro Guarda, em Tubarão/SC",
                "url": "casa-a-venda-no-bairro-guarda-em-tubarao-sc/741",
                "address": {"formatted": "Guarda - Tubarão/SC"},
                "areas": {
                    "total_area": {"value": "360", "measure": "m²"}
                },
                "rooms": {
                    "bedroom": {"value": 2},
                    "bathroom": {"value": 1},
                    "garage": {"value": 2}
                }
            }],
            "meta": {
                "pagination": {
                    "total": 1,
                    "per_page": 21,
                    "current_page": 1,
                    "total_pages": 1
                }
            }
        }

    def test_normalization_correctly_maps_fields(self):
        """Verifica se os campos da API são mapeados corretamente para o modelo Property."""
        # Mock do método interno para retornar a fixture sem fazer requisição real
        self.scraper._fetch_page = MagicMock(return_value=self.fixture)
        
        results = self.scraper.scrape()
        
        self.assertEqual(len(results), 1)
        prop = results[0]
        
        self.assertIsInstance(prop, Property)
        self.assertEqual(prop.agency, "sittuarimoveis")
        self.assertEqual(prop.price, 150000.0)
        self.assertEqual(prop.area, 360.0)
        self.assertEqual(prop.bedrooms, 2)
        self.assertEqual(prop.bathrooms, 1)
        self.assertEqual(prop.parking, 2)
        self.assertEqual(prop.neighborhood, "Guarda")
        self.assertEqual(prop.city, "Tubarão")
        self.assertIn("sittuarimoveis.com.br/comprar/", prop.url)

    def test_split_address_helper(self):
        """Testa o helper de extração de bairro e cidade."""
        from scrapers.sittuarimoveis import _split_address
        
        # Caso completo
        self.assertEqual(_split_address("Centro - Tubarão/SC"), ("Centro", "Tubarão"))
        # Sem bairro
        self.assertEqual(_split_address("Tubarão/SC"), (None, "Tubarão"))
        # Vazio
        self.assertEqual(_split_address(""), (None, None))

    def test_handle_empty_results(self):
        """Garante que o scraper lida corretamente com páginas vazias."""
        empty_fixture = {"data": [], "meta": {"pagination": {"total_pages": 1}}}
        self.scraper._fetch_page = MagicMock(return_value=empty_fixture)
        
        results = self.scraper.scrape()
        self.assertEqual(results, [])

if __name__ == "__main__":
    unittest.main()