const API_BASE = "https://imobiliarias.onrender.com";
const PAGE_SIZE = 30;

let allData = [];
let sortKey = "price";
let sortDir = "asc";
let currentPage = 1;
let loading = false;

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
    allData = await resp.json();
    currentPage = 1;
    renderTable();
    setStatus(
      `<b>${allData.length}</b> imóve${
        allData.length === 1 ? "l" : "is"
      } encontrado${allData.length === 1 ? "" : "s"}`,
    );
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
<td><div class="skeleton-cell" style="width: 60%;"></div></td>
<td><div class="skeleton-cell" style="width: 40px;"></div></td>
<td><div class="skeleton-cell" style="width: 40px;"></div></td>
<td><div class="skeleton-cell" style="width: 40px;"></div></td>
<td><div class="skeleton-cell" style="width: 80%;"></div></td>
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

  const numericKeys = ["price", "area", "bedrooms", "bathrooms", "parking"];

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
  { key: "area", label: "Área", sortable: true },
  { key: "bedrooms", label: "Quartos", sortable: true },
  { key: "bathrooms", label: "Banheiros", sortable: true },
  { key: "parking", label: "Vagas", sortable: true },
  { key: "neighborhood", label: "Bairro", sortable: true },
  { key: "city", label: "Cidade", sortable: true },
  { key: "agency", label: "Imobiliária", sortable: true },
  { key: "_link", label: "Ver", sortable: false },
];

function fmtImage(url) {
  if (!url) {
    return '<div style="width:64px;height:48px;background:#e8e4dc;border-radius:4px;display:flex;align-items:center;justify-content:center;color:#a89f93;font-size:0.6rem;text-transform:uppercase;">Sem foto</div>';
  }
  return `<img src="${esc(
    url,
  )}" alt="Miniatura" loading="lazy" style="width:64px;height:48px;object-fit:cover;border-radius:4px;box-shadow:0 1px 3px rgba(0,0,0,0.1);">`;
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
      return `<tr style="animation-delay:${delay}">
      <td>${fmtImage(p.image_url)}</td> <td class="title-cell">
        <div class="listing-title">${esc(p.title || "–")}</div>
        <div class="listing-agency">${esc(p.agency)}</div>
      </td>
      <td>${fmtPrice(p.price)}</td>
      <td>${fmtArea(p.area)}</td>
      <td>${fmtInt(p.bedrooms)}</td>
      <td>${fmtInt(p.bathrooms)}</td>
      <td>${fmtInt(p.parking)}</td>
      <td>${
        p.neighborhood
          ? `<span class="tag">${esc(p.neighborhood)}</span>`
          : '<span class="null-dash">—</span>'
      }</td>
      <td>${p.city ? esc(p.city) : '<span class="null-dash">—</span>'}</td>
      <td><span class="badge">${esc(p.agency)}</span></td>
      <td><a class="link" href="${esc(
        p.url,
      )}" target="_blank" rel="noopener">Ver →</a></td>
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
