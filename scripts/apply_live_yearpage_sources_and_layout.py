#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
INDEX_JS = DATA_DIR / "index-data.js"
CAL_JS = ROOT / "js" / "calendar.js"
CSS = ROOT / "css" / "calendar.css"


def E(era, *notes):
    return {"era": era, "notes": [n for n in notes if n]}

# Current effective values read directly from the live 年 sheet. Only rows that
# contain source text are overridden; ordinary blank 年-page cells retain the
# already-present annual era so headings never disappear.
LIVE = {
    11: {"秦": [E("始皇帝三十七年",
        "六月丙寅，始皇崩於沙丘平臺。（《史記·秦始皇本紀》；原作七月，校改为六月）",
        "太子胡亥襲位，為二世皇帝。九月，葬始皇酈山。（《史記·秦始皇本紀》）")]},
    14: {"秦": [E("二世皇帝三年", "八月……二世自殺。（《史記·秦始皇本紀》）"),
                 E("秦王子嬰元年", "立二世之兄子公子嬰為秦王。（《史記·秦始皇本紀》）")]},
    15: {"秦": [E("秦王子嬰二年", "子嬰為秦王四十六日……奉天子璽符，降軹道旁。（《史記·秦始皇本紀》）")],
         "漢": [E("元年", "正月，項羽自立為西楚霸王……更立沛公為漢王。")]},
    26: {"漢": [E("十二年", "四月甲辰，高祖崩長樂宮。"),
                 E("元年", "五月丙寅，太子即皇帝位。（《漢書·惠帝紀》）")]},
    245: {"漢": [E("建武元年",
        "六月己未，即皇帝位……於是建元爲建武，大赦天下。（《後漢書·光武帝紀》）",
        "十月，更始遂隨祿肉袒詣長樂宮，上璽綬於盆子。（《後漢書·劉玄列傳》）")]},
    247: {"漢": [E("建武三年", "二月……丙午，赤眉君臣面縛，奉高皇帝璽綬。（《後漢書·光武帝紀》，原文为“閏月”，校改为“二月”）")]},
    277: {"漢": [E("建武中二年", "二月戊戌，帝崩於南宮前殿。太子即皇帝位，年三十。（《後漢書·明帝紀》）")]},
    295: {"漢": [E("永平十八年", "秋八月壬子，帝崩於東宮前殿。太子即皇帝位，年十九。（《後漢書·章帝紀》）")]},
    305: {"漢": [E("元和二年", "二月甲寅，始用四分曆。（《後漢書·律曆志下》）")]},
    308: {"漢": [E("章和二年", "二月壬辰，即皇帝位，年十歲。（《後漢書·和帝紀》）")]},
    326: {"漢": [E("延平元年",
        "八月辛亥，帝崩。（《後漢書·殤帝紀》）",
        "其夜……即皇帝位，年十三。（《後漢書·安帝紀》）")]},
    345: {"漢": [E("延光四年",
        "三月……丁卯，幸葉，帝崩于乘輿，年三十二。（《後漢書·安帝紀》）",
        "三月……乙酉，北鄉侯即皇帝位。（《後漢書·安帝紀》）",
        "冬十月……辛亥，少帝薨。（《後漢書·安帝紀》）",
        "十一月丁巳……即皇帝位，年十一。（《後漢書·順帝紀》）")]},
    365: {"漢": [E("永嘉元年",
        "春正月戊戌，帝崩于玉堂前殿，年三歲。（《後漢書·沖帝紀》）",
        "正月……丁巳，封爲建平侯，其日即皇帝位，年八歲。（《後漢書·質帝紀》）")]},
    366: {"漢": [E("本初元年",
        "閏六月甲申，大將軍梁冀潛行鴆弒，帝崩于玉堂前殿，年九歲。（《後漢書·質帝紀》）",
        "閏月庚寅……迎帝入南宮，其日即皇帝位，時年十五。（《後漢書·桓帝紀》）")]},
    370: {"漢": [E("和平元年", "春正月甲子，大赦天下，改元和平。（《後漢書·桓帝紀》）")]},
    409: {"漢": [E("中平六年",
        "夏四月丙辰，帝崩于南宮嘉德殿，年三十四。（《後漢書·靈帝紀》）",
        "閏月戊戌……詔除光熹、昭寧、永漢三號，還復中平六年。（《後漢書·獻帝紀》）"),
        E("光熹元年", "戊午，皇子辯即皇帝位，年十七……大赦天下，改元爲光喜。（《後漢書·靈帝紀》）"),
        E("昭寧元年", "八月……辛未，還宮。大赦天下，改光喜爲昭寧。（《後漢書·靈帝紀》）"),
        E("永漢元年", "九月甲戌，即皇帝位，年九歲……大赦天下。改昭寧爲永漢。（《後漢書·獻帝紀》）")]},
    440: {"魏": [E("黄初元年", "辛未，魏王登壇受禪……其以延康元年为黄初元年。（《三國志·魏書·文帝紀》裴松之注引《獻帝傳》）")]},
    441: {"漢": [E("黄初二年", "四月丙午，皇帝備……受皇帝璽綬……大赦，改年。（《三國志·蜀書·先主傳》）")],
          "魏": [E("黄初二年")]},
    442: {"漢": [E("黄初三年", "冬十月……孫權復叛。（《三國志·魏書·文帝紀》）權遂改年，臨江拒守。（《三國志·吳書·吳主傳》）")],
          "魏": [E("黄初三年")], "漢（蜀）": [E("章武二年")],
          "吴": [E("黄武元年", "冬十月……孫權復叛。（《三國志·魏書·文帝紀》）權遂改年，臨江拒守。（《三國志·吳書·吳主傳》）")]},
    443: {"漢": [E("黄初四年", "春正月……改四分，用乾象曆。（《三國志·吳書·吳主傳》）", "五月，後主襲位於成都，大赦，改元。（《三國志·蜀書·後主傳》）")],
          "魏": [E("黄初四年")],
          "漢（蜀）": [E("章武三年"), E("建興元年", "五月，後主襲位於成都，大赦，改元。（《三國志·蜀書·後主傳》）")],
          "吴": [E("黄武二年")]},
    446: {"漢": [E("黄初七年", "夏五月……丁巳，即皇帝位，大赦。（《三國志·魏書·明帝紀》）")],
          "魏": [E("黄初七年")], "漢（蜀）": [E("建興四年")], "吴": [E("黄武五年")]},
    449: {"漢": [E("太和三年", "夏四月，夏口、武昌並言黃龍、鳳皇見。丙申，南郊即皇帝位，大赦，改元。（《三國志·吳書·吳主傳》）")],
          "魏": [E("太和三年")], "漢（蜀）": [E("建興七年")]},
    452: {"漢": [E("太和六年", "春正月……（《三國志·吳書·吳主傳》）")],
          "魏": [E("太和六年")], "漢（蜀）": [E("建興十年")], "吴": [E("嘉禾元年")]},
    458: {"漢（蜀）": [E("延熙元年")],
          "吴": [E("嘉禾七年"), E("赤烏元年", "秋八月，武昌言麒麟見。有司奏言麒麟者太平之應，宜改年號。詔曰可。（《三國志·吳書·吳主傳》）")]},
    460: {"漢": [E("正始元年", "春二月乙丑，加侍中中書監劉放、侍中中書令孫資右光祿大夫，金印紫綬，儀同三司。（《三國志·魏書·三少帝紀》）")],
          "魏": [E("正始元年")], "吴": [E("赤烏三年")]},
    471: {"漢": [E("嘉平三年", "夏五月，立皇后潘氏，大赦，改年。（《三國志·吳書·吳主傳》）")],
          "魏": [E("嘉平三年")], "漢（蜀）": [E("延熙十四年")]},
    472: {"漢": [E("嘉平四年", "春二月，帝寢疾。（《三國志·吳書·吳主傳》）", "夏四月，權薨……太子亮即尊號，大赦，改元。（《三國志·吳書·三嗣主傳》）")],
          "魏": [E("嘉平四年")], "漢（蜀）": [E("延熙十五年")]},
    474: {"漢": [E("嘉平六年", "春，大赦。（《三國志·吳書·三嗣主傳》）"),
                 E("正元元年", "冬十月己丑，公至於玄武館。庚寅……乃御前殿，改元。（《三國志·魏書·三少帝紀》）")],
          "魏": [E("嘉平六年"), E("正元元年", "冬十月己丑，公至於玄武館。庚寅……乃御前殿，改元。（《三國志·魏書·三少帝紀》）")],
          "漢（蜀）": [E("延熙十七年")], "吴": [E("五鳳元年")]},
    476: {"漢（蜀）": [E("延熙十九年")],
          "吴": [E("五鳳三年"), E("太平元年", "冬十月己酉，大赦，改年。（《三國志·吳書·三嗣主傳》）")]},
    478: {"漢": [E("甘露三年",
        "春正月，姜維還成都。史官言景星見，於是大赦，改年。（《三國志·蜀書·後主傳》）",
        "冬十月戊寅，行至曲阿，有老公干休叩頭曰：「事久變生，天下喁喁，願陛下速行。」休善之。己卯，行至布塞亭，武衞將軍恩行丞相事，率百僚以乘輿法駕迎於永昌亭，築宮，以武帳爲便殿，設御座。休謙不肯御，百僚上書三四，休乃許之。於是正殿，羣臣以次奉引，休就乘輿，百官陪位。孫綝以兵千人迎於半野，拜於道側。休下車答拜。即日御正殿，大赦，改元。（《三國志·吳書·三嗣主傳》）")],
          "魏": [E("甘露三年")],
          "吴": [E("太平三年"), E("永安元年", "冬十月戊寅，行至曲阿，有老公干休叩頭曰：「事久變生，天下喁喁，願陛下速行。」休善之。己卯，行至布塞亭，武衞將軍恩行丞相事，率百僚以乘輿法駕迎於永昌亭，築宮，以武帳爲便殿，設御座。休謙不肯御，百僚上書三四，休乃許之。於是正殿，羣臣以次奉引，休就乘輿，百官陪位。孫綝以兵千人迎於半野，拜於道側。休下車答拜。即日御正殿，大赦，改元。（《三國志·吳書·三嗣主傳》）")]},
    483: {"漢": [E("景元四年", "夏，魏大興徒衆，命征西將軍鄧艾、鎮西將軍鍾會、雍州刺史諸葛緒數道並攻。（《三國志·蜀書·後主傳》）", "冬十一月……是月，蜀主劉禪詣艾降，巴蜀皆平。（《三國志·魏書·三少帝紀》）")],
          "魏": [E("景元四年")], "吴": [E("永安六年")]},
    484: {"吴": [E("永安七年"), E("元興元年", "秋七月，休薨。是月，皓即皇帝位，大赦，改元。（《三國志·吳書·三嗣主傳》）")]},
    485: {"漢": [E("咸熙二年", "夏四月，蔣陵言甘露降，於是大赦，改年。（《三國志·吳書·三嗣主傳》）"),
                 E("泰始元年", "十二月丙寅，設壇於南郊，百僚在位及匈奴南單于四夷會者數萬人，柴燎告類於上帝曰：……於是大赦，改元。（《晉書·武帝紀》）")],
          "魏": [E("咸熙二年")],
          "晉": [E("泰始元年", "十二月丙寅，設壇於南郊，百僚在位及匈奴南單于四夷會者數萬人，柴燎告類於上帝曰：……於是大赦，改元。（《晉書·武帝紀》）")]},
    486: {"漢": [E("泰始二年", "秋八月，所在言得大鼎，於是大赦，改年。（《三國志·吳書·三嗣主傳》）")],
          "晉": [E("泰始二年")]},
    489: {"漢": [E("泰始五年", "冬十月，改年，大赦。（《三國志·吳書·三嗣主傳》）")],
          "晉": [E("泰始五年")]},
    492: {"漢": [E("泰始八年", "春正月，大赦，改年。（《三國志·吳書·三嗣主傳》）")],
          "晉": [E("泰始八年")], "吴": [E("鳳皇元年")]},
    495: {"漢": [E("咸寧元年", "，吳郡言掘地得銀，長一尺，廣三分，刻上有年月字，於是大赦，改年。（《三國志·吳書·三嗣主傳》）")],
          "晉": [E("咸寧元年")], "吴": [E("天冊元年")]},
    496: {"漢": [E("咸寧二年", "，吳郡言臨平湖自漢末草穢壅塞，今更開通。長老相傳，此湖塞，天下亂，此湖開，天下平。又於湖邊得石函，中有小石，青白色，長四寸，廣二寸餘，刻上作皇帝字，於是改年，大赦。（《三國志·吳書·三嗣主傳》）")],
          "晉": [E("咸寧二年")]},
    497: {"漢": [E("咸寧三年", "夏，夏口督孫慎出江夏、汝南，燒略居民。（《三國志·吳書·三嗣主傳》）")],
          "晉": [E("咸寧三年")], "吴": [E("天紀元年")]},
}

ACTUAL_COL = {"秦": "秦", "漢": "漢", "魏": "魏", "晉": "晉", "漢（蜀）": "漢（蜀）", "吴": "吴"}
CANONICAL = ["秦", "楚", "漢", "魏", "晉", "漢（蜀）", "吴"]


def load_js_json(path: Path, variable: str):
    text = path.read_text(encoding="utf-8")
    marker = f"window.{variable} ="
    payload = text[text.index(marker) + len(marker):].strip()
    if payload.endswith(";"):
        payload = payload[:-1]
    return json.loads(payload)


def save_js_json(path: Path, variable: str, obj):
    path.write_text(f"window.{variable} = " + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


def unique(seq):
    out = []
    for x in seq:
        if x not in out:
            out.append(x)
    return out


def update_titles():
    source_entries = 0
    expanded_years = []
    for year in range(1, 501):
        p = DATA_DIR / f"{year}.js"
        data = load_js_json(p, "CalendarData")
        row = LIVE.get(year, {})

        note_map = defaultdict(list)
        for entries in row.values():
            for entry in entries:
                for note in entry.get("notes", []):
                    if note not in note_map[entry["era"]]:
                        note_map[entry["era"]].append(note)

        old_groups = data["title"].get("eras", [])
        old_by_state = {g["state"]: g for g in old_groups}
        states = [g["state"] for g in old_groups]
        # Add state-specific live cells that are absent from the prior heading.
        for state in CANONICAL:
            if state in row and state != "漢" and state not in states:
                states.append(state)

        new_groups = []
        for state in states:
            old = old_by_state.get(state, {"state": state, "entries": []})
            old_entries = []
            for item in old.get("entries", []):
                if isinstance(item, str):
                    old_entries.append(E(item))
                else:
                    old_entries.append(E(item.get("era", ""), *(item.get("notes") or [])))

            live_entries = None
            if state in ACTUAL_COL and state in row:
                # After the Han dynasty, the 年-sheet “漢” column functions as a
                # main-line source helper; do not create a spurious 漢 heading.
                if state != "漢" or year <= 440:
                    live_entries = row[state]
            entries = live_entries if live_entries is not None else old_entries
            if live_entries is not None and [x["era"] for x in live_entries] != [x["era"] for x in old_entries]:
                expanded_years.append(year)

            cleaned = []
            for entry in entries:
                era = entry.get("era", "").strip()
                if not era:
                    continue
                notes = unique([n.strip() for n in entry.get("notes", []) if n and n.strip()] + note_map.get(era, []))
                if notes:
                    source_entries += 1
                cleaned.append({"era": era, "notes": notes})
            if cleaned:
                new_groups.append({"state": state, "entries": cleaned})
        data["title"]["eras"] = new_groups
        save_js_json(p, "CalendarData", data)
    return source_entries, unique(expanded_years)


def update_index_data():
    index = load_js_json(INDEX_JS, "CalendarIndexData")
    by_year = {x["year"]: x for x in index["years"]}
    for year in range(1, 501):
        data = load_js_json(DATA_DIR / f"{year}.js", "CalendarData")
        item = by_year[year]
        details, eras, states = [], [], []
        for group in data["title"].get("eras", []):
            state = group["state"]
            if state not in states:
                states.append(state)
            for entry in group.get("entries", []):
                era, notes = entry["era"], entry.get("notes", []) or []
                full = era + (("：" + "\n".join(notes)) if notes else "")
                eras.append(era)
                details.append({"state": state, "text": full, "era": era,
                                "note": notes[0] if notes else "", "notes": notes,
                                "fullText": full})
        item["eras"], item["eraDetails"], item["states"] = eras, details, states
    save_js_json(INDEX_JS, "CalendarIndexData", index)


def patch_js():
    text = CAL_JS.read_text(encoding="utf-8")
    start = text.index("  function renderHeader() {")
    end = text.index("\n  function getLower(day) {", start)
    replacement = '''  function renderHeader() {
    document.getElementById("yearNumber").textContent = `${String(DATA.displayYear).padStart(4, "0")}年`;
    document.getElementById("yearGanzhi").textContent = DATA.title.ganzhi;
    document.getElementById("solarNewYear").textContent = `元日西曆 ${DATA.title.solarNewYear}`;
    document.getElementById("eraSummary").innerHTML = DATA.title.eras.map(group => {
      const entries = Array.isArray(group.entries) ? group.entries : [];
      return entries.map((entry, index) => {
        const item = typeof entry === "string" ? { era: entry, notes: [] } : entry;
        const notes = Array.isArray(item.notes)
          ? item.notes
          : (item.note ? String(item.note).split(/\\n+/).filter(Boolean) : []);
        return `<div class="year-era-row">` +
          `<span class="year-era-power">${index === 0 ? esc(displayState(group.state)) : ""}</span>` +
          `<span class="year-era-name">${esc(item.era || "")}</span>` +
          `<span class="year-era-source">${notes.map(note => `<span>${esc(note)}</span>`).join("")}</span>` +
          `</div>`;
      }).join("");
    }).join("");
  }
'''
    CAL_JS.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


def patch_css():
    marker = "/* 2026-07-24 年页出典分栏与弹窗六列统一 */"
    text = CSS.read_text(encoding="utf-8")
    if marker in text:
        text = text[:text.index(marker)].rstrip() + "\n"
    override = r'''

/* 2026-07-24 年页出典分栏与弹窗六列统一 */
.year-era-summary{
  display:grid !important;
  grid-template-columns:4.8em max-content minmax(0,1fr) !important;
  column-gap:.72rem !important;
  row-gap:3px !important;
  align-items:start !important;
  padding-top:0 !important;
  max-width:none !important;
  min-width:0;
}
.year-era-row{display:contents;}
.year-era-power{grid-column:1;min-width:0 !important;width:auto !important;max-width:none !important;color:#7d2419;font-weight:700;text-align:left;}
.year-era-name{grid-column:2;white-space:nowrap;font-family:"SimSun","Songti SC","Noto Serif CJK SC","Noto Serif CJK TC",serif !important;font-weight:400 !important;}
.year-era-source{grid-column:3;min-width:0;font-family:KaiTi,"STKaiti","Kaiti SC","標楷體",serif !important;font-size:13px;line-height:1.22;font-weight:400;color:#49372a;overflow-wrap:anywhere;}
.year-era-source > span{display:block;}

/* 上栏、下栏表头与下栏数据严格共用六列固定轨道。 */
.detail-panel{box-sizing:border-box !important;width:482px !important;max-width:calc(100vw - 16px) !important;overflow:hidden !important;}
.date-grid,.era-detail-head,.era-detail-row{
  display:grid !important;
  grid-template-columns:72px 74px 110px 52px 52px 78px !important;
  column-gap:3px !important;
  align-items:start !important;
  box-sizing:border-box !important;
  width:100% !important;
  min-width:0 !important;
  max-width:100% !important;
}
.date-grid{font-size:15px !important;line-height:1.28 !important;}
.era-detail-head{font-size:12px !important;line-height:1.28 !important;}
.era-detail-row{font-size:14px !important;line-height:1.3 !important;}
.date-grid > span,.era-detail-head > span,.era-detail-row > span{display:block !important;box-sizing:border-box !important;min-width:0 !important;max-width:100% !important;margin:0 !important;padding:0 !important;}
.date-grid > :nth-child(1){grid-column:1;grid-row:1;}
.date-grid > :nth-child(2){grid-column:2 / 6;grid-row:1;}
.date-grid > :nth-child(3){grid-column:6;grid-row:1;}
.date-grid > :nth-child(4){grid-column:1;grid-row:2;}
.date-grid > :nth-child(5){grid-column:2 / 6;grid-row:2;}
.date-grid > :nth-child(6){grid-column:6;grid-row:2;}
.date-grid .date-main{text-align:left !important;white-space:nowrap !important;overflow:hidden !important;}
.date-grid .date-cal,.era-detail-head > span:last-child,.era-detail-row .era-cal{grid-column:6;width:100% !important;text-align:right !important;justify-self:stretch !important;white-space:nowrap !important;overflow:hidden !important;}
.era-detail-head > span:not(:last-child),.era-detail-row > span:not(.era-cal){text-align:left !important;}
.era-detail-row .era-power{white-space:normal !important;overflow-wrap:anywhere !important;word-break:keep-all !important;}
@media(max-width:496px){
  .date-grid,.era-detail-head,.era-detail-row{grid-template-columns:minmax(46px,5fr) minmax(50px,5fr) minmax(70px,7fr) minmax(38px,4fr) minmax(38px,4fr) minmax(50px,5fr) !important;column-gap:2px !important;}
  .date-grid{font-size:13px !important;}.era-detail-row{font-size:12px !important;}
}
'''
    CSS.write_text(text.rstrip() + override + "\n", encoding="utf-8")


def main():
    source_entries, expanded = update_titles()
    update_index_data()
    patch_js()
    patch_css()
    print("year-page source entries:", source_entries)
    print("years whose displayed era list changed:", expanded)
    for year in (11, 14, 15, 26, 409, 440, 441, 442, 443, 458, 460, 474, 476, 478, 485, 497):
        d = load_js_json(DATA_DIR / f"{year}.js", "CalendarData")
        print(year, d["title"]["eras"])

if __name__ == "__main__":
    main()
