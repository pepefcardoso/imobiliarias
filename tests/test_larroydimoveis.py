"""
tests/test_larroydimoveis.py

Unit tests for the Larroyd Imóveis scraper.

Strategy:
  - Uses a JSON fixture matching the Tecimob API response format.
  - Mocks the HTTP session so no live network calls are made.
  - Validates that every Property field is correctly normalized.
"""

import sys
import os
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.settings import AgencyConfig
from core.models import Property
from scrapers.larroydimoveis import LarroyImoveisScraper, _split_address


# ---------------------------------------------------------------------------
# Fixtures — two listings in the Tecimob card format
# ---------------------------------------------------------------------------

FIXTURE_PAGE_1 = {
    "data": [
        {
            "id": "de8ae8ae-6cae-4355-866c-9acd0f559f7a",
            "reference": "4415",
            "price": "R$245.000",
            "total_price": "R$245.000",
            "title_formatted": "Casa geminada à venda no Residencial Morada dos Sonhos",
            "url": "casa-geminada-a-venda-no-residencial-morada-dos-sonhos-sao-joao-tubarao-sc/4415",
            "address": {"formatted": "São João (Margem Esquerda) - Tubarão/SC"},
            "areas": {
                "primary_area": {"name": "private_area", "value": "53,11", "measure": "m²"},
                "built_area": {"name": "built_area", "value": "54,44", "measure": "m²"},
            },
            "rooms": {
                "garage": {"value": 1},
                "bedroom": {"value": 2},
                "bathroom": {"value": 1},
            },
        },
        {
            "id": "1f83f807-d00e-4f1a-b8b3-4c905809a547",
            "reference": "2244",
            "price": "R$260.000",
            "total_price": "R$260.000",
            "title_formatted": "Apartamento à venda no Residencial Oficinas",
            "url": "apartamento-a-venda-em-oficinas-tubarao-sc-residencial-oficinas/2244",
            "address": {"formatted": "Oficinas - Tubarão/SC"},
            "areas": {
                "primary_area": {"name": "private_area", "value": "47,39", "measure": "m²"},
            },
            "rooms": {
                "garage": {"value": 1},
                "bedroom": {"value": 2},
                "bathroom": {"value": 1},
            },
        },
    ],
    "meta": {
        "pagination": {
            "total": 2,
            "per_page": 21,
            "current_page": 1,
            "total_pages": 1,
        }
    },
}


def _make_mock_response(payload: dict) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = payload
    return mock_resp


def _make_scraper(max_pages: int = 10) -> LarroyImoveisScraper:
    config = AgencyConfig(
        name="larroydimoveis",
        url="https://larroydimoveis.com.br",
        use_browser=False,
        max_pages=max_pages,
    )
    return LarroyImoveisScraper(config=config)


# ---------------------------------------------------------------------------
# Normalization tests
# ---------------------------------------------------------------------------

class TestLarroyNormalization(unittest.TestCase):

    def setUp(self):
        self.scraper = _make_scraper()
        self.scraper.client._session.get = MagicMock(
            return_value=_make_mock_response(FIXTURE_PAGE_1)
        )

    def test_returns_correct_number_of_properties(self):
        results = self.scraper.scrape()
        self.assertEqual(len(results), 2)

    def test_all_results_are_property_instances(self):
        for prop in self.scraper.scrape():
            self.assertIsInstance(prop, Property)

    def test_agency_name(self):
        for prop in self.scraper.scrape():
            self.assertEqual(prop.agency, "larroydimoveis")

    def test_price_parsed(self):
        results = self.scraper.scrape()
        self.assertAlmostEqual(results[0].price, 245000.0)
        self.assertAlmostEqual(results[1].price, 260000.0)

    def test_area_uses_private_area_when_no_total_area(self):
        results = self.scraper.scrape()
        # First listing: no total_area — falls back to primary_area (private_area)
        self.assertAlmostEqual(results[0].area, 53.11)
        # Second listing: only private_area available
        self.assertAlmostEqual(results[1].area, 47.39)

    def test_bedrooms_parsed(self):
        results = self.scraper.scrape()
        self.assertEqual(results[0].bedrooms, 2)
        self.assertEqual(results[1].bedrooms, 2)

    def test_bathrooms_parsed(self):
        results = self.scraper.scrape()
        self.assertEqual(results[0].bathrooms, 1)
        self.assertEqual(results[1].bathrooms, 1)

    def test_parking_parsed(self):
        results = self.scraper.scrape()
        self.assertEqual(results[0].parking, 1)
        self.assertEqual(results[1].parking, 1)

    def test_neighborhood_extracted(self):
        results = self.scraper.scrape()
        self.assertEqual(results[0].neighborhood, "São João (Margem Esquerda)")
        self.assertEqual(results[1].neighborhood, "Oficinas")

    def test_city_extracted(self):
        results = self.scraper.scrape()
        self.assertEqual(results[0].city, "Tubarão")
        self.assertEqual(results[1].city, "Tubarão")

    def test_url_construction(self):
        results = self.scraper.scrape()
        self.assertEqual(
            results[0].url,
            "https://larroydimoveis.com.br/comprar/casa-geminada-a-venda-no-residencial-morada-dos-sonhos-sao-joao-tubarao-sc/4415",
        )
        self.assertEqual(
            results[1].url,
            "https://larroydimoveis.com.br/comprar/apartamento-a-venda-em-oficinas-tubarao-sc-residencial-oficinas/2244",
        )

    def test_title_normalized(self):
        results = self.scraper.scrape()
        self.assertEqual(
            results[0].title,
            "Casa geminada à venda no Residencial Morada dos Sonhos",
        )

    def test_area_prefers_total_area_when_present(self):
        fixture = {
            "data": [{
                **FIXTURE_PAGE_1["data"][0],
                "areas": {
                    "total_area": {"value": "200", "measure": "m²"},
                    "private_area": {"value": "53,11", "measure": "m²"},
                },
            }],
            "meta": {"pagination": {"total": 1, "per_page": 21, "current_page": 1, "total_pages": 1}},
        }
        self.scraper.client._session.get = MagicMock(
            return_value=_make_mock_response(fixture)
        )
        results = self.scraper.scrape()
        self.assertAlmostEqual(results[0].area, 200.0)


# ---------------------------------------------------------------------------
# Pagination tests
# ---------------------------------------------------------------------------

class TestLarroyPagination(unittest.TestCase):

    def test_single_page_when_all_results_fit(self):
        scraper = _make_scraper()
        mock_get = MagicMock(return_value=_make_mock_response(FIXTURE_PAGE_1))
        scraper.client._session.get = mock_get
        scraper.scrape()
        self.assertEqual(mock_get.call_count, 1)

    def test_stops_at_max_pages(self):
        """Pagination must not exceed config.max_pages."""
        multi_page_fixture = {
            "data": [FIXTURE_PAGE_1["data"][0]] * 21,
            "meta": {"pagination": {"total": 63, "per_page": 21, "current_page": 1, "total_pages": 3}},
        }
        scraper = _make_scraper(max_pages=2)
        mock_get = MagicMock(return_value=_make_mock_response(multi_page_fixture))
        scraper.client._session.get = mock_get
        scraper.scrape()
        # max_pages=2 → only 2 calls despite 3 pages available
        self.assertEqual(mock_get.call_count, 2)

    def test_empty_data_stops_pagination(self):
        empty_fixture = {
            "data": [],
            "meta": {"pagination": {"total": 0, "per_page": 21, "current_page": 1, "total_pages": 1}},
        }
        scraper = _make_scraper()
        scraper.client._session.get = MagicMock(return_value=_make_mock_response(empty_fixture))
        results = scraper.scrape()
        self.assertEqual(results, [])


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------

class TestLarroyEdgeCases(unittest.TestCase):

    def test_listing_without_url_slug_is_skipped(self):
        fixture = {
            "data": [{
                "id": "abc",
                "reference": "999",
                "price": "R$200.000",
                "title_formatted": "Sem slug",
                "url": "",
                "address": {"formatted": "Centro - Tubarão/SC"},
                "areas": {},
                "rooms": {},
            }],
            "meta": {"pagination": {"total": 1, "per_page": 21, "current_page": 1, "total_pages": 1}},
        }
        scraper = _make_scraper()
        scraper.client._session.get = MagicMock(return_value=_make_mock_response(fixture))
        results = scraper.scrape()
        self.assertEqual(results, [])

    def test_missing_optional_fields_return_none(self):
        fixture = {
            "data": [{
                "id": "minimal",
                "reference": "000",
                "price": "",
                "title_formatted": "",
                "url": "imovel-minimal/000",
                "address": {"formatted": ""},
                "areas": {},
                "rooms": {},
            }],
            "meta": {"pagination": {"total": 1, "per_page": 21, "current_page": 1, "total_pages": 1}},
        }
        scraper = _make_scraper()
        scraper.client._session.get = MagicMock(return_value=_make_mock_response(fixture))
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

    def test_x_domain_header_is_set(self):
        scraper = _make_scraper()
        self.assertEqual(
            scraper.client._session.headers.get("x-domain"),
            "larroydimoveis.com.br",
        )


# ---------------------------------------------------------------------------
# _split_address helper tests
# ---------------------------------------------------------------------------

class TestSplitAddress(unittest.TestCase):

    def test_full_address(self):
        self.assertEqual(_split_address("Centro - Tubarão/SC"), ("Centro", "Tubarão"))

    def test_no_neighborhood(self):
        self.assertEqual(_split_address("Tubarão/SC"), (None, "Tubarão"))

    def test_empty_string(self):
        self.assertEqual(_split_address(""), (None, None))

    def test_complex_neighborhood(self):
        self.assertEqual(
            _split_address("São João (Margem Esquerda) - Tubarão/SC"),
            ("São João (Margem Esquerda)", "Tubarão"),
        )

    def test_strips_whitespace(self):
        self.assertEqual(_split_address("  Oficinas  -  Tubarão/SC  "), ("Oficinas", "Tubarão"))


if __name__ == "__main__":
    unittest.main()