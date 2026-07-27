#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = {
    373: ("元嘉二年", "元嘉三年（中曆正月二日）"),
    377: ("永壽二年", "永壽三年（中曆正月二日）"),
}
SUFFIX = "\n\nwindow.CalendarData.dayIndex = Object.fromEntries(\n  window.CalendarData.months.flatMap(month => month.days.map(day => [`${day.key}|${day.western.date}`, day]))\n);\n"

def load_js(path):
    text = path.read_text(encoding='utf-8')
    body = text[len('window.CalendarData = '):].split(';\n\nwindow.CalendarData.dayIndex', 1)[0]
    return json.loads(body)

def save_js(path, data):
    path.write_text('window.CalendarData = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';' + SUFFIX, encoding='utf-8')

def repair_year(year, entries):
    path = ROOT / 'data' / f'{year}.js'
    d = load_js(path)
    rogue, first = d['months'][0], d['months'][1]
    assert rogue['id'] == '12C' and len(rogue['days']) == 1
    assert first['id'] == '01C'
    first_day = rogue['days'][0]
    first_day['key'] = f'{year:04d}-01C-01'
    first_day['chinese'].update(date=first_day['key'], month='01C', day='01')
    shifted = []
    for day in first['days']:
        n = int(day['chinese']['day']) + 1
        day['key'] = f'{year:04d}-01C-{n:02d}'
        day['chinese'].update(date=day['key'], month='01C', day=f'{n:02d}')
        shifted.append(day)
    first['days'] = [first_day] + shifted
    first['daysInMonth'] = len(first['days'])
    d['months'] = [first] + d['months'][2:]
    d['title']['monthCount'] = len(d['months'])
    d['title']['eras'] = [{'state': '漢', 'entries': list(entries)}]
    save_js(path, d)

for y, entries in CASES.items():
    repair_year(y, entries)

# Patch year-card index details without rebuilding unrelated content.
ip = ROOT / 'data' / 'index-data.js'
text = ip.read_text(encoding='utf-8')
prefix = 'window.CalendarIndexData = '
obj = json.loads(text[len(prefix):].rstrip().rstrip(';'))
for item in obj['years']:
    if item['year'] in CASES:
        entries = CASES[item['year']]
        item['eras'] = list(entries)
        item['eraDetails'] = [
            {'state':'漢','text':entries[0],'fullText':entries[0]},
            {'state':'漢','text':entries[1].split('（',1)[0],'fullText':entries[1]},
        ]
ip.write_text(prefix + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
