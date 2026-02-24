"""
tests/test_keyonimoveis.py

Unit tests for the KeyOn scraper.

Strategy:
  - Uses a JSON fixture extracted from the real API response (captured via HAR).
  - Mocks the HTTP session so no live network calls are made.
  - Validates that every Property field is correctly normalized.
"""

import json
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.settings import AgencyConfig
from core.models import Property
from scrapers.keyonimoveis import KeyOnImoveisScraper

# ---------------------------------------------------------------------------
# Minimal fixture: two listings drawn directly from the captured HAR response.
# One has a populated urlpublica; the other requires URL construction.
# ---------------------------------------------------------------------------

FIXTURE_PAGE_1 = {
    "quantidade": 2,
    "lista": [
        {
            "codigo": 8027,
            "titulo": "Anúncio de Venda – Casa Geminada em Tubarão/SC",
            "finalidade": "Venda",
            "tipo": "Casa Geminada",
            "valor": "R$ 289.900,00",
            "bairro": "São João (Margem Esquerda)",
            "cidade": "Tubarão",
            "estado": "SC",
            "numeroquartos": "2",
            "numerobanhos": "1",
            "numerovagas": "1",
            "areaprincipal": "53,00",
            "areainterna": "53,00",
            # urlpublica is populated for this listing
            "urlpublica": "https://www.keyonimoveis.com.br/imovel/anuncio-de-venda-casa-geminada-em-tubarao-sc/8027",
            "url_amigavel": "anuncio-de-venda-casa-geminada-em-tubarao-sc",
        },
        {
            "codigo": 5990,
            "titulo": "Apartamento à venda, 2 quartos, 1 vaga, Monte Castelo - Tubarão/SC",
            "finalidade": "Venda",
            "tipo": "Apartamento",
            "valor": "R$ 235.000,00",
            "bairro": "Monte Castelo",
            "cidade": "Tubarão",
            "estado": "SC",
            "numeroquartos": "2",
            "numerobanhos": "1",
            "numerovagas": "1",
            "areaprincipal": "45,96",
            "areainterna": "45,96",
            # urlpublica is empty → URL must be constructed from slug + code
            "urlpublica": "",
            "url_amigavel": "apartamento-a-venda-2-quartos-1-vaga-monte-castelo-tubarao-sc",
        },
    ],
    "favoritos": [],
}


def _make_mock_response(payload: dict) -> MagicMock:
    """Returns a mock requests.Response that serialises *payload* as JSON."""
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = payload
    return mock_resp


class TestKeyOnNormalization(unittest.TestCase):
    """Tests that raw API data is correctly mapped to Property objects."""

    def _scraper(self) -> KeyOnImoveisScraper:
        config = AgencyConfig(
            name="keyonimoveis",
            url="https://www.keyonimoveis.com.br",
            max_pages=5,
        )
        return KeyOnImoveisScraper(config=config)

    def test_returns_correct_number_of_properties(self):
        scraper = self._scraper()
        scraper.client._session.post = MagicMock(
            return_value=_make_mock_response(FIXTURE_PAGE_1)
        )
        results = scraper.scrape()
        self.assertEqual(len(results), 2)

    def test_all_results_are_property_instances(self):
        scraper = self._scraper()
        scraper.client._session.post = MagicMock(
            return_value=_make_mock_response(FIXTURE_PAGE_1)
        )
        for prop in scraper.scrape():
            self.assertIsInstance(prop, Property)

    def test_agency_name_is_set(self):
        scraper = self._scraper()
        scraper.client._session.post = MagicMock(
            return_value=_make_mock_response(FIXTURE_PAGE_1)
        )
        for prop in scraper.scrape():
            self.assertEqual(prop.agency, "keyonimoveis")

    def test_title_normalized(self):
        scraper = self._scraper()
        scraper.client._session.post = MagicMock(
            return_value=_make_mock_response(FIXTURE_PAGE_1)
        )
        results = scraper.scrape()
        self.assertEqual(
            results[0].title,
            "Anúncio de Venda – Casa Geminada em Tubarão/SC",
        )

    def test_price_parsed_correctly(self):
        scraper = self._scraper()
        scraper.client._session.post = MagicMock(
            return_value=_make_mock_response(FIXTURE_PAGE_1)
        )
        results = scraper.scrape()
        self.assertAlmostEqual(results[0].price, 289900.0)
        self.assertAlmostEqual(results[1].price, 235000.0)

    def test_area_parsed_correctly(self):
        scraper = self._scraper()
        scraper.client._session.post = MagicMock(
            return_value=_make_mock_response(FIXTURE_PAGE_1)
        )
        results = scraper.scrape()
        self.assertAlmostEqual(results[0].area, 53.0)
        self.assertAlmostEqual(results[1].area, 45.96)

    def test_bedrooms_parsed(self):
        scraper = self._scraper()
        scraper.client._session.post = MagicMock(
            return_value=_make_mock_response(FIXTURE_PAGE_1)
        )
        results = scraper.scrape()
        self.assertEqual(results[0].bedrooms, 2)
        self.assertEqual(results[1].bedrooms, 2)

    def test_bathrooms_parsed(self):
        scraper = self._scraper()
        scraper.client._session.post = MagicMock(
            return_value=_make_mock_response(FIXTURE_PAGE_1)
        )
        results = scraper.scrape()
        self.assertEqual(results[0].bathrooms, 1)

    def test_parking_parsed(self):
        scraper = self._scraper()
        scraper.client._session.post = MagicMock(
            return_value=_make_mock_response(FIXTURE_PAGE_1)
        )
        results = scraper.scrape()
        self.assertEqual(results[0].parking, 1)

    def test_neighborhood_set(self):
        scraper = self._scraper()
        scraper.client._session.post = MagicMock(
            return_value=_make_mock_response(FIXTURE_PAGE_1)
        )
        results = scraper.scrape()
        self.assertEqual(results[0].neighborhood, "São João (Margem Esquerda)")
        self.assertEqual(results[1].neighborhood, "Monte Castelo")

    def test_city_set(self):
        scraper = self._scraper()
        scraper.client._session.post = MagicMock(
            return_value=_make_mock_response(FIXTURE_PAGE_1)
        )
        for prop in scraper.scrape():
            self.assertEqual(prop.city, "Tubarão")

    def test_url_uses_urlpublica_when_available(self):
        scraper = self._scraper()
        scraper.client._session.post = MagicMock(
            return_value=_make_mock_response(FIXTURE_PAGE_1)
        )
        results = scraper.scrape()
        self.assertEqual(
            results[0].url,
            "https://www.keyonimoveis.com.br/imovel/anuncio-de-venda-casa-geminada-em-tubarao-sc/8027",
        )

    def test_url_constructed_when_urlpublica_empty(self):
        scraper = self._scraper()
        scraper.client._session.post = MagicMock(
            return_value=_make_mock_response(FIXTURE_PAGE_1)
        )
        results = scraper.scrape()
        self.assertEqual(
            results[1].url,
            "https://www.keyonimoveis.com.br/imovel/apartamento-a-venda-2-quartos-1-vaga-monte-castelo-tubarao-sc/5990",
        )


class TestKeyOnPagination(unittest.TestCase):
    """Tests that pagination stops at the right page."""

    def _scraper(self, max_pages: int = 10) -> KeyOnImoveisScraper:
        config = AgencyConfig(
            name="keyonimoveis",
            url="https://www.keyonimoveis.com.br",
            max_pages=max_pages,
        )
        return KeyOnImoveisScraper(config=config)

    def test_single_page_when_quantity_fits(self):
        """If quantidade ≤ PAGE_SIZE, only one POST should be made."""
        scraper = self._scraper()
        mock_post = MagicMock(return_value=_make_mock_response(FIXTURE_PAGE_1))
        scraper.client._session.post = mock_post
        scraper.scrape()
        self.assertEqual(mock_post.call_count, 1)

    def test_stops_at_max_pages(self):
        """Pagination must not exceed config.max_pages."""
        # Simulate an API that always returns 40 total listings (2 pages worth)
        page_response = {
            "quantidade": 40,
            "lista": [FIXTURE_PAGE_1["lista"][0]] * 20,
            "favoritos": [],
        }
        scraper = self._scraper(max_pages=1)
        mock_post = MagicMock(return_value=_make_mock_response(page_response))
        scraper.client._session.post = mock_post
        scraper.scrape()
        # max_pages=1 → only one call despite 2 pages available
        self.assertEqual(mock_post.call_count, 1)

    def test_empty_lista_stops_pagination(self):
        """An empty lista on first page should return no properties."""
        empty_response = {"quantidade": 0, "lista": [], "favoritos": []}
        scraper = self._scraper()
        scraper.client._session.post = MagicMock(
            return_value=_make_mock_response(empty_response)
        )
        results = scraper.scrape()
        self.assertEqual(results, [])


class TestKeyOnEdgeCases(unittest.TestCase):
    """Tests for malformed or incomplete listing data."""

    def _scraper(self) -> KeyOnImoveisScraper:
        config = AgencyConfig(
            name="keyonimoveis",
            url="https://www.keyonimoveis.com.br",
            max_pages=5,
        )
        return KeyOnImoveisScraper(config=config)

    def test_listing_without_url_is_skipped(self):
        """Listings with no url_amigavel and no urlpublica are silently dropped."""
        bad_listing = {
            "codigo": None,
            "titulo": "Broken listing",
            "valor": "R$ 100.000,00",
            "bairro": "Centro",
            "cidade": "Tubarão",
            "numeroquartos": "1",
            "numerobanhos": "1",
            "numerovagas": "0",
            "areaprincipal": "40,00",
            "urlpublica": "",
            "url_amigavel": "",
        }
        payload = {"quantidade": 1, "lista": [bad_listing], "favoritos": []}
        scraper = self._scraper()
        scraper.client._session.post = MagicMock(
            return_value=_make_mock_response(payload)
        )
        results = scraper.scrape()
        self.assertEqual(results, [])

    def test_missing_optional_fields_return_none(self):
        """Optional fields absent from the API response map to None."""
        minimal_listing = {
            "codigo": 9999,
            "titulo": "Minimal listing",
            "valor": "",
            "bairro": "",
            "cidade": "",
            "numeroquartos": "",
            "numerobanhos": "",
            "numerovagas": "",
            "areaprincipal": "",
            "urlpublica": "",
            "url_amigavel": "minimal-listing",
        }
        payload = {"quantidade": 1, "lista": [minimal_listing], "favoritos": []}
        scraper = self._scraper()
        scraper.client._session.post = MagicMock(
            return_value=_make_mock_response(payload)
        )
        results = scraper.scrape()
        self.assertEqual(len(results), 1)
        prop = results[0]
        self.assertIsNone(prop.price)
        self.assertIsNone(prop.area)
        self.assertIsNone(prop.bedrooms)
        self.assertIsNone(prop.bathrooms)
        self.assertIsNone(prop.parking)
        self.assertIsNone(prop.neighborhood)
        self.assertIsNone(prop.city)


if __name__ == "__main__":
    unittest.main()