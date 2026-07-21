(() => {
  "use strict";

  const DATA = window.CalendarData;
  if (!DATA) throw new Error("CalendarData 未载入");

  const AVAILABLE = {"401":{"displayYear":"0401","ganzhi":"辛酉","solarYear":"0181"},"402":{"displayYear":"0402","ganzhi":"壬戌","solarYear":"0182"},"403":{"displayYear":"0403","ganzhi":"癸亥","solarYear":"0183"},"404":{"displayYear":"0404","ganzhi":"甲子","solarYear":"0184"},"405":{"displayYear":"0405","ganzhi":"乙丑","solarYear":"0185"},"406":{"displayYear":"0406","ganzhi":"丙寅","solarYear":"0186"},"407":{"displayYear":"0407","ganzhi":"丁卯","solarYear":"0187"},"408":{"displayYear":"0408","ganzhi":"戊辰","solarYear":"0188"},"409":{"displayYear":"0409","ganzhi":"己巳","solarYear":"0189"},"410":{"displayYear":"0410","ganzhi":"庚午","solarYear":"0190"},"411":{"displayYear":"0411","ganzhi":"辛未","solarYear":"0191"},"412":{"displayYear":"0412","ganzhi":"壬申","solarYear":"0192"},"413":{"displayYear":"0413","ganzhi":"癸酉","solarYear":"0193"},"414":{"displayYear":"0414","ganzhi":"甲戌","solarYear":"0194"},"415":{"displayYear":"0415","ganzhi":"乙亥","solarYear":"0195"},"416":{"displayYear":"0416","ganzhi":"丙子","solarYear":"0196"},"417":{"displayYear":"0417","ganzhi":"丁丑","solarYear":"0197"},"418":{"displayYear":"0418","ganzhi":"戊寅","solarYear":"0198"},"419":{"displayYear":"0419","ganzhi":"己卯","solarYear":"0199"},"420":{"displayYear":"0420","ganzhi":"庚辰","solarYear":"0200"},"421":{"displayYear":"0421","ganzhi":"辛巳","solarYear":"0201"},"422":{"displayYear":"0422","ganzhi":"壬午","solarYear":"0202"},"423":{"displayYear":"0423","ganzhi":"癸未","solarYear":"0203"},"424":{"displayYear":"0424","ganzhi":"甲申","solarYear":"0204"},"425":{"displayYear":"0425","ganzhi":"乙酉","solarYear":"0205"},"426":{"displayYear":"0426","ganzhi":"丙戌","solarYear":"0206"},"427":{"displayYear":"0427","ganzhi":"丁亥","solarYear":"0207"},"428":{"displayYear":"0428","ganzhi":"戊子","solarYear":"0208"},"429":{"displayYear":"0429","ganzhi":"己丑","solarYear":"0209"},"430":{"displayYear":"0430","ganzhi":"庚寅","solarYear":"0210"},"431":{"displayYear":"0431","ganzhi":"辛卯","solarYear":"0211"},"432":{"displayYear":"0432","ganzhi":"壬辰","solarYear":"0212"},"433":{"displayYear":"0433","ganzhi":"癸巳","solarYear":"0213"},"434":{"displayYear":"0434","ganzhi":"甲午","solarYear":"0214"},"435":{"displayYear":"0435","ganzhi":"乙未","solarYear":"0215"},"436":{"displayYear":"0436","ganzhi":"丙申","solarYear":"0216"},"437":{"displayYear":"0437","ganzhi":"丁酉","solarYear":"0217"},"438":{"displayYear":"0438","ganzhi":"戊戌","solarYear":"0218"},"439":{"displayYear":"0439","ganzhi":"己亥","solarYear":"0219"},"440":{"displayYear":"0440","ganzhi":"庚子","solarYear":"0220"},"441":{"displayYear":"0441","ganzhi":"辛丑","solarYear":"0221"},"442":{"displayYear":"0442","ganzhi":"壬寅","solarYear":"0222"},"443":{"displayYear":"0443","ganzhi":"癸卯","solarYear":"0223"},"444":{"displayYear":"0444","ganzhi":"甲辰","solarYear":"0224"},"445":{"displayYear":"0445","ganzhi":"乙巳","solarYear":"0225"},"446":{"displayYear":"0446","ganzhi":"丙午","solarYear":"0226"},"447":{"displayYear":"0447","ganzhi":"丁未","solarYear":"0227"},"448":{"displayYear":"0448","ganzhi":"戊申","solarYear":"0228"},"449":{"displayYear":"0449","ganzhi":"己酉","solarYear":"0229"},"450":{"displayYear":"0450","ganzhi":"庚戌","solarYear":"0230"},"451":{"displayYear":"0451","ganzhi":"辛亥","solarYear":"0231"},"452":{"displayYear":"0452","ganzhi":"壬子","solarYear":"0232"},"453":{"displayYear":"0453","ganzhi":"癸丑","solarYear":"0233"},"454":{"displayYear":"0454","ganzhi":"甲寅","solarYear":"0234"},"455":{"displayYear":"0455","ganzhi":"乙卯","solarYear":"0235"},"456":{"displayYear":"0456","ganzhi":"丙辰","solarYear":"0236"},"457":{"displayYear":"0457","ganzhi":"丁巳","solarYear":"0237"},"458":{"displayYear":"0458","ganzhi":"戊午","solarYear":"0238"},"459":{"displayYear":"0459","ganzhi":"己未","solarYear":"0239"},"460":{"displayYear":"0460","ganzhi":"庚申","solarYear":"0240"},"461":{"displayYear":"0461","ganzhi":"辛酉","solarYear":"0241"},"462":{"displayYear":"0462","ganzhi":"壬戌","solarYear":"0242"},"463":{"displayYear":"0463","ganzhi":"癸亥","solarYear":"0243"},"464":{"displayYear":"0464","ganzhi":"甲子","solarYear":"0244"},"465":{"displayYear":"0465","ganzhi":"乙丑","solarYear":"0245"},"466":{"displayYear":"0466","ganzhi":"丙寅","solarYear":"0246"},"467":{"displayYear":"0467","ganzhi":"丁卯","solarYear":"0247"},"468":{"displayYear":"0468","ganzhi":"戊辰","solarYear":"0248"},"469":{"displayYear":"0469","ganzhi":"己巳","solarYear":"0249"},"470":{"displayYear":"0470","ganzhi":"庚午","solarYear":"0250"},"471":{"displayYear":"0471","ganzhi":"辛未","solarYear":"0251"},"472":{"displayYear":"0472","ganzhi":"壬申","solarYear":"0252"},"473":{"displayYear":"0473","ganzhi":"癸酉","solarYear":"0253"},"474":{"displayYear":"0474","ganzhi":"甲戌","solarYear":"0254"},"475":{"displayYear":"0475","ganzhi":"乙亥","solarYear":"0255"},"476":{"displayYear":"0476","ganzhi":"丙子","solarYear":"0256"},"477":{"displayYear":"0477","ganzhi":"丁丑","solarYear":"0257"},"478":{"displayYear":"0478","ganzhi":"戊寅","solarYear":"0258"},"479":{"displayYear":"0479","ganzhi":"己卯","solarYear":"0259"},"480":{"displayYear":"0480","ganzhi":"庚辰","solarYear":"0260"},"481":{"displayYear":"0481","ganzhi":"辛巳","solarYear":"0261"},"482":{"displayYear":"0482","ganzhi":"壬午","solarYear":"0262"},"483":{"displayYear":"0483","ganzhi":"癸未","solarYear":"0263"},"484":{"displayYear":"0484","ganzhi":"甲申","solarYear":"0264"},"485":{"displayYear":"0485","ganzhi":"乙酉","solarYear":"0265"},"486":{"displayYear":"0486","ganzhi":"丙戌","solarYear":"0266"},"487":{"displayYear":"0487","ganzhi":"丁亥","solarYear":"0267"},"488":{"displayYear":"0488","ganzhi":"戊子","solarYear":"0268"},"489":{"displayYear":"0489","ganzhi":"己丑","solarYear":"0269"},"490":{"displayYear":"0490","ganzhi":"庚寅","solarYear":"0270"},"491":{"displayYear":"0491","ganzhi":"辛卯","solarYear":"0271"},"492":{"displayYear":"0492","ganzhi":"壬辰","solarYear":"0272"},"493":{"displayYear":"0493","ganzhi":"癸巳","solarYear":"0273"},"494":{"displayYear":"0494","ganzhi":"甲午","solarYear":"0274"},"495":{"displayYear":"0495","ganzhi":"乙未","solarYear":"0275"},"496":{"displayYear":"0496","ganzhi":"丙申","solarYear":"0276"},"497":{"displayYear":"0497","ganzhi":"丁酉","solarYear":"0277"},"498":{"displayYear":"0498","ganzhi":"戊戌","solarYear":"0278"},"499":{"displayYear":"0499","ganzhi":"己亥","solarYear":"0279"},"500":{"displayYear":"0500","ganzhi":"庚子","solarYear":"0280"}};

  const DAY_NAMES = [
    "初一","初二","初三","初四","初五","初六","初七","初八","初九","初十",
    "十一","十二","十三","十四","十五","十六","十七","十八","十九","二十",
    "廿一","廿二","廿三","廿四","廿五","廿六","廿七","廿八","廿九","三十"
  ];

  const panel = document.getElementById("detailPanel");
  const title = document.getElementById("detailTitle");
  const dateGrid = document.getElementById("dateGrid");
  const eraList = document.getElementById("eraList");
  let activeCell = null;

  function esc(value) {
    return String(value ?? "").replace(/[&<>\"]/g, ch => ({
      "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"
    }[ch]));
  }

  function renderToolbar() {
    const select = document.getElementById("yearSelect");
    select.innerHTML = Object.entries(AVAILABLE).map(([year, meta]) =>
      `<option value="${year}.html" ${Number(year) === DATA.displayYear ? "selected" : ""}>` +
      `${meta.displayYear}年 ${meta.ganzhi} 西曆${meta.solarYear}年</option>`
    ).join("");
    select.addEventListener("change", () => { location.href = select.value; });
  }

  function renderHeader() {
    document.getElementById("yearNumber").textContent = `${String(DATA.displayYear).padStart(4, "0")}年`;
    document.getElementById("yearGanzhi").textContent = DATA.title.ganzhi;
    document.getElementById("solarNewYear").textContent = `元日西曆 ${DATA.title.solarNewYear}`;
    document.getElementById("eraSummary").innerHTML = DATA.title.eras.map(group => `
      <div class="year-era-block">
        <span class="year-era-power">${esc(group.state)}</span>
        <span class="year-era-lines">${group.entries.map(entry => `<span>${esc(entry)}</span>`).join("")}</span>
      </div>`
    ).join("");
  }

  function getLower(day) {
    // 日历正文只使用平气。定气保留在数据中，但不参与显示。
    const term = day.astronomy.meanSolarTerm || "";
    if (term) return { text: term, term, rollover: false };
    const western = day.western;
    const rollover = western.month === "01" && western.day === "01";
    return {
      // 西曆01-01只显示四位西曆年，例如0221。
      text: rollover ? western.year : `${western.month}-${western.day}`,
      term: "",
      rollover
    };
  }

  function renderTable() {
    const table = document.getElementById("calendarTable");
    let html = `<thead><tr><th class="month-col">月</th>` +
      DAY_NAMES.map(name => `<th>${name}</th>`).join("") + `</tr></thead><tbody>`;
    for (const month of DATA.months) {
      const byNumber = new Map(month.days.map(day => [Number(day.chinese.day), day]));
      html += `<tr><td class="month-name${month.isLeap ? " leap" : ""}">${esc(month.name)}</td>`;
      for (let number = 1; number <= 30; number++) {
        const day = byNumber.get(number);
        if (!day) {
          html += `<td class="day-cell empty"><div class="top"></div><div class="bottom"></div></td>`;
          continue;
        }
        const lower = getLower(day);
        const lowerHtml = lower.term
          ? `<div class="bottom" data-term="${esc(lower.term)}">${esc(lower.text)}</div>`
          : `<div class="bottom${lower.rollover ? " rollover" : ""}">${esc(lower.text)}</div>`;
        html += `<td class="day-cell day-clickable" data-key="${esc(day.key)}">` +
          `<div class="top">${esc(day.ganzhi)}</div>${lowerHtml}</td>`;
      }
      html += `</tr>`;
    }
    table.innerHTML = html + `</tbody>`;
  }

  function closePanel() {
    panel.classList.remove("show");
    panel.style.display = "none";
    if (activeCell) { activeCell.classList.remove("active"); activeCell = null; }
  }

  function renderPopup(day) {
    title.textContent = day.ganzhi || "";
    dateGrid.innerHTML =
      `<span class="date-label">中曆</span>` +
      `<span class="date-main">${esc(day.chinese.date)}</span>` +
      `<span class="date-cal">${esc(day.chinese.calendar)}</span>` +
      `<span class="date-label">西曆</span>` +
      `<span class="date-main">${esc(day.western.date)}</span>` +
      `<span class="date-cal">${esc(day.western.calendar)}</span>`;

    // 君主保留在数据中，但弹窗不显示。
    const rows = (day.orthodoxies || []).map(record => `
      <div class="era-detail-row">
        <span class="era-power">${esc(record.state)}</span>
        <span class="era-detail-main">
          <span>${esc(record.eraYear)}</span><span>${esc(record.month)}</span><span>${esc(record.day)}</span>
        </span>
        <span class="era-cal">${esc(record.calendar)}</span>
      </div>`);
    eraList.innerHTML = rows.join("") ||
      `<div class="era-detail-row"><span></span><span>無紀年資料</span><span></span></div>`;
  }

  function placePanel(cell) {
    panel.style.display = "block";
    panel.classList.add("show");
    const rect = cell.getBoundingClientRect();
    const panelRect = panel.getBoundingClientRect();
    let left = window.scrollX + rect.left + rect.width / 2 - panelRect.width / 2;
    const minLeft = window.scrollX + 8;
    const maxLeft = window.scrollX + window.innerWidth - panelRect.width - 8;
    if (left < minLeft) left = minLeft;
    if (left > maxLeft) left = Math.max(minLeft, maxLeft);
    let arrow = window.scrollX + rect.left + rect.width / 2 - left - 7;
    arrow = Math.max(14, Math.min(panelRect.width - 26, arrow));
    panel.style.setProperty("--arrow-left", `${arrow}px`);
    panel.style.left = `${left}px`;
    panel.style.top = `${window.scrollY + rect.bottom + 9}px`;
  }

  document.addEventListener("click", event => {
    const cell = event.target.closest(".day-clickable");
    if (!cell) {
      if (!event.target.closest("#detailPanel")) closePanel();
      return;
    }
    if (activeCell === cell && panel.classList.contains("show")) { closePanel(); return; }
    if (activeCell) activeCell.classList.remove("active");
    activeCell = cell;
    cell.classList.add("active");
    renderPopup(DATA.dayIndex[cell.dataset.key]);
    placePanel(cell);
  });

  document.getElementById("closeDetail").addEventListener("click", closePanel);
  window.addEventListener("resize", () => {
    if (activeCell && panel.classList.contains("show")) placePanel(activeCell);
  });

  renderToolbar();
  renderHeader();
  renderTable();
})();
