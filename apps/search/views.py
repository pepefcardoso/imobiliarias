import hashlib
import json

from django.core.cache import cache
from django.shortcuts import render
from django.views import View

from domain.models import SearchQuery

from .forms import SearchForm
from .services import get_aggregator


def _build_pills(data: dict) -> list[str]:
    pills = []
    if data.get("city"):
        pills.append(f"📍 {data['city']}")
    if data.get("neighborhood"):
        pills.append(f"📍 {data['neighborhood']}")
    if data.get("min_price"):
        pills.append(f"Mín. R$ {data['min_price']:,.0f}".replace(",", "."))
    if data.get("max_price"):
        pills.append(f"Máx. R$ {data['max_price']:,.0f}".replace(",", "."))
    if data.get("min_bedrooms"):
        pills.append(f"🛏️ {data['min_bedrooms']}+ quartos")
    if data.get("min_bathrooms"):
        pills.append(f"🚿 {data['min_bathrooms']}+ banheiros")
    if data.get("min_parking"):
        pills.append(f"🚗 {data['min_parking']}+ vagas")
    if data.get("min_area"):
        pills.append(f"Mín. {data['min_area']:.0f} m²")
    if data.get("max_area"):
        pills.append(f"Máx. {data['max_area']:.0f} m²")
    return pills


class SearchView(View):
    def get(self, request):
        form = SearchForm(request.GET)
        properties, pills = [], []

        if request.GET and form.is_valid():
            data = form.cleaned_data
            query = SearchQuery(
                **data,
                property_types=request.GET.getlist("property_types") or None,
            )
            cache_key = "search:" + hashlib.md5(
                json.dumps(query.__dict__, sort_keys=True, default=str).encode()
            ).hexdigest()

            properties = cache.get(cache_key)
            if properties is None:
                properties = get_aggregator().search(query)
                cache.set(cache_key, properties, timeout=900)

            pills = _build_pills(data)

        context = {
            "form": form,
            "properties": properties,
            "properties_data": [p.to_dict() for p in properties],
            "pills": pills,
        }
        template = "search/_results.html" if request.htmx else "search/index.html"
        return render(request, template, context)