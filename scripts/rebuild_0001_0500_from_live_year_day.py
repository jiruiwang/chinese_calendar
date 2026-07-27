#!/usr/bin/env python3
"""Rebuild calendar data for years 0001-0500 from fresh 年/日-sheet XLSX files.

The current 年 sheet is mostly formula-driven. This script reproduces its displayed
A:Q formula values from the fresh 日 data and applies any literal/manual 年-sheet
cell overrides, using the live 年-sheet headers/formula rules:
秦、楚、新、漢（更始）、漢、漢（赤眉）、魏、晉、漢（蜀）、吴.
It updates only data/1.js..data/500.js, data/index-data.js, and the year selector
metadata embedded in js/calendar.js.  Years 0501 onward are left unchanged.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator, Sequence

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
YEAR_STATES = ["秦", "楚", "新", "漢（更始）", "漢", "漢（赤眉）", "魏", "晉", "漢（蜀）", "吴"]
GROUP_STARTS = (18, 24, 30)
GROUP_NAMES = ("正朔一", "正朔二", "正朔三")
GANZHI = [
    "甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉",
    "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未",
    "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
    "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯",
    "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑",
    "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥",
]
MONTH_NAMES = {
    1: "正月", 2: "二月", 3: "三月", 4: "四月", 5: "五月", 6: "六月",
    7: "七月", 8: "八月", 9: "九月", 10: "十月", 11: "十一月", 12: "十二月",
}
SOURCE_MARKER_RE = re.compile(r"【[^】]+】")
ERA_ONLY_RE = re.compile(r"(?:元|[一二三四五六七八九十百]+)年$")


def col_index(ref: str) -> int:
    match = re.match(r"([A-Z]+)", ref)
    if not match:
        raise ValueError(f"Invalid cell reference: {ref!r}")
    value = 0
    for char in match.group(1):
        value = value * 26 + ord(char) - 64
    return value - 1


def load_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    strings: list[str] = []
    try:
        stream = archive.open("xl/sharedStrings.xml")
    except KeyError:
        return strings
    with stream:
        for _event, element in ET.iterparse(stream, events=("end",)):
            if element.tag == NS + "si":
                strings.append("".join((node.text or "") for node in element.iter(NS + "t")))
                element.clear()
    return strings



def decode_cell(cell: ET.Element, strings: Sequence[str]) -> str:
    cell_type = cell.get("t")
    value_node = cell.find(NS + "v")
    value = "" if value_node is None or value_node.text is None else value_node.text
    if cell_type == "s" and value:
        value = strings[int(value)]
    elif cell_type == "inlineStr":
        value = "".join((node.text or "") for node in cell.iter(NS + "t"))
    return value


def load_year_page(path: Path) -> tuple[list[str], dict[int, dict[int, str]]]:
    """Return current A:Q headers and nonempty literal (non-formula) cell overrides."""
    with zipfile.ZipFile(path) as archive:
        strings = load_shared_strings(archive)
        headers = [""] * 17
        overrides: dict[int, dict[int, str]] = {}
        with archive.open("xl/worksheets/sheet1.xml") as stream:
            for _event, element in ET.iterparse(stream, events=("end",)):
                if element.tag != NS + "c":
                    continue
                ref = element.get("r", "")
                index = col_index(ref)
                row_match = re.search(r"(\d+)$", ref)
                if row_match is None or index >= 17:
                    element.clear()
                    continue
                row_number = int(row_match.group(1))
                value = decode_cell(element, strings)
                formula = element.find(NS + "f")
                if row_number == 1:
                    headers[index] = value
                elif 2 <= row_number <= 501 and formula is None and value != "":
                    overrides.setdefault(row_number - 1, {})[index] = value
                element.clear()
    expected = ["中曆年", "年干支", "月數", "日數", "元日干支", "元日西曆", "冬至中曆", *YEAR_STATES]
    if headers != expected:
        raise RuntimeError(f"Unexpected 年-sheet headers: {headers!r}")
    return headers, overrides


def is_era_only(line: str) -> bool:
    return len(line) <= 24 and bool(ERA_ONLY_RE.search(line))


def split_year_cell(value: str) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for raw_line in str(value or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        separator = "：" if "：" in line else (":" if ":" in line else None)
        if separator:
            era, note = line.split(separator, 1)
            current = {"era": era.strip(), "notes": [note.strip()] if note.strip() else []}
            entries.append(current)
        elif is_era_only(line):
            current = {"era": line, "notes": []}
            entries.append(current)
        elif current is not None:
            current["notes"].append(line)
        else:
            current = {"era": line, "notes": []}
            entries.append(current)
    return entries


def xlsx_rows(path: Path, max_cols: int = 40) -> Iterator[tuple[int, list[str]]]:
    with zipfile.ZipFile(path) as archive:
        strings = load_shared_strings(archive)
        with archive.open("xl/worksheets/sheet1.xml") as stream:
            for _event, element in ET.iterparse(stream, events=("end",)):
                if element.tag != NS + "row":
                    continue
                cells: dict[int, str] = {}
                for cell in element.findall(NS + "c"):
                    ref = cell.get("r", "")
                    index = col_index(ref)
                    if index >= max_cols:
                        continue
                    cells[index] = decode_cell(cell, strings)
                if cells:
                    row_number = int(element.get("r", "0"))
                    yield row_number, [cells.get(i, "") for i in range(max_cols)]
                element.clear()


def text(row: Sequence[str], index: int) -> str:
    if index >= len(row) or row[index] is None:
        return ""
    return str(row[index]).strip()


def normalize_state(value: str) -> str:
    # Google Sheets comparisons treat the mixed full-/half-width parentheses in
    # the source labels as equivalent. Store a clean full-width form in output.
    value = re.sub(r"（([^）)]*)\)", r"（\1）", str(value or "").strip())
    return value


def comparison_key(value: str) -> str:
    return unicodedata.normalize("NFKC", normalize_state(value))


def month_name(code: str) -> str:
    match = re.fullmatch(r"(\d{2})([CL])", code)
    if not match:
        return code
    number = int(match.group(1))
    return ("閏" if match.group(2) == "L" else "") + MONTH_NAMES.get(number, f"{number}月")


def normalize_western_year(value: str) -> str:
    """Normalize BCE/CE year text to four digits, preserving the BCE B prefix."""
    value = str(value or "").strip()
    match = re.fullmatch(r"(B?)(\d+)", value)
    if not match:
        return value
    prefix, digits = match.groups()
    return prefix + digits.zfill(4)


def normalize_western_date(value: str) -> str:
    """Normalize the year component of a YYYY-MM-DD or BYYYY-MM-DD date."""
    value = str(value or "").strip()
    match = re.fullmatch(r"(B?\d+)-(\d{2})-(\d{2})", value)
    if not match:
        return value
    year, month, day = match.groups()
    return f"{normalize_western_year(year)}-{month}-{day}"


def source_texts_for_era(rows: Sequence[Sequence[str]], group_start: int, state: str, era: str) -> list[str]:
    # Reproduce the 年-sheet formula literally. Only 吴 maps to the source tag 吳;
    # the current 日 sheet mostly uses 【吴】, so those notes intentionally do not
    # attach unless the year formula itself would attach them.
    source_land = "吳" if state == "吴" else state
    marker = f"【{source_land}】"
    state_key = comparison_key(state)
    found: list[str] = []
    seen: set[str] = set()
    for row in rows:
        if comparison_key(text(row, group_start)) != state_key:
            continue
        if text(row, group_start + 2) != era:
            continue
        source = text(row, 39)
        if marker not in source:
            continue
        cleaned = SOURCE_MARKER_RE.sub("", source).strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            found.append(cleaned)
    return found


def year_cell_entries(rows: Sequence[Sequence[str]], state: str) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    state_key = comparison_key(state)
    for group_start in GROUP_STARTS:
        lands = [text(row, group_start) for row in rows]
        eras = [text(row, group_start + 2) for row in rows]
        special_first_day = (
            len(rows) >= 2
            and comparison_key(lands[0]) == state_key
            and comparison_key(lands[1]) == state_key
            and eras[1] != eras[0]
        )
        previous_era = ""
        for index, (land, era) in enumerate(zip(lands, eras)):
            changed = index == 0 or era != previous_era
            include = (
                comparison_key(land) == state_key
                and bool(era)
                and changed
                and not (special_first_day and index == 0)
            )
            if include:
                notes = source_texts_for_era(rows, group_start, state, era)
                entries.append({"era": era, "notes": notes})
            previous_era = era
    return entries


def make_day(row: Sequence[str]) -> dict[str, object]:
    orthodoxies: list[dict[str, str]] = []
    for group_name, start in zip(GROUP_NAMES, GROUP_STARTS):
        state = normalize_state(text(row, start))
        if not state:
            continue
        orthodoxies.append({
            "group": group_name,
            "state": state,
            "ruler": text(row, start + 1),
            "eraYear": text(row, start + 2),
            "month": text(row, start + 3),
            "day": text(row, start + 4),
            "calendar": text(row, start + 5),
        })
    return {
        "key": text(row, 0),
        "ganzhi": text(row, 1),
        "weekday": text(row, 9),
        "chinese": {
            "date": text(row, 0),
            "year": text(row, 3),
            "month": text(row, 4),
            "day": text(row, 5),
            "calendar": text(row, 16),
        },
        "western": {
            "date": normalize_western_date(text(row, 2)),
            "year": normalize_western_year(text(row, 6)),
            "month": text(row, 7),
            "day": text(row, 8),
            "calendar": text(row, 17),
        },
        "astronomy": {
            "syzygy": text(row, 10),
            "meanSolarTerm": text(row, 11),
            "moonPhase": text(row, 12),
            "trueSolarTerm": text(row, 13),
            "solarEclipse": text(row, 14),
            "lunarEclipse": text(row, 15),
        },
        "orthodoxies": orthodoxies,
        "events": {
            "calendarChange": text(row, 36),
            "newRuler": text(row, 37),
            "eraChange": text(row, 38),
            "source": text(row, 39),
        },
    }


def build_year(
    year: int,
    raw_rows: Sequence[Sequence[str]],
    year_overrides: dict[int, str],
) -> tuple[dict[str, object], dict[str, object]]:
    if not raw_rows:
        raise RuntimeError(f"No 日-page rows found for year {year:04d}")
    days = [make_day(row) for row in raw_rows]

    months: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for day in days:
        code = str(day["chinese"]["month"])
        if current is None or current["id"] != code:
            current = {
                "id": code,
                "name": month_name(code),
                "isLeap": code.endswith("L"),
                "daysInMonth": 0,
                "days": [],
            }
            months.append(current)
        current["days"].append(day)
        current["daysInMonth"] = int(current["daysInMonth"]) + 1

    era_groups: list[dict[str, object]] = []
    for state_index, state in enumerate(YEAR_STATES, start=7):
        if state_index in year_overrides:
            entries = split_year_cell(year_overrides[state_index])
        else:
            entries = year_cell_entries(raw_rows, state)
        if entries:
            era_groups.append({"state": state, "entries": entries})

    winter_solstice = ""
    for day in days:
        if day["astronomy"]["meanSolarTerm"] == "冬至":
            winter_solstice = str(day["key"])
            break

    def override_int(index: int, fallback: int) -> int:
        value = year_overrides.get(index, "")
        try:
            return int(float(value)) if value != "" else fallback
        except ValueError as exc:
            raise RuntimeError(f"Invalid numeric 年-sheet override {year:04d}, column {index + 1}: {value!r}") from exc

    title = {
        "year": f"{year:04d}",
        "displayYear": year,
        "ganzhi": year_overrides.get(1, GANZHI[(year + 16) % 60]),
        "monthCount": override_int(2, len(months)),
        "dayCount": override_int(3, len(days)),
        "yuanriGanzhi": year_overrides.get(4, str(days[0]["ganzhi"])),
        "solarNewYear": year_overrides.get(5, str(days[0]["western"]["date"])),
        "winterSolstice": year_overrides.get(6, winter_solstice),
        "eras": era_groups,
    }
    calendar = {
        "year": f"{year:04d}",
        "displayYear": year,
        "title": title,
        "months": months,
    }
    return title, calendar


def load_index(path: Path) -> tuple[str, dict[str, object]]:
    source = path.read_text(encoding="utf-8")
    prefix = "window.CalendarIndexData = "
    if not source.startswith(prefix):
        raise RuntimeError(f"Unexpected index-data format: {path}")
    return prefix, json.loads(source[len(prefix):].rstrip().rstrip(";"))


def update_calendar_available(calendar_js: Path, years: Sequence[dict[str, object]]) -> None:
    available = {
        str(record["year"]): {
            "displayYear": record["year4"],
            "ganzhi": record["ganzhi"],
            "solarYear": record["solarYear"],
        }
        for record in years
    }
    source = calendar_js.read_text(encoding="utf-8")
    replacement = "const AVAILABLE = " + json.dumps(available, ensure_ascii=False, separators=(",", ":")) + ";"
    updated, count = re.subn(r"const AVAILABLE = \{.*?\};", replacement, source, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError("Could not locate the embedded AVAILABLE map in calendar.js")
    calendar_js.write_text(updated, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year-xlsx", type=Path, required=True)
    parser.add_argument("--day-xlsx", type=Path, required=True)
    parser.add_argument("--site-root", type=Path, required=True)
    args = parser.parse_args()

    year_xlsx = args.year_xlsx.resolve()
    day_xlsx = args.day_xlsx.resolve()
    root = args.site_root.resolve()
    data_dir = root / "data"
    index_path = data_dir / "index-data.js"
    calendar_js = root / "js" / "calendar.js"
    if not year_xlsx.is_file():
        raise FileNotFoundError(year_xlsx)
    if not day_xlsx.is_file():
        raise FileNotFoundError(day_xlsx)
    if not data_dir.is_dir() or not index_path.is_file() or not calendar_js.is_file():
        raise RuntimeError(f"Invalid site root: {root}")

    _year_headers, manual_year_overrides = load_year_page(year_xlsx)
    index_prefix, index = load_index(index_path)
    index_by_year = {int(record["year"]): record for record in index["years"]}
    built_titles: dict[int, dict[str, object]] = {}
    daily_row_count = 0
    expected_year = 1
    current_year: int | None = None
    current_rows: list[list[str]] = []

    def flush(year: int, rows_for_year: list[list[str]]) -> None:
        nonlocal expected_year
        if year != expected_year:
            raise RuntimeError(f"Unexpected year order: expected {expected_year:04d}, found {year:04d}")
        title, calendar = build_year(year, rows_for_year, manual_year_overrides.get(year, {}))
        built_titles[year] = title
        output = "window.CalendarData = " + json.dumps(calendar, ensure_ascii=False, separators=(",", ":")) + ";\n"
        (data_dir / f"{year}.js").write_text(output, encoding="utf-8")

        details: list[dict[str, object]] = []
        era_names: list[str] = []
        state_names: list[str] = []
        for group in title["eras"]:
            state_names.append(group["state"])
            for entry in group["entries"]:
                notes = list(entry.get("notes", []))
                note = "\n".join(notes)
                era = str(entry["era"])
                details.append({
                    "state": group["state"],
                    "text": era,
                    "era": era,
                    "note": note,
                    "notes": notes,
                    "fullText": era + ((" " + note) if note else ""),
                })
                era_names.append(era)
        solar = str(title["solarNewYear"])
        solar_year = solar.rsplit("-", 2)[0] if "-" in solar else ""
        index_by_year[year] = {
            "year": year,
            "year4": f"{year:04d}",
            "ganzhi": title["ganzhi"],
            "solarYear": solar_year,
            "solarNewYear": solar,
            "eras": era_names,
            "eraDetails": details,
            "states": state_names,
            "href": f"years/{year}.html",
        }
        expected_year += 1

    for row_number, row in xlsx_rows(day_xlsx, 40):
        if row_number <= 2:
            continue
        year_text = text(row, 3)
        if not year_text.isdigit():
            continue
        year = int(year_text)
        if not 1 <= year <= 500:
            continue
        daily_row_count += 1
        if current_year is None:
            current_year = year
        if year != current_year:
            flush(current_year, current_rows)
            current_year = year
            current_rows = []
        current_rows.append(row)
    if current_year is not None:
        flush(current_year, current_rows)

    if expected_year != 501:
        raise RuntimeError(f"Only rebuilt through year {expected_year - 1:04d}")
    if daily_row_count != 182705:
        raise RuntimeError(f"Expected 182705 日-page records, found {daily_row_count}")

    index["years"] = [index_by_year[year] for year in sorted(index_by_year)]
    index_path.write_text(
        index_prefix + json.dumps(index, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    update_calendar_available(calendar_js, index["years"])

    print(json.dumps({
        "rebuiltYears": len(built_titles),
        "dailyRows": daily_row_count,
        "firstYear": built_titles[1],
        "lastYear": built_titles[500],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
