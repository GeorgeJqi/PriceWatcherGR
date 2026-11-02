/**
 * PriceWatcher GR - Frontend Application Logic (Dark Theme Main)
 */

// Global State
const state = {
  currentQuery: "",
  results: [],
  sourcesStatus: [],
  lastUpdated: null,
  executionTime: 0,
  isLoading: false,
  viewMode: "grid", // "grid" | "list"
  filters: {
    platform: "all",
    location: "all",
    minPrice: null,
    maxPrice: null,
    onlyClearPrice: false,
    sortBy: "price_asc"
  }
};

// DOM Elements
const searchForm = document.getElementById("search-form");
const searchInput = document.getElementById("search-input");
const searchButton = document.getElementById("search-button");
const btnSearchText = document.getElementById("btn-search-text");
const btnSearchSpinner = document.getElementById("btn-search-spinner");

const controlsSection = document.getElementById("controls-section");
const filterPlatform = document.getElementById("filter-platform");
const filterLocation = document.getElementById("filter-location");
const filterMinPrice = document.getElementById("filter-min-price");
const filterMaxPrice = document.getElementById("filter-max-price");
const filterSort = document.getElementById("filter-sort");
const filterOnlyClear = document.getElementById("filter-only-clear");
const btnApplyFilters = document.getElementById("btn-apply-filters");
const btnResetFilters = document.getElementById("btn-reset-filters");

const resultsHeader = document.getElementById("results-header");
const resultsTitle = document.getElementById("results-title");
const resultsMeta = document.getElementById("results-meta");
const sourceBadgesContainer = document.getElementById("source-badges");

const welcomeState = document.getElementById("welcome-state");
const loadingState = document.getElementById("loading-state");
const noResultsState = document.getElementById("no-results-state");
const listingsContainer = document.getElementById("listings-container");

const btnViewGrid = document.getElementById("btn-view-grid");
const btnViewList = document.getElementById("btn-view-list");

// Direct Links
const linkInsomnia = document.getElementById("link-insomnia");
const linkVendora = document.getElementById("link-vendora");
const linkZer = document.getElementById("link-zer");
const linkEbyte = document.getElementById("link-ebyte");
const linkPcarena = document.getElementById("link-pcarena");
const linkFacebook = document.getElementById("link-facebook");

// Modals
const modalSources = document.getElementById("modal-sources");
const btnSourcesModal = document.getElementById("btn-sources-modal");
const btnCloseSourcesModal = document.getElementById("btn-close-sources-modal");
const btnCloseSourcesModal2 = document.getElementById("btn-close-sources-modal-2");
const sourcesAuditContent = document.getElementById("sources-audit-content");

const modalManual = document.getElementById("modal-manual");
const btnManualModal = document.getElementById("btn-manual-modal");
const btnCloseManualModal = document.getElementById("btn-close-manual-modal");
const btnCancelManual = document.getElementById("btn-cancel-manual");
const manualAdForm = document.getElementById("manual-ad-form");

// Init
document.addEventListener("DOMContentLoaded", () => {
  initIcons();
  setupEventListeners();
  updateDirectLinks("");
  loadSourcesAudit();
});

function initIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function setupEventListeners() {
  // Search Form Submit
  searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const query = searchInput.value.trim();
    if (query) {
      performSearch(query);
    }
  });

  // Dynamic direct link updates as user types
  searchInput.addEventListener("input", (e) => {
    updateDirectLinks(e.target.value.trim());
  });

  // Quick Tags
  document.querySelectorAll(".quick-tag").forEach((btn) => {
    btn.addEventListener("click", () => {
      const tag = btn.dataset.tag;
      searchInput.value = tag;
      updateDirectLinks(tag);
      performSearch(tag);
    });
  });

  // Apply filters button
  btnApplyFilters.addEventListener("click", () => {
    readFiltersFromUI();
    renderFilteredResults();
  });

  // Reset Filters
  btnResetFilters.addEventListener("click", () => {
    resetFilters();
  });

  // Instant filter auto-update on changes (no manual "Apply" required!)
  filterSort.addEventListener("change", () => {
    state.filters.sortBy = filterSort.value;
    renderFilteredResults();
  });

  filterPlatform.addEventListener("change", () => {
    state.filters.platform = filterPlatform.value;
    renderFilteredResults();
  });

  filterLocation.addEventListener("change", () => {
    state.filters.location = filterLocation.value;
    renderFilteredResults();
  });

  filterOnlyClear.addEventListener("change", () => {
    state.filters.onlyClearPrice = filterOnlyClear.checked;
    renderFilteredResults();
  });

  filterMinPrice.addEventListener("input", () => {
    state.filters.minPrice = filterMinPrice.value ? parseFloat(filterMinPrice.value) : null;
    renderFilteredResults();
  });

  filterMaxPrice.addEventListener("input", () => {
    state.filters.maxPrice = filterMaxPrice.value ? parseFloat(filterMaxPrice.value) : null;
    renderFilteredResults();
  });

  // View Mode Toggles
  btnViewGrid.addEventListener("click", () => setViewMode("grid"));
  btnViewList.addEventListener("click", () => setViewMode("list"));

  // Modals Toggles
  btnSourcesModal.addEventListener("click", () => openModal(modalSources));
  btnCloseSourcesModal.addEventListener("click", () => closeModal(modalSources));
  btnCloseSourcesModal2.addEventListener("click", () => closeModal(modalSources));

  btnManualModal.addEventListener("click", () => openModal(modalManual));
  btnCloseManualModal.addEventListener("click", () => closeModal(modalManual));
  btnCancelManual.addEventListener("click", () => closeModal(modalManual));

  // Modal Backdrop Click
  modalSources.addEventListener("click", (e) => {
    if (e.target === modalSources) closeModal(modalSources);
  });
  modalManual.addEventListener("click", (e) => {
    if (e.target === modalManual) closeModal(modalManual);
  });

  // Manual Ad Form Submit
  manualAdForm.addEventListener("submit", handleManualAdSubmit);
}

function updateDirectLinks(query) {
  const q = encodeURIComponent(query);
  linkInsomnia.href = query ? `https://www.insomnia.gr/classifieds/search/?q=${q}` : "https://www.insomnia.gr/classifieds/";
  linkVendora.href = query ? `https://vendora.gr/items?q=${q}` : "https://vendora.gr/";
  linkZer.href = query ? `https://www.zer.gr/index.php?act=viewCat&keywords=${q}` : "https://www.zer.gr/";
  linkEbyte.href = query ? `https://e-byte.gr/?s=${q}&post_type=product` : "https://e-byte.gr/";
  linkPcarena.href = query ? `https://www.pcarena.gr/index.php?route=product/search&search=${q}` : "https://www.pcarena.gr/";
  linkFacebook.href = query ? `https://www.facebook.com/marketplace/search/?query=${q}` : "https://www.facebook.com/marketplace/";
}

function openModal(modal) {
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  initIcons();
}

function closeModal(modal) {
  modal.classList.add("hidden");
  modal.classList.remove("flex");
}

function setViewMode(mode) {
  state.viewMode = mode;
  if (mode === "grid") {
    btnViewGrid.className = "p-1.5 rounded-lg bg-blue-600/30 border border-blue-500/50 text-blue-400";
    btnViewList.className = "p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white border border-slate-700";
    listingsContainer.className = "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4";
  } else {
    btnViewGrid.className = "p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white border border-slate-700";
    btnViewList.className = "p-1.5 rounded-lg bg-blue-600/30 border border-blue-500/50 text-blue-400";
    listingsContainer.className = "flex flex-col space-y-3";
  }
  renderFilteredResults();
}

function readFiltersFromUI() {
  state.filters.platform = filterPlatform.value;
  state.filters.location = filterLocation.value;
  state.filters.minPrice = filterMinPrice.value ? parseFloat(filterMinPrice.value) : null;
  state.filters.maxPrice = filterMaxPrice.value ? parseFloat(filterMaxPrice.value) : null;
  state.filters.onlyClearPrice = filterOnlyClear.checked;
  state.filters.sortBy = filterSort.value;
}

function resetFilters() {
  filterPlatform.value = "all";
  filterLocation.value = "all";
  filterMinPrice.value = "";
  filterMaxPrice.value = "";
  filterOnlyClear.checked = false;
  filterSort.value = "price_asc";
  readFiltersFromUI();
  renderFilteredResults();
}

function resetSearch() {
  searchInput.value = "";
  state.currentQuery = "";
  state.results = [];
  welcomeState.classList.remove("hidden");
  resultsHeader.classList.add("hidden");
  noResultsState.classList.add("hidden");
  listingsContainer.innerHTML = "";
  updateDirectLinks("");
}

async function performSearch(query) {
  state.currentQuery = query;
  state.isLoading = true;

  welcomeState.classList.add("hidden");
  noResultsState.classList.add("hidden");
  resultsHeader.classList.add("hidden");
  listingsContainer.innerHTML = "";
  loadingState.classList.remove("hidden");

  btnSearchText.classList.add("hidden");
  btnSearchSpinner.classList.remove("hidden");
  searchButton.disabled = true;

  try {
    const params = new URLSearchParams({
      q: query,
      sort: state.filters.sortBy
    });

    const resp = await fetch(`/api/search?${params.toString()}`);
    if (!resp.ok) {
      throw new Error(`HTTP Error: ${resp.status}`);
    }

    const data = await resp.json();
    state.results = data.results || [];
    state.sourcesStatus = data.sources_status || [];
    state.executionTime = data.execution_time_seconds || 0;
    state.lastUpdated = new Date();

    // Reset loading state IMMEDIATELY so results render on arrival
    state.isLoading = false;
    loadingState.classList.add("hidden");

    renderFilteredResults();
    renderSourceBadges();
  } catch (err) {
    console.error("Search failed:", err);
    alert("Παρουσιάστηκε σφάλμα κατά την αναζήτηση. Παρακαλώ δοκιμάστε ξανά.");
  } finally {
    state.isLoading = false;
    loadingState.classList.add("hidden");
    btnSearchText.classList.remove("hidden");
    btnSearchSpinner.classList.add("hidden");
    searchButton.disabled = false;
  }
}

function renderSourceBadges() {
  sourceBadgesContainer.innerHTML = "";
  const countsByPlatform = {};
  state.results.forEach((r) => {
    countsByPlatform[r.platform] = (countsByPlatform[r.platform] || 0) + 1;
  });

  const platformNames = {
    insomnia: "Insomnia",
    vendora: "Vendora",
    zer: "ZER Shop",
    ebyte: "E-Byte",
    pcarena: "PC Arena",
    facebook: "Facebook",
    facebook_manual: "FB Manual"
  };

  Object.entries(countsByPlatform).forEach(([plat, count]) => {
    const badge = document.createElement("span");
    badge.className = `px-2 py-0.5 rounded-full border text-[11px] font-semibold badge-${plat.replace("_manual", "")}`;
    badge.textContent = `${platformNames[plat] || plat}: ${count}`;
    sourceBadgesContainer.appendChild(badge);
  });
}

function renderFilteredResults() {
  const f = state.filters;
  let items = [...state.results];

  // Filter: Platform
  if (f.platform !== "all") {
    if (f.platform === "facebook") {
      items = items.filter((i) => i.platform.startsWith("facebook"));
    } else {
      items = items.filter((i) => i.platform === f.platform);
    }
  }

  // Filter: Location
  if (f.location !== "all") {
    const locLower = f.location.toLowerCase();
    items = items.filter((i) => i.location && i.location.toLowerCase().includes(locLower));
  }

  // Filter: Min Price
  if (f.minPrice !== null && !isNaN(f.minPrice)) {
    items = items.filter((i) => i.price !== null && i.price >= f.minPrice);
  }

  // Filter: Max Price
  if (f.maxPrice !== null && !isNaN(f.maxPrice)) {
    items = items.filter((i) => i.price !== null && i.price <= f.maxPrice);
  }

  // Filter: Only Clear Price
  if (f.onlyClearPrice) {
    items = items.filter((i) => i.is_price_clear && i.price !== null);
  }

  // Sort
  if (f.sortBy === "price_asc") {
    items.sort((a, b) => {
      if (a.price === null) return 1;
      if (b.price === null) return -1;
      return a.price - b.price;
    });
  } else if (f.sortBy === "price_desc") {
    items.sort((a, b) => {
      if (a.price === null) return 1;
      if (b.price === null) return -1;
      return b.price - a.price;
    });
  } else if (f.sortBy === "newest") {
    items.sort((a, b) => new Date(b.last_updated) - new Date(a.last_updated));
  }

  // Render UI states
  if (items.length === 0) {
    noResultsState.classList.remove("hidden");
    resultsHeader.classList.add("hidden");
    listingsContainer.innerHTML = "";
    return;
  }

  noResultsState.classList.add("hidden");
  resultsHeader.classList.remove("hidden");

  const updatedStr = state.lastUpdated
    ? state.lastUpdated.toLocaleTimeString("el-GR", { hour: "2-digit", minute: "2-digit", second: "2-digit" })
    : "";

  resultsTitle.textContent = `Αποτελέσματα για «${state.currentQuery}»`;
  resultsMeta.textContent = `Βρέθηκαν ${items.length} αγγελίες (από ${state.results.length} σύνολο) σε ${state.executionTime}s • Τελευταία ενημέρωση: ${updatedStr}`;

  listingsContainer.innerHTML = "";

  if (state.viewMode === "grid") {
    items.forEach((item, index) => {
      listingsContainer.appendChild(createGridCard(item, index === 0 && item.price !== null));
    });
  } else {
    items.forEach((item, index) => {
      listingsContainer.appendChild(createListCard(item, index === 0 && item.price !== null));
    });
  }

  initIcons();
}

function getPlatformBadgeClass(platform) {
  if (platform.includes("insomnia")) return "badge-insomnia";
  if (platform.includes("vendora")) return "badge-vendora";
  if (platform.includes("zer")) return "badge-zer";
  if (platform.includes("ebyte")) return "badge-ebyte";
  if (platform.includes("pcarena")) return "badge-pcarena";
  return "badge-facebook";
}

function createGridCard(item, isLowestPrice) {
  const card = document.createElement("div");
  card.className = "listing-card rounded-2xl overflow-hidden flex flex-col relative";

  const badgeClass = getPlatformBadgeClass(item.platform);
  const fallbackImg = `https://placehold.co/400x300/0b0f19/94a3b8?text=${encodeURIComponent(item.platform_name)}`;
  const imgUrl = item.image_url || fallbackImg;

  card.innerHTML = `
    <!-- Image Box -->
    <div class="relative w-full h-44 bg-white/[0.015] overflow-hidden group border-b border-white/[0.06]">
      <img
        src="${escapeHtml(imgUrl)}"
        alt="${escapeHtml(item.title)}"
        loading="lazy"
        onerror="this.src='${fallbackImg}'"
        class="w-full h-full object-contain p-2.5 group-hover:scale-105 transition-transform duration-300"
      />
      <!-- Platform Badge -->
      <span class="absolute top-2.5 left-2.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold tracking-wide ${badgeClass} backdrop-blur-md">
        ${escapeHtml(item.platform_name)}
      </span>

      ${
        isLowestPrice
          ? `<span class="absolute top-2.5 right-2.5 bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 text-[10px] font-semibold px-2 py-0.5 rounded-full backdrop-blur-md flex items-center space-x-1">
              <span>Χαμηλότερη τιμή</span>
            </span>`
          : ""
      }
    </div>

    <!-- Body Content -->
    <div class="p-4 flex-1 flex flex-col">
      <!-- Price -->
      <div class="mb-2 flex items-baseline justify-between">
        <span class="text-xl font-bold tracking-tight ${item.is_price_clear ? "text-white" : "text-amber-300"}">
          ${escapeHtml(item.price_formatted)}
        </span>
        ${
          item.is_price_clear
            ? '<span class="text-[10px] text-slate-500 font-normal">σε ευρώ (€)</span>'
            : '<span class="text-[10px] bg-amber-500/10 text-amber-300 border border-amber-500/20 px-1.5 py-0.5 rounded font-normal">Ζήτηση / Έλεγχος</span>'
        }
      </div>

      <!-- Title -->
      <h3 class="text-sm font-semibold text-slate-200 line-clamp-2 hover:text-white transition-colors mb-2 leading-snug" title="${escapeHtml(item.title)}">
        <a href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer">
          ${escapeHtml(item.title)}
        </a>
      </h3>

      <!-- Description / Snippet -->
      <p class="text-xs text-slate-400 line-clamp-2 mb-4 flex-1">
        ${escapeHtml(item.description || "Δεν υπάρχει πρόσθετη περιγραφή.")}
      </p>

      <!-- Meta Info: Location & Date -->
      <div class="pt-3 border-t border-white/[0.06] text-[11px] text-slate-400 space-y-1.5 mb-3.5">
        <div class="flex items-center space-x-1.5">
          <i data-lucide="map-pin" class="w-3.5 h-3.5 text-slate-500 shrink-0"></i>
          <span class="truncate">${escapeHtml(item.location || "Πανελλαδικά")}</span>
        </div>
        ${
          item.date_published
            ? `<div class="flex items-center space-x-1.5">
                <i data-lucide="clock" class="w-3.5 h-3.5 text-slate-500 shrink-0"></i>
                <span class="truncate">${escapeHtml(item.date_published)}</span>
              </div>`
            : ""
        }
      </div>

      <!-- Human-Crafted CTA Button (Inverts smoothly on hover) -->
      <a
        href="${escapeHtml(item.url)}"
        target="_blank"
        rel="noopener noreferrer"
        class="btn-card-action w-full py-2.5 px-3 rounded-xl flex items-center justify-center space-x-1.5 group"
      >
        <span>Μετάβαση στην αγγελία</span>
        <i data-lucide="arrow-up-right" class="w-3.5 h-3.5 text-slate-400 group-hover:text-black transition-colors"></i>
      </a>
    </div>
  `;

  return card;
}

function createListCard(item, isLowestPrice) {
  const card = document.createElement("div");
  card.className = "listing-card rounded-2xl p-4 flex flex-col sm:flex-row items-center gap-4 relative";

  const badgeClass = getPlatformBadgeClass(item.platform);
  const fallbackImg = `https://placehold.co/200x200/0b0f19/94a3b8?text=${encodeURIComponent(item.platform_name)}`;
  const imgUrl = item.image_url || fallbackImg;

  card.innerHTML = `
    <!-- Thumbnail -->
    <div class="w-full sm:w-36 h-32 bg-white/[0.015] rounded-xl overflow-hidden shrink-0 relative border border-white/[0.06]">
      <img
        src="${escapeHtml(imgUrl)}"
        alt="${escapeHtml(item.title)}"
        loading="lazy"
        onerror="this.src='${fallbackImg}'"
        class="w-full h-full object-contain p-2"
      />
      <span class="absolute top-2 left-2 px-2 py-0.5 rounded-full text-[10px] font-semibold ${badgeClass}">
        ${escapeHtml(item.platform_name)}
      </span>
    </div>

    <!-- Center Info -->
    <div class="flex-1 min-w-0 w-full">
      <div class="flex items-center space-x-2 mb-1">
        ${
          isLowestPrice
            ? '<span class="bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 text-[10px] font-semibold px-2 py-0.5 rounded-full">Χαμηλότερη τιμή</span>'
            : ""
        }
        <div class="text-[11px] text-slate-400 flex items-center space-x-1">
          <i data-lucide="map-pin" class="w-3 h-3 text-slate-500"></i>
          <span>${escapeHtml(item.location || "Πανελλαδικά")}</span>
        </div>
      </div>

      <h3 class="text-sm font-semibold text-white truncate mb-1 hover:text-slate-200 transition-colors">
        <a href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer">
          ${escapeHtml(item.title)}
        </a>
      </h3>

      <p class="text-xs text-slate-400 line-clamp-2 mb-2">
        ${escapeHtml(item.description || "Δεν υπάρχει πρόσθετη περιγραφή.")}
      </p>

      ${
        item.date_published
          ? `<span class="text-[11px] text-slate-500 flex items-center space-x-1">
              <i data-lucide="clock" class="w-3 h-3"></i>
              <span>${escapeHtml(item.date_published)}</span>
            </span>`
          : ""
      }
    </div>

    <!-- Right Side Price & Action -->
    <div class="sm:text-right shrink-0 w-full sm:w-44 flex sm:flex-col items-center sm:items-end justify-between sm:justify-center border-t sm:border-t-0 pt-3 sm:pt-0 border-white/[0.06]">
      <div class="mb-2">
        <div class="text-xl font-bold tracking-tight ${item.is_price_clear ? "text-white" : "text-amber-300"}">
          ${escapeHtml(item.price_formatted)}
        </div>
        <div class="text-[10px] text-slate-500">
          ${item.is_price_clear ? "σε ευρώ (€)" : "απαιτεί έλεγχο"}
        </div>
      </div>

      <a
        href="${escapeHtml(item.url)}"
        target="_blank"
        rel="noopener noreferrer"
        class="btn-card-action py-2 px-4 rounded-xl flex items-center space-x-1.5 group"
      >
        <span>Προβολή</span>
        <i data-lucide="arrow-up-right" class="w-3.5 h-3.5 text-slate-400 group-hover:text-black transition-colors"></i>
      </a>
    </div>
  `;

  return card;
}

async function loadSourcesAudit() {
  try {
    const resp = await fetch("/api/sources");
    if (!resp.ok) return;
    const sources = await resp.json();
    state.sourcesStatus = sources;

    sourcesAuditContent.innerHTML = sources
      .map((s) => {
        const isRestricted = s.status === "direct_link_only" || s.id === "facebook";
        const statusBadge = isRestricted
          ? `<span class="bg-amber-500/10 text-amber-300 border border-amber-500/25 font-medium px-2.5 py-0.5 rounded-full text-[10px]">Μόνο Άμεσος Σύνδεσμος / Login</span>`
          : `<span class="bg-emerald-500/10 text-emerald-300 border border-emerald-500/25 font-medium px-2.5 py-0.5 rounded-full text-[10px]">Επιτρεπτή Συλλογή</span>`;

        return `
          <div class="p-3.5 bg-white/[0.02] border border-white/[0.07] rounded-xl space-y-2">
            <div class="flex items-center justify-between">
              <div class="font-bold text-white text-sm flex items-center space-x-2">
                <span>${escapeHtml(s.name)}</span>
                <a href="${escapeHtml(s.base_url)}" target="_blank" rel="noopener noreferrer" class="text-slate-400 hover:text-white text-xs font-normal">
                  ${escapeHtml(s.base_url)}
                </a>
              </div>
              ${statusBadge}
            </div>

            <p class="text-slate-300 text-xs leading-relaxed">
              ${escapeHtml(s.legal_notes)}
            </p>

            <div class="pt-2 border-t border-white/[0.06] flex flex-wrap items-center justify-between text-[11px] text-slate-400 gap-2">
              <div>
                <strong class="text-slate-300">robots.txt:</strong> <code class="bg-white/[0.05] border border-white/10 px-1.5 py-0.5 rounded text-blue-300 font-mono text-[10px]">${escapeHtml(s.robots_txt_status)}</code>
              </div>
              <div>
                <strong class="text-slate-300">Επίσημο API:</strong> ${s.api_available ? "Διαθέσιμο" : "Μη διαθέσιμο / Κλειστό"}
              </div>
            </div>
          </div>
        `;
      })
      .join("");
  } catch (err) {
    console.error("Failed to load sources audit:", err);
  }
}

async function handleManualAdSubmit(e) {
  e.preventDefault();

  const title = document.getElementById("manual-title").value.trim();
  const price = document.getElementById("manual-price").value;
  const url = document.getElementById("manual-url").value.trim();
  const location = document.getElementById("manual-location").value.trim() || "Πανελλαδικά";
  const desc = document.getElementById("manual-desc").value.trim();

  if (!title || !url) {
    alert("Παρακαλώ συμπληρώστε τα υποχρεωτικά πεδία.");
    return;
  }

  try {
    const payload = {
      title,
      price: price ? parseFloat(price) : null,
      url,
      location,
      description: desc,
      platform: "facebook_manual"
    };

    const resp = await fetch("/api/manual", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Error");
    }

    const newListing = await resp.json();
    state.results.unshift(newListing);

    manualAdForm.reset();
    closeModal(modalManual);

    renderFilteredResults();
    renderSourceBadges();

    alert("Η αγγελία προστέθηκε επιτυχώς στη λίστα σύγκρισης!");
  } catch (err) {
    console.error("Manual add failed:", err);
    alert(`Σφάλμα καταχώρισης: ${err.message}`);
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
