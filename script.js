const API_BASE = "https://imobiliarias.onrender.com";
const PAGE_SIZE = 30;

let allData = [];
let sortKey = "price";
let sortDir = "asc";
let currentPage = 1;
let loading = false;

let currentView = "table";
let map = null;
let markersGroup = null;
let geocodeQueue = [];
let isGeocoding = false;
let geocodeCache = JSON.parse(sessionStorage.getItem("geocodeCache") || "{}");

const statusText = document.getElementById("status-text");
const errorArea = document.getElementById("error-area");
const tableContainer = document.getElementById("table-container");
const paginationEl = document.getElementById("pagination");
const filterSummaryEl = document.getElementById("filter-summary");

const DICIONARIO_BAIRROS = {
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

const CITY_CENTERS = {
  Tubarão: { lat: -28.48, lng: -49.0066 },
  "Capivari de Baixo": { lat: -28.4447, lng: -48.9536 },
  Laguna: { lat: -28.4816, lng: -48.7811 },
  Jaguaruna: { lat: -28.6141, lng: -49.0253 },
};

document
  .getElementById("btn-view-table")
  .addEventListener("click", () => setView("table"));
document
  .getElementById("btn-view-map")
  .addEventListener("click", () => setView("map"));

function setView(view) {
  currentView = view;
  if (view === "table") {
    document.getElementById("view-table-section").style.display = "block";
    document.getElementById("view-map-section").style.display = "none";
    document.getElementById("btn-view-table").classList.add("active");
    document.getElementById("btn-view-map").classList.remove("active");
  } else {
    document.getElementById("view-table-section").style.display = "none";
    document.getElementById("view-map-section").style.display = "block";
    document.getElementById("btn-view-table").classList.remove("active");
    document.getElementById("btn-view-map").classList.add("active");
    initMap();
    startGeocoding();
  }
}

function initMap() {
  if (!map) {
    const city = document.getElementById("filter-city").value || "Tubarão";
    const center = CITY_CENTERS[city] || CITY_CENTERS["Tubarão"];

    map = L.map("map-container").setView([center.lat, center.lng], 13);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    markersGroup = L.markerClusterGroup({
      chunkedLoading: true,
      maxClusterRadius: 40,
    });
    map.addLayer(markersGroup);
  }
  setTimeout(() => map.invalidateSize(), 100);
}

function prepareGeocodingData() {
  if (markersGroup) markersGroup.clearLayers();
  geocodeQueue = [];
  isGeocoding = false;

  allData.forEach((p) => {
    if (!p.city) return;

    let addressQuery = "";
    if (p.street) {
      const ruaLimpa = p.street.replace(/,\s*\d+.*$/, "").trim();
      addressQuery = `${ruaLimpa}, ${p.neighborhood || ""}, ${
        p.city
      }, SC, Brasil`;
    } else if (p.neighborhood) {
      addressQuery = `${p.neighborhood}, ${p.city}, SC, Brasil`;
    } else {
      addressQuery = `${p.city}, SC, Brasil`;
    }

    p._geocodeQuery = addressQuery
      .replace(/,\s*,/g, ",")
      .replace(/\s+/g, " ")
      .trim();
    p._fallbackQuery = p.neighborhood
      ? `${p.neighborhood}, ${p.city}, SC, Brasil`
      : `${p.city}, SC, Brasil`;
    p._geocoded = false;
  });
}

function startGeocoding() {
  if (isGeocoding) return;

  allData.forEach((p) => {
    if (!p._geocoded && p._geocodeQuery && geocodeCache[p._geocodeQuery]) {
      const cached = geocodeCache[p._geocodeQuery];
      if (!cached.notFound) {
        addMarkerToMap(p, cached.lat, cached.lon);
      }
      p._geocoded = true;
    }
  });

  geocodeQueue = allData.filter((p) => !p._geocoded && p._geocodeQuery);

  if (geocodeQueue.length > 0) {
    isGeocoding = true;
    processGeocodeQueue();
  }
}

async function processGeocodeQueue() {
  if (geocodeQueue.length === 0 || currentView !== "map") {
    isGeocoding = false;
    return;
  }

  const p = geocodeQueue.shift();

  if (geocodeCache[p._geocodeQuery]) {
    const cached = geocodeCache[p._geocodeQuery];
    if (!cached.notFound) {
      addMarkerToMap(p, cached.lat, cached.lon);
    }
    p._geocoded = true;
    processGeocodeQueue();
    return;
  }

  try {
    let result = await fetchNominatim(p._geocodeQuery);

    if (!result && p._fallbackQuery && p._fallbackQuery !== p._geocodeQuery) {
      result = await fetchNominatim(p._fallbackQuery);
    }

    if (result) {
      geocodeCache[p._geocodeQuery] = { lat: result.lat, lon: result.lon };
      sessionStorage.setItem("geocodeCache", JSON.stringify(geocodeCache));
      addMarkerToMap(p, result.lat, result.lon);
    } else {
      geocodeCache[p._geocodeQuery] = { notFound: true };
      sessionStorage.setItem("geocodeCache", JSON.stringify(geocodeCache));
    }
    p._geocoded = true;
  } catch (err) {
    console.error("Geocoding failed for", p._geocodeQuery, err);
  }

  setTimeout(processGeocodeQueue, 1100);
}

async function fetchNominatim(query) {
  const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
    query,
  )}&limit=1`;
  const res = await fetch(url, { headers: { "Accept-Language": "pt-BR" } });
  if (!res.ok) return null;
  const data = await res.json();
  if (data && data.length > 0) {
    return { lat: parseFloat(data[0].lat), lon: parseFloat(data[0].lon) };
  }
  return null;
}

function addMarkerToMap(p, lat, lon) {
  if (!markersGroup) return;

  const priceStr = p.price
    ? `R$ ${Number(p.price).toLocaleString("pt-BR")}`
    : "Consulte";
  const bedsStr = p.bedrooms ? `${p.bedrooms} quartos` : "";
  const areaStr = p.area ? ` | ${p.area}m²` : "";
  const imgStr = p.image_url
    ? `<img src="${p.image_url}" style="width: 100%; height: 120px; object-fit: cover; border-radius: 4px; margin-bottom: 8px;">`
    : "";

  const popupContent = `
    <div style="width: 220px; font-family: 'DM Sans', sans-serif;">
        ${imgStr}
        <strong style="font-size: 0.9rem;">${p.title}</strong><br>
        <span style="color: var(--green); font-weight: bold; font-size: 1rem;">${priceStr}</span><br>
        <div style="font-size: 0.8rem; margin: 4px 0;">${bedsStr}${areaStr}</div>
        <span style="font-size: 0.75rem; color: var(--ink-muted); display: inline-block; background: var(--bg); padding: 2px 6px; border-radius: 4px;">${p.agency}</span><br>
        <a href="${p.url}" target="_blank" style="display: block; margin-top: 10px; color: var(--accent); text-decoration: none; font-weight: 500; font-size: 0.85rem;">Ver Imóvel →</a>
    </div>
  `;

  const marker = L.marker([lat, lon]);
  marker.bindPopup(popupContent);
  markersGroup.addLayer(marker);
}

function calculateDistance(lat1, lon1, lat2, lon2) {
  if (!lat1 || !lon1 || !lat2 || !lon2) return null;
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function atualizarBairros() {
  const city = document.getElementById("filter-city").value;
  const neighSelect = document.getElementById("filter-neighborhood");

  neighSelect.innerHTML = '<option value="">Todos os bairros</option>';

  if (city && DICIONARIO_BAIRROS[city]) {
    const bairros = DICIONARIO_BAIRROS[city].sort();
    bairros.forEach((bairro) => {
      neighSelect.innerHTML += `<option value="${bairro}">${bairro}</option>`;
    });
    neighSelect.disabled = false;
  } else {
    neighSelect.disabled = true;
  }
}

document
  .getElementById("filter-city")
  .addEventListener("change", atualizarBairros);

async function fetchProperties() {
  if (loading) return;
  loading = true;

  const city = document.getElementById("filter-city").value;
  const neighborhood = document.getElementById("filter-neighborhood").value;
  const bedrooms = document.getElementById("filter-bedrooms").value;
  const bathrooms = document.getElementById("filter-bathrooms").value;
  const parking = document.getElementById("filter-parking").value;
  const minPrice = document.getElementById("filter-min-price").value;
  const maxPrice = document.getElementById("filter-max-price").value;
  const minArea = document.getElementById("filter-min-area").value;
  const maxArea = document.getElementById("filter-max-area").value;

  const params = new URLSearchParams();
  if (city) params.set("city", city);
  if (neighborhood) params.set("neighborhood", neighborhood);
  if (bedrooms) params.set("min_bedrooms", bedrooms);
  if (bathrooms) params.set("min_bathrooms", bathrooms);
  if (parking) params.set("min_parking", parking);
  if (minPrice) params.set("min_price", minPrice);
  if (maxPrice) params.set("max_price", maxPrice);
  if (minArea) params.set("min_area", minArea);
  if (maxArea) params.set("max_area", maxArea);

  setStatus('<span class="loading-dot"></span> Carregando…');
  errorArea.innerHTML = "";
  renderSkeleton();
  renderFilterSummary({
    city,
    neighborhood,
    bedrooms,
    bathrooms,
    parking,
    minPrice,
    maxPrice,
    minArea,
    maxArea,
  });

  try {
    const url = `${API_BASE}/properties?${params.toString()}`;
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${resp.statusText}`);

    const rawData = await resp.json();

    allData = rawData.map((p) => {
      let price_sqm = null;
      if (p.price && p.area && p.area > 0) {
        price_sqm = p.price / p.area;
      }

      let distance = null;
      if (p.city && CITY_CENTERS[p.city] && p.latitude && p.longitude) {
        distance = calculateDistance(
          CITY_CENTERS[p.city].lat,
          CITY_CENTERS[p.city].lng,
          p.latitude,
          p.longitude,
        );
      }

      return { ...p, price_sqm, distance };
    });

    currentPage = 1;
    renderTable();
    setStatus(
      `<b>${allData.length}</b> imóve${
        allData.length === 1 ? "l" : "is"
      } encontrado${allData.length === 1 ? "" : "s"}`,
    );

    prepareGeocodingData();
    if (currentView === "map") {
      startGeocoding();
    }
  } catch (err) {
    console.error(err);
    errorArea.innerHTML = `
<div class="error-banner">
  <span class="error-icon">⚠️</span>
  <b>Erro ao buscar imóveis</b>
  <p style="margin-top: 4px;">${err.message}</p>
  <small style="margin-top: 8px; opacity: 0.8;">Verifique se a API está online em <code>${API_BASE}</code></small>
</div>`;
    setStatus("Erro ao carregar.");
    allData = [];
    tableContainer.innerHTML = "";
  } finally {
    loading = false;
  }
}

function setStatus(html) {
  statusText.innerHTML = html;
}

function renderSkeleton() {
  const rows = Array.from({ length: 6 })
    .map(
      (_, i) => `
<tr>
  <td><div class="skeleton-cell" style="width: 64px; height: 48px;"></div></td>
  <td class="title-cell">
    <div class="skeleton-cell" style="width: 90%; margin-bottom: 6px;"></div>
    <div class="skeleton-cell" style="width: 50%; height: 12px;"></div>
  </td>
  <td><div class="skeleton-cell" style="width: 70%;"></div></td>
  <td><div class="skeleton-cell" style="width: 50%;"></div></td> <td><div class="skeleton-cell" style="width: 60%;"></div></td>
  <td><div class="skeleton-cell" style="width: 40px;"></div></td>
  <td><div class="skeleton-cell" style="width: 30px;"></div></td>
  <td><div class="skeleton-cell" style="width: 30px;"></div></td>
  <td><div class="skeleton-cell" style="width: 30px;"></div></td>
  <td><div class="skeleton-cell" style="width: 50px;"></div></td>
  <td><div class="skeleton-cell" style="width: 70%;"></div></td>
  <td><div class="skeleton-cell" style="width: 70%;"></div></td>
  <td><div class="skeleton-cell" style="width: 60px; border-radius: 20px;"></div></td>
  <td><div class="skeleton-cell" style="width: 40px;"></div></td>
</tr>
`,
    )
    .join("");

  const headCells = COLUMNS.map((col) => `<th>${col.label}</th>`).join("");

  tableContainer.innerHTML = `
<table>
<thead><tr>${headCells}</tr></thead>
<tbody>${rows}</tbody>
</table>`;

  paginationEl.innerHTML = "";
}

function fmtCondoFee(v) {
  if (v == null || v === 0) return '<span class="null-dash">—</span>';
  return `<span style="color: var(--ink-muted); font-size: 0.85rem;">R$ ${Number(
    v,
  ).toLocaleString("pt-BR", {
    maximumFractionDigits: 0,
  })}</span>`;
}

function renderFilterSummary({
  city,
  neighborhood,
  bedrooms,
  bathrooms,
  parking,
  minPrice,
  maxPrice,
  minArea,
  maxArea,
}) {
  const pills = [];
  if (city) pills.push(`📍 ${city}`);
  if (neighborhood) pills.push(`🏘️ ${neighborhood}`);
  if (maxPrice)
    pills.push(`💰 até R$ ${Number(maxPrice).toLocaleString("pt-BR")}`);
  if (minPrice)
    pills.push(`💰 mín. R$ ${Number(minPrice).toLocaleString("pt-BR")}`);
  if (bedrooms) pills.push(`🛏 ${bedrooms}+ quartos`);
  if (bathrooms) pills.push(`🚿 ${bathrooms}+ banheiros`);
  if (parking) pills.push(`🅿️ ${parking}+ vagas`);
  if (minArea) pills.push(`📐 mín. ${minArea} m²`);
  if (maxArea) pills.push(`📐 máx. ${maxArea} m²`);

  if (pills.length === 0) {
    filterSummaryEl.style.display = "none";
    return;
  }
  filterSummaryEl.style.display = "flex";
  filterSummaryEl.innerHTML =
    `<span>Filtros ativos:</span>` +
    pills.map((p) => `<span class="filter-pill">${p}</span>`).join("");
}

function sortData(data) {
  const d = [...data];

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

  d.sort((a, b) => {
    let av = a[sortKey];
    let bv = b[sortKey];

    if (av == null && bv == null) return 0;
    if (av == null) return 1;
    if (bv == null) return -1;

    if (numericKeys.includes(sortKey)) {
      return sortDir === "asc" ? av - bv : bv - av;
    }

    if (typeof av === "string") av = av.toLowerCase();
    if (typeof bv === "string") bv = bv.toLowerCase();

    if (av < bv) return sortDir === "asc" ? -1 : 1;
    if (av > bv) return sortDir === "asc" ? 1 : -1;
    return 0;
  });

  return d;
}

function setSort(key) {
  if (sortKey === key) {
    sortDir = sortDir === "asc" ? "desc" : "asc";
  } else {
    sortKey = key;
    sortDir = "asc";
  }
  currentPage = 1;
  renderTable();
}

function fmtPrice(v) {
  if (v == null) return '<span class="price-null">—</span>';
  return `<span class="price">R$ ${Number(v).toLocaleString("pt-BR", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  })}</span>`;
}

function fmtArea(v) {
  if (v == null) return '<span class="null-dash">—</span>';
  return `${Number(v).toLocaleString("pt-BR", {
    maximumFractionDigits: 0,
  })} m²`;
}

function fmtInt(v) {
  if (v == null) return '<span class="null-dash">—</span>';
  return `${v}`;
}

const COLUMNS = [
  { key: "image_url", label: "Imagem", sortable: false },
  { key: "title", label: "Imóvel", sortable: false },
  { key: "price", label: "Preço", sortable: true },
  { key: "condo_fee", label: "Condomínio", sortable: true },
  { key: "price_sqm", label: "R$/m²", sortable: true },
  { key: "area", label: "Área", sortable: true },
  { key: "bedrooms", label: "Quartos", sortable: true },
  { key: "bathrooms", label: "Banheiros", sortable: true },
  { key: "parking", label: "Vagas", sortable: true },
  { key: "distance", label: "Dist. Centro", sortable: true },
  { key: "neighborhood", label: "Bairro", sortable: true },
  { key: "city", label: "Cidade", sortable: true },
  { key: "agency", label: "Imobiliária", sortable: true },
  { key: "_link", label: "Ver", sortable: false },
];

function fmtPriceSqm(v) {
  if (v == null) return '<span class="null-dash">—</span>';
  return `R$ ${Number(v).toLocaleString("pt-BR", {
    maximumFractionDigits: 0,
  })}/m²`;
}

function fmtDistance(v) {
  if (v == null) return '<span class="null-dash">—</span>';
  return `${Number(v).toFixed(1)} km`;
}

function fmtImage(url) {
  if (!url) {
    return '<div style="width:64px;height:48px;background:#e8e4dc;border-radius:4px;display:flex;align-items:center;justify-content:center;color:#a89f93;font-size:0.6rem;text-transform:uppercase;">Sem foto</div>';
  }
  return `<img src="${esc(
    url,
  )}" alt="Miniatura" loading="lazy" class="clickable-img" onclick="openModal('${esc(
    url,
  )}')" style="width:64px;height:48px;object-fit:cover;border-radius:4px;box-shadow:0 1px 3px rgba(0,0,0,0.1);">`;
}

function renderTable() {
  const sorted = sortData(allData);
  const totalPages = Math.ceil(sorted.length / PAGE_SIZE) || 1;
  if (currentPage > totalPages) currentPage = totalPages;

  const start = (currentPage - 1) * PAGE_SIZE;
  const pageData = sorted.slice(start, start + PAGE_SIZE);

  if (sorted.length === 0) {
    tableContainer.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🏠</div>
        <div class="big">Nenhum imóvel encontrado</div>
        <p>Não encontrámos propriedades que correspondam aos teus critérios.</p>
        <button class="btn btn-ghost" style="margin: 1.5rem auto 0;" onclick="document.getElementById('btn-clear').click()">Limpar Filtros</button>
      </div>`;
    paginationEl.innerHTML = "";
    return;
  }

  const headCells = COLUMNS.map((col) => {
    let cls = col.sortable ? "sortable" : "";
    if (col.sortable && sortKey === col.key)
      cls += sortDir === "asc" ? " sort-asc" : " sort-desc";
    const click = col.sortable ? `onclick="setSort('${col.key}')"` : "";
    return `<th class="${cls}" ${click}>${col.label}${
      col.sortable ? '<span class="sort-icon"></span>' : ""
    }</th>`;
  }).join("");

  const rows = pageData
    .map((p, i) => {
      const delay = i * 15 + "ms";

      let agencyHtml = `<span class="badge">${esc(p.agency)}</span>`;
      let actionHtml = `<a class="link" href="${esc(
        p.url,
      )}" target="_blank" rel="noopener">Ver →</a>`;

      if (p.source_links && p.source_links.length > 1) {
        agencyHtml = `<span class="badge" style="background: var(--green); color: white; border: none;">Listado em ${p.source_links.length} imobiliárias</span>`;
        const encodedLinks = encodeURIComponent(JSON.stringify(p.source_links));
        actionHtml = `<button class="btn btn-ghost" style="height: 26px; padding: 0 10px; font-size: 0.75rem;" onclick="openSourcesModal('${encodedLinks}')">Ver links</button>`;
      }

      return `<tr style="animation-delay:${delay}">
    <td>${fmtImage(p.image_url)}</td> 
    <td class="title-cell">
      <div class="listing-title">${esc(p.title || "–")}</div>
      <div class="listing-agency">${esc(p.agency)}</div>
    </td>
    <td>${fmtPrice(p.price)}</td>
    <td>${fmtCondoFee(p.condo_fee)}</td> <td>${fmtPriceSqm(p.price_sqm)}</td>
    <td>${fmtPriceSqm(p.price_sqm)}</td> 
    <td>${fmtArea(p.area)}</td>
    <td>${fmtInt(p.bedrooms)}</td>
    <td>${fmtInt(p.bathrooms)}</td>
    <td>${fmtInt(p.parking)}</td>
    <td>${fmtDistance(p.distance)}</td> 
    <td>${
      p.neighborhood
        ? `<span class="tag">${esc(p.neighborhood)}</span>`
        : '<span class="null-dash">—</span>'
    }</td>
    <td>${p.city ? esc(p.city) : '<span class="null-dash">—</span>'}</td>
    <td>${agencyHtml}</td>
    <td>${actionHtml}</td>
  </tr>`;
    })
    .join("");

  tableContainer.innerHTML = `
    <table>
      <thead><tr>${headCells}</tr></thead>
      <tbody>${rows}</tbody>
    </table>`;

  renderPagination(totalPages);
}

function renderPagination(totalPages) {
  if (totalPages <= 1) {
    paginationEl.innerHTML = "";
    return;
  }
  let html = `<button class="page-btn" ${
    currentPage === 1 ? "disabled" : ""
  } onclick="goPage(${currentPage - 1})">‹</button>`;
  const range = [];
  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || Math.abs(i - currentPage) <= 2)
      range.push(i);
    else if (range[range.length - 1] !== "…") range.push("…");
  }
  range.forEach((p) => {
    if (p === "…")
      html += `<span style="padding:0 4px;color:var(--ink-muted)">…</span>`;
    else
      html += `<button class="page-btn ${
        p === currentPage ? "active" : ""
      }" onclick="goPage(${p})">${p}</button>`;
  });
  html += `<button class="page-btn" ${
    currentPage === totalPages ? "disabled" : ""
  } onclick="goPage(${currentPage + 1})">›</button>`;
  paginationEl.innerHTML = html;
}

function goPage(n) {
  const totalPages = Math.ceil(allData.length / PAGE_SIZE) || 1;

  if (n < 1) n = 1;
  if (n > totalPages) n = totalPages;

  if (currentPage === n) return;

  currentPage = n;
  renderTable();

  const tableWrap = document.querySelector(".table-wrap");
  if (tableWrap) {
    window.scrollTo({
      top: tableWrap.offsetTop - 60,
      behavior: "smooth",
    });
  }
}

function openModal(url) {
  const modal = document.getElementById("image-modal");
  const modalImg = document.getElementById("modal-img");
  modal.style.display = "flex";
  modalImg.src = url;
}

function closeModal() {
  document.getElementById("image-modal").style.display = "none";
  document.getElementById("modal-img").src = "";
}

window.addEventListener("click", function (event) {
  const modal = document.getElementById("image-modal");
  if (event.target === modal) {
    closeModal();
  }
});

window.addEventListener("keydown", function (event) {
  if (event.key === "Escape") closeModal();
});

function esc(s) {
  if (!s) return "";
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

const DEFAULTS = {
  city: "Tubarão",
  neighborhood: "",
  minPrice: "",
  maxPrice: "320000",
  bedrooms: "1",
  bathrooms: "1",
  parking: "1",
  minArea: "50",
  maxArea: "",
};

function openSourcesModal(encodedLinks) {
  const links = JSON.parse(decodeURIComponent(encodedLinks));
  const container = document.getElementById("sources-list");

  container.innerHTML = links
    .map((l) => {
      const priceFmt = l.price
        ? `R$ ${Number(l.price).toLocaleString("pt-BR")}`
        : "Preço sob consulta";
      return `
      <div style="padding: 1rem; background: var(--bg); border: 1px solid var(--border); border-radius: 6px; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <strong style="display: block; font-size: 0.95rem; text-transform: capitalize;">${esc(
            l.agency,
          )}</strong>
          <span style="color: var(--green); font-size: 0.85rem; font-weight: 500;">${priceFmt}</span>
        </div>
        <a href="${esc(
          l.url,
        )}" target="_blank" class="btn btn-primary" style="text-decoration: none; font-size: 0.8rem; padding: 0 1.2rem; height: 32px;">Acessar</a>
      </div>
    `;
    })
    .join("");

  document.getElementById("sources-modal").style.display = "flex";
}

function closeSourcesModal() {
  document.getElementById("sources-modal").style.display = "none";
}

window.addEventListener("click", function (event) {
  const imgModal = document.getElementById("image-modal");
  const srcModal = document.getElementById("sources-modal");
  if (event.target === imgModal) closeModal();
  if (event.target === srcModal) closeSourcesModal();
});

window.addEventListener("keydown", function (event) {
  if (event.key === "Escape") {
    closeModal();
    closeSourcesModal();
  }
});

function applyDefaults() {
  document.getElementById("filter-city").value = DEFAULTS.city;
  atualizarBairros();
  document.getElementById("filter-neighborhood").value = DEFAULTS.neighborhood;
  document.getElementById("filter-min-price").value = DEFAULTS.minPrice;
  document.getElementById("filter-max-price").value = DEFAULTS.maxPrice;
  document.getElementById("filter-bedrooms").value = DEFAULTS.bedrooms;
  document.getElementById("filter-bathrooms").value = DEFAULTS.bathrooms;
  document.getElementById("filter-parking").value = DEFAULTS.parking;
  document.getElementById("filter-min-area").value = DEFAULTS.minArea;
  document.getElementById("filter-max-area").value = DEFAULTS.maxArea;
}

document
  .getElementById("btn-search")
  .addEventListener("click", fetchProperties);

document.getElementById("btn-clear").addEventListener("click", () => {
  applyDefaults();
  fetchProperties();
});

document.querySelectorAll("#controls input, #controls select").forEach((el) => {
  el.addEventListener("keydown", (e) => {
    if (e.key === "Enter") fetchProperties();
  });
});

applyDefaults();
atualizarBairros();
fetchProperties();
