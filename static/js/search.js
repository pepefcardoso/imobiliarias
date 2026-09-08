const CITY_CENTERS = {
  Tubarão: { lat: -28.48, lng: -49.0066 },
  "Capivari de Baixo": { lat: -28.4447, lng: -48.9536 },
  Laguna: { lat: -28.4816, lng: -48.7811 },
  Jaguaruna: { lat: -28.6141, lng: -49.0253 },
};

window.BAIRROS = {
  Tubarão: [
    "Andrino",
    "Bom Pastor",
    "Campestre",
    "Centro",
    "Congonhas",
    "Dehon",
    "Fábio Silva",
    "Guarda (Margem Direita)",
    "Guarda (Margem Esquerda)",
    "Humaitá",
    "Km 60",
    "Km 63",
    "Madre",
    "Monte Castelo",
    "Morrotes",
    "Oficinas",
    "Passagem",
    "Passo do Gado",
    "Recife",
    "Revoredo",
    "Santa Luzia",
    "Santo Antônio de Pádua",
    "São Bernardo",
    "São Clemente",
    "São Cristóvão",
    "São João (Margem Direita)",
    "São João (Margem Esquerda)",
    "São Martinho",
    "Sertão dos Corrêa",
    "Vila Esperança",
    "Vila Moema",
  ],
  "Capivari de Baixo": [
    "Alvorada",
    "Bairro da Amizade",
    "Caçador",
    "Centro",
    "Ilhota",
    "Operário",
    "Paraíso",
    "Santa Lúcia",
    "Santo André",
    "Três de Maio",
    "Vila Flor",
  ],
  Laguna: [
    "Bananal",
    "Barbacena",
    "Barranceira",
    "Bentos",
    "Cabeçuda",
    "Caputera",
    "Centro",
    "Esperança",
    "Farol de Santa Marta",
    "Itapirubá",
    "Jardim das Palmeiras",
    "Magalhães",
    "Mar Grosso",
    "Mato Alto",
    "Nova Fazenda",
    "Paranhos",
    "Passagem da Barra",
    "Ponta das Pedras",
    "Portinho",
    "Progresso",
    "Ribeirão Pequeno",
    "Vila Vitória",
  ],
  Jaguaruna: [
    "Arroio Corrente",
    "Balneário Esplanada",
    "Beira Mar",
    "Camacho",
    "Campo Bom",
    "Centro",
    "Costa da Lagoa",
    "Dunas do Sul",
    "Figueira",
    "Garopaba do Sul",
    "Jabuticabeira",
    "Laranjal",
    "Morro Azul",
    "Morro Bonito",
    "Olho D'Água",
    "Retiro",
    "Riacho dos Guedes",
    "Torneiro",
  ],
};

function calcDistance(lat1, lon1, lat2, lon2) {
  if (!lat1 || !lon1 || !lat2 || !lon2) return null;
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

document.addEventListener("alpine:init", () => {
  Alpine.store("search", {
    properties: [],
    view: "table",
    sortKey: "price",
    sortDir: "asc",
    page: 1,
    pageSize: 30,
    modalImg: null,
    sourcesLinks: null,
    map: null,
    markersGroup: null,
    geocodeQueue: [],
    isGeocoding: false,
    geocodeCache: JSON.parse(sessionStorage.getItem("geocodeCache") || "{}"),

    loadFromJson() {
      const el = document.getElementById("properties-json");
      const raw = el ? JSON.parse(el.textContent) : [];
      this.properties = raw.map((p) => {
        const price_sqm = p.price && p.area ? p.price / p.area : null;
        let distance = null;
        if (p.city && CITY_CENTERS[p.city] && p.latitude && p.longitude) {
          distance = calcDistance(
            CITY_CENTERS[p.city].lat,
            CITY_CENTERS[p.city].lng,
            p.latitude,
            p.longitude,
          );
        }
        return { ...p, price_sqm, distance };
      });
      this.page = 1;
      if (this.view === "map") this.resetMapAndGeocode();
    },

    get sorted() {
      const numericKeys = [
        "price",
        "condo_fee",
        "area",
        "bedrooms",
        "bathrooms",
        "parking",
        "distance",
        "price_sqm",
      ];
      return [...this.properties].sort((a, b) => {
        let av = a[this.sortKey],
          bv = b[this.sortKey];
        if (av == null && bv == null) return 0;
        if (av == null) return 1;
        if (bv == null) return -1;
        if (numericKeys.includes(this.sortKey))
          return this.sortDir === "asc" ? av - bv : bv - av;
        if (typeof av === "string") av = av.toLowerCase();
        if (typeof bv === "string") bv = bv.toLowerCase();
        if (av < bv) return this.sortDir === "asc" ? -1 : 1;
        if (av > bv) return this.sortDir === "asc" ? 1 : -1;
        return 0;
      });
    },
    get totalPages() {
      return Math.ceil(this.sorted.length / this.pageSize) || 1;
    },
    get pageData() {
      const start = (this.page - 1) * this.pageSize;
      return this.sorted.slice(start, start + this.pageSize);
    },
    get pageRange() {
      const total = this.totalPages,
        range = [];
      for (let i = 1; i <= total; i++) {
        if (i === 1 || i === total || Math.abs(i - this.page) <= 2)
          range.push(i);
        else if (range[range.length - 1] !== "...") range.push("...");
      }
      return range;
    },

    setSort(key) {
      if (this.sortKey === key)
        this.sortDir = this.sortDir === "asc" ? "desc" : "asc";
      else {
        this.sortKey = key;
        this.sortDir = "asc";
      }
      this.page = 1;
    },
    goPage(n) {
      if (n < 1) n = 1;
      if (n > this.totalPages) n = this.totalPages;
      if (n === this.page) return;
      this.page = n;
      const wrap = document.querySelector(".table-wrap");
      if (wrap)
        window.scrollTo({ top: wrap.offsetTop - 60, behavior: "smooth" });
    },
    setView(view) {
      this.view = view;
      if (view === "map") this.$nextTick(() => this.initMap());
    },

    initMap() {
      if (!this.map) {
        const center = CITY_CENTERS["Tubarão"];
        this.map = L.map("map-container").setView([center.lat, center.lng], 13);
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: "&copy; OpenStreetMap contributors",
        }).addTo(this.map);
        this.markersGroup = L.markerClusterGroup({
          chunkedLoading: true,
          maxClusterRadius: 40,
        });
        this.map.addLayer(this.markersGroup);
      }
      setTimeout(() => this.map.invalidateSize(), 100);
      this.resetMapAndGeocode();
    },
    resetMapAndGeocode() {
      if (this.markersGroup) this.markersGroup.clearLayers();
      this.geocodeQueue = [];
      this.isGeocoding = false;
      this.properties.forEach((p) => {
        if (!p.city) return;
        let query = p.street
          ? `${p.street.replace(/,\s*\d+.*$/, "").trim()}, ${p.neighborhood || ""}, ${p.city}, SC, Brasil`
          : p.neighborhood
            ? `${p.neighborhood}, ${p.city}, SC, Brasil`
            : `${p.city}, SC, Brasil`;
        p._geocodeQuery = query
          .replace(/,\s*,/g, ",")
          .replace(/\s+/g, " ")
          .trim();
        p._fallbackQuery = p.neighborhood
          ? `${p.neighborhood}, ${p.city}, SC, Brasil`
          : `${p.city}, SC, Brasil`;
        p._geocoded = false;
      });
      this.startGeocoding();
    },
    startGeocoding() {
      if (this.isGeocoding || !this.map) return;
      this.properties.forEach((p) => {
        if (
          !p._geocoded &&
          p._geocodeQuery &&
          this.geocodeCache[p._geocodeQuery]
        ) {
          const cached = this.geocodeCache[p._geocodeQuery];
          if (!cached.notFound) this.addMarker(p, cached.lat, cached.lon);
          p._geocoded = true;
        }
      });
      this.geocodeQueue = this.properties.filter(
        (p) => !p._geocoded && p._geocodeQuery,
      );
      if (this.geocodeQueue.length > 0) {
        this.isGeocoding = true;
        this.processQueue();
      }
    },
    async processQueue() {
      if (this.geocodeQueue.length === 0 || this.view !== "map") {
        this.isGeocoding = false;
        return;
      }
      const p = this.geocodeQueue.shift();
      try {
        let result = await this.fetchNominatim(p._geocodeQuery);
        if (!result && p._fallbackQuery !== p._geocodeQuery)
          result = await this.fetchNominatim(p._fallbackQuery);
        if (result) {
          this.geocodeCache[p._geocodeQuery] = result;
          this.addMarker(p, result.lat, result.lon);
        } else {
          this.geocodeCache[p._geocodeQuery] = { notFound: true };
        }
        sessionStorage.setItem(
          "geocodeCache",
          JSON.stringify(this.geocodeCache),
        );
      } catch (err) {
        console.error("Geocoding failed", p._geocodeQuery, err);
      }
      setTimeout(() => this.processQueue(), 1100);
    },
    async fetchNominatim(query) {
      const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`;
      const res = await fetch(url, { headers: { "Accept-Language": "pt-BR" } });
      if (!res.ok) return null;
      const data = await res.json();
      return data.length > 0
        ? { lat: parseFloat(data[0].lat), lon: parseFloat(data[0].lon) }
        : null;
    },
    addMarker(p, lat, lon) {
      if (!this.markersGroup) return;
      const priceStr = p.price
        ? `R$ ${Number(p.price).toLocaleString("pt-BR")}`
        : "Consulte";
      const bedsStr = p.bedrooms ? `${p.bedrooms} quartos` : "";
      const areaStr = p.area ? ` | ${p.area}m²` : "";
      const imgStr = p.image_url
        ? `<img src="${p.image_url}" style="width:100%;height:120px;object-fit:cover;border-radius:4px;margin-bottom:8px">`
        : "";
      const popup = `<div style="width:220px;font-family:'DM Sans',sans-serif">${imgStr}<strong style="font-size:.9rem">${p.title}</strong><br><span style="color:var(--green);font-weight:bold;font-size:1rem">${priceStr}</span><br><div style="font-size:.8rem;margin:4px 0">${bedsStr}${areaStr}</div><span style="font-size:.75rem;color:var(--ink-muted);background:var(--bg);padding:2px 6px;border-radius:4px">${p.agency}</span><br><a href="${p.url}" target="_blank" style="display:block;margin-top:10px;color:var(--accent);font-weight:500;font-size:.85rem">Ver Imóvel &rarr;</a></div>`;
      L.marker([lat, lon]).bindPopup(popup).addTo(this.markersGroup);
    },

    openImage(url) {
      this.modalImg = url;
    },
    closeImage() {
      this.modalImg = null;
    },
    openSources(links) {
      this.sourcesLinks = links;
    },
    closeSources() {
      this.sourcesLinks = null;
    },

    fmtPrice(v) {
      return v == null
        ? '<span class="price-null">-</span>'
        : `<span class="price">R$ ${Number(v).toLocaleString("pt-BR", { maximumFractionDigits: 0 })}</span>`;
    },
    fmtArea(v) {
      return v == null
        ? '<span class="null-dash">-</span>'
        : `${Number(v).toLocaleString("pt-BR", { maximumFractionDigits: 0 })} m²`;
    },
    fmtPriceSqm(v) {
      return v == null
        ? '<span class="null-dash">-</span>'
        : `R$ ${Number(v).toLocaleString("pt-BR", { maximumFractionDigits: 0 })}/m²`;
    },
  });
});
