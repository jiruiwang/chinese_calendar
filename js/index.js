(() => {
  "use strict";

  const DATA = window.CalendarIndexData;
  const tabButtons = document.querySelectorAll(".index-tab");
  const panels = document.querySelectorAll(".index-panel");
  const searchInput = document.getElementById("chronologySearch");
  const results = document.getElementById("chronologyResults");
  const count = document.getElementById("chronologyCount");
  const dynastyCards = document.getElementById("dynastyCards");
  const dynastyResults = document.getElementById("dynastyResults");
  const dynastyHeading = document.getElementById("dynastyHeading");

  function esc(value) {
    return String(value ?? "").replace(/[&<>"]/g, ch => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"
    }[ch]));
  }

  function normalize(value) {
    return String(value || "")
      .trim()
      .toLowerCase()
      .replace(/\s+/g, "")
      .replace(/吴/g, "吴")
      .replace(/黄/g, "黄");
  }

  function eraBaseName(text) {
    return String(text || "").replace(/（.*?）/g, "").replace(/\(.*?\)/g, "").trim();
  }

  function uniqueEraDetails(details) {
    const seen = new Set();
    return details.filter(item => {
      const key = eraBaseName(item.text);
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  function orderedEraDetails(record, preferredState = "") {
    const unique = uniqueEraDetails(record.eraDetails || []);
    if (!preferredState) return unique;
    return [
      ...unique.filter(item => item.state === preferredState),
      ...unique.filter(item => item.state !== preferredState)
    ];
  }

  function yearCard(record, preferredState = "") {
    let previousState = "";
    const displayDetails = orderedEraDetails(record, preferredState);
    const eras = displayDetails.length
      ? `<div class="result-eras">${displayDetails.map(item => {
          const stateLabel = item.state === previousState ? "" : item.state;
          previousState = item.state;
          return `
          <div class="result-era-line">
            <small class="result-era-state">${esc(stateLabel)}</small>
            <small class="result-era-text">${esc(item.text)}</small>
          </div>`;
        }).join("")}</div>`
      : `<div class="result-eras result-eras-empty"><small>無纪年</small></div>`;

    return `
      <a class="search-year-card" href="${record.href}">
        <div class="search-year-main">
          <strong>${record.year4}年</strong>
          <span>${esc(record.ganzhi)}</span>
          <small>西曆${esc(record.solarYear)}年</small>
        </div>
        ${eras}
      </a>`;
  }

  function renderChronology(query = "") {
    const q = normalize(query);
    const matched = DATA.years.filter(record => {
      if (!q) return true;
      const searchable = [
        record.year4,
        String(record.year),
        record.solarYear,
        record.ganzhi,
        ...record.eras,
        ...record.states
      ].map(normalize).join("|");
      return searchable.includes(q);
    });

    count.textContent = q
      ? `找到 ${matched.length} 個年份`
      : `共 ${matched.length} 個年份`;

    results.innerHTML = matched.length
      ? matched.map(yearCard).join("")
      : `<div class="no-results">沒有找到相符的紀年。可输入“0440”“0220”“庚子”“黄初元年”等。</div>`;
  }

  function renderDynastyCards() {
    dynastyCards.innerHTML = DATA.dynasties.map((dynasty, index) => {
      const rulerOptions = dynasty.rulers.length
        ? `<option value="">${esc(dynasty.allRulersLabel)}</option>` + dynasty.rulers.map(ruler =>
            `<option value="${esc(ruler.name)}">${esc(ruler.name)}</option>`
          ).join("")
        : `<option value="">暂無國君</option>`;

      return `
        <div class="dynasty-card${index === 0 ? " active" : ""}" data-dynasty="${esc(dynasty.id)}">
          <button class="dynasty-card-main" type="button" data-action="dynasty">
            <strong>${esc(dynasty.label)}</strong>
            <span>${esc(dynasty.displayRange)}，${esc(dynasty.displayCount)}</span>
            <small>${esc(dynasty.description)}</small>
          </button>
          <label class="dynasty-ruler-select">
            <span>國君</span>
            <select data-action="ruler" aria-label="${esc(dynasty.label)}國君">
              ${rulerOptions}
            </select>
          </label>
        </div>`;
    }).join("");

    dynastyCards.addEventListener("click", event => {
      const card = event.target.closest(".dynasty-card");
      if (!card) return;
      if (event.target.closest("select")) return;

      dynastyCards.querySelectorAll(".dynasty-card").forEach(item => item.classList.remove("active"));
      card.classList.add("active");
      const select = card.querySelector("select");
      if (select) select.value = "";
      renderDynasty(card.dataset.dynasty);
    });

    dynastyCards.addEventListener("change", event => {
      const select = event.target.closest('select[data-action="ruler"]');
      if (!select) return;
      const card = select.closest(".dynasty-card");
      dynastyCards.querySelectorAll(".dynasty-card").forEach(item => item.classList.remove("active"));
      card.classList.add("active");

      if (select.value) {
        renderRulerWithinDynasty(card.dataset.dynasty, select.value);
      } else {
        renderDynasty(card.dataset.dynasty);
      }
    });
  }

  function renderDynasty(id) {
    const dynasty = DATA.dynasties.find(item => item.id === id);
    if (!dynasty) return;

    dynastyHeading.innerHTML = `
      <strong>${esc(dynasty.label)}</strong>
      <span>${esc(dynasty.displayRange)}，${esc(dynasty.displayCount)}</span>`;

    const yearSet = new Set(dynasty.years);
    const records = DATA.years.filter(record => yearSet.has(record.year));
    dynastyResults.innerHTML = records.map(record => yearCard(record, dynasty.id === "東漢" ? "漢" : dynasty.id === "曹魏" ? "魏" : dynasty.id === "蜀漢" ? "漢" : dynasty.id === "孫吴" ? "吴" : "晉")).join("");
  }

  function renderRulerWithinDynasty(dynastyId, rulerName) {
    const dynasty = DATA.dynasties.find(item => item.id === dynastyId);
    const ruler = DATA.rulers.find(item => item.name === rulerName);
    if (!dynasty || !ruler) return;

    const dynastyYearSet = new Set(dynasty.years);
    const years = ruler.years.filter(year => dynastyYearSet.has(year));
    const first = Math.min(...years);
    const last = Math.max(...years);

    dynastyHeading.innerHTML = `
      <strong>${esc(dynasty.label)} · ${esc(ruler.name)}</strong>
      <span>${String(first).padStart(4, "0")}年至${String(last).padStart(4, "0")}年，凡${years.length}年</span>`;

    const yearSet = new Set(years);
    const records = DATA.years.filter(record => yearSet.has(record.year));
    dynastyResults.innerHTML = records.map(record => yearCard(record, dynasty.id === "東漢" ? "漢" : dynasty.id === "曹魏" ? "魏" : dynasty.id === "蜀漢" ? "漢" : dynasty.id === "孫吴" ? "吴" : "晉")).join("");
  }


  tabButtons.forEach(button => {
    button.addEventListener("click", () => {
      const target = button.dataset.target;
      tabButtons.forEach(item => {
        item.classList.toggle("active", item === button);
        item.setAttribute("aria-selected", item === button ? "true" : "false");
      });
      panels.forEach(panel => {
        panel.hidden = panel.id !== target;
      });
    });
  });

  searchInput.addEventListener("input", () => renderChronology(searchInput.value));
  document.getElementById("clearChronology").addEventListener("click", () => {
    searchInput.value = "";
    renderChronology();
    searchInput.focus();
  });

  renderChronology();
  renderDynastyCards();
  renderDynasty(DATA.dynasties[0].id);
})();
