import csv, json, re, shutil
from pathlib import Path

ROOT = Path('/mnt/data/rebuild_1_500')
DAY = Path('/mnt/data/中國歷朝正朔日曆_日頁_1至500_重讀.csv')
MONTH = Path('/mnt/data/中國歷朝正朔日曆_月頁_1至500_重讀.csv')
YEAR = Path('/mnt/data/中國歷朝正朔日曆_年頁_1至500_重讀.csv')

month_names={1:'正月',2:'二月',3:'三月',4:'四月',5:'五月',6:'六月',7:'七月',8:'八月',9:'九月',10:'十月',11:'十一月',12:'十二月'}

def v(row, i):
    return row[i].strip() if i < len(row) and row[i] is not None else ''

def month_name(code):
    m=re.match(r'^(\d{2})([CL])$', code)
    if not m: return code
    n=int(m.group(1))
    return ('閏' if m.group(2)=='L' else '') + month_names.get(n, f'{n}月')

def split_cell(text):
    entries=[]
    current=None
    for raw in str(text or '').splitlines():
        line=raw.strip()
        if not line: continue
        # A new era line starts with an era name and optional full-width/ASCII colon.
        if '：' in line:
            era, note=line.split('：',1)
            current={'era':era.strip(),'notes':[note.strip()] if note.strip() else []}
            entries.append(current)
        elif ':' in line:
            era, note=line.split(':',1)
            current={'era':era.strip(),'notes':[note.strip()] if note.strip() else []}
            entries.append(current)
        elif current and (line.startswith('（') or line.startswith('(') or '《' in line):
            current['notes'].append(line)
        else:
            current={'era':line,'notes':[]}
            entries.append(current)
    return entries

# Read year page exactly; do not infer titles from daily data.
years={}
with YEAR.open(encoding='utf-8-sig', newline='') as f:
    rows=list(csv.reader(f))
headers=rows[0]
state_cols=[(headers[i],i) for i in range(7,len(headers))]
for row in rows[1:]:
    if not v(row,0).isdigit(): continue
    y=int(v(row,0))
    if not 1 <= y <= 500: continue
    eras=[]
    for state,col in state_cols:
        entries=split_cell(v(row,col))
        if entries:
            eras.append({'state':state,'entries':entries})
    years[y]={
        'year':f'{y:04d}', 'displayYear':y, 'ganzhi':v(row,1),
        'monthCount':int(v(row,2)) if v(row,2).isdigit() else None,
        'dayCount':int(v(row,3)) if v(row,3).isdigit() else None,
        'yuanriGanzhi':v(row,4), 'solarNewYear':v(row,5),
        'winterSolstice':v(row,6), 'eras':eras
    }

# Read all daily records 1-500.
days_by_year={y:[] for y in range(1,501)}
with DAY.open(encoding='utf-8-sig', newline='') as f:
    r=csv.reader(f)
    top=next(r); hdr=next(r)
    for row in r:
        cy=v(row,3)
        if not cy.isdigit(): continue
        y=int(cy)
        if not 1 <= y <= 500: continue
        day={
            'key':v(row,0), 'ganzhi':v(row,1), 'weekday':v(row,9),
            'chinese':{'date':v(row,0),'year':cy,'month':v(row,4),'day':v(row,5),'calendar':v(row,16)},
            'western':{'date':v(row,2),'year':v(row,6),'month':v(row,7),'day':v(row,8),'calendar':v(row,17)},
            'astronomy':{'syzygy':v(row,10),'meanSolarTerm':v(row,11),'moonPhase':v(row,12),'trueSolarTerm':v(row,13),'solarEclipse':v(row,14),'lunarEclipse':v(row,15)},
            'orthodoxies':[],
            'events':{'calendarChange':v(row,36),'newRuler':v(row,37),'eraChange':v(row,38),'source':v(row,39)}
        }
        for gi,start in enumerate((18,24,30),1):
            state=v(row,start)
            if state:
                day['orthodoxies'].append({'group':f'正朔{"一二三"[gi-1]}','state':state,'ruler':v(row,start+1),'eraYear':v(row,start+2),'month':v(row,start+3),'day':v(row,start+4),'calendar':v(row,start+5)})
        days_by_year[y].append(day)

# Month tab is reread and archived. Its exported duplicate currently contains formula errors,
# so daily rows remain the authoritative source for month boundaries and month lengths.
month_rows=[]
with MONTH.open(encoding='utf-8-sig', newline='') as f:
    month_rows=list(csv.reader(f))

# Build all 500 data files.
for y in range(1,501):
    ds=days_by_year[y]
    if not ds: raise RuntimeError(f'No daily rows for {y}')
    months=[]; cur=None
    for d in ds:
        code=d['chinese']['month']
        if cur is None or cur['id'] != code:
            cur={'id':code,'name':month_name(code),'isLeap':code.endswith('L'),'daysInMonth':0,'days':[]}
            months.append(cur)
        cur['days'].append(d); cur['daysInMonth']+=1
    title=years[y]
    # Formula-error fields in early year-page export are recovered from the freshly reread day page.
    if not title.get('solarNewYear') or title['solarNewYear'].startswith('#'):
        title['solarNewYear']=ds[0]['western']['date']
    if not title.get('yuanriGanzhi') or title['yuanriGanzhi'].startswith('#'):
        title['yuanriGanzhi']=ds[0]['ganzhi']
    if not title.get('monthCount'):
        title['monthCount']=len(months)
    if not title.get('dayCount'):
        title['dayCount']=len(ds)
    obj={'year':f'{y:04d}','displayYear':y,'title':title,'months':months}
    (ROOT/'data'/f'{y}.js').write_text('window.CalendarData = '+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')

# Update index years 1-500 strictly from year-page titles.
p=ROOT/'data/index-data.js'
s=p.read_text(encoding='utf-8')
prefix='window.CalendarIndexData = '
obj=json.loads(s[len(prefix):].rstrip().rstrip(';'))
by={int(x['year']):x for x in obj['years']}
for y in range(1,501):
    t=years[y]; details=[]; eras=[]; states=[]
    for group in t['eras']:
        states.append(group['state'])
        for ent in group['entries']:
            note='\n'.join(ent.get('notes',[]))
            details.append({'state':group['state'],'text':ent['era'],'era':ent['era'],'note':note,'notes':ent.get('notes',[]),'fullText':ent['era'] + ((' '+note) if note else '')})
            eras.append(ent['era'])
    solar=t['solarNewYear']; solar_year=solar.rsplit('-',2)[0] if solar and '-' in solar else ''
    by[y]={'year':y,'year4':f'{y:04d}','ganzhi':t['ganzhi'],'solarYear':solar_year,'solarNewYear':solar,'eras':eras,'eraDetails':details,'states':states,'href':f'years/{y}.html'}
obj['years']=sorted(by.values(),key=lambda x:x['year'])
p.write_text(prefix+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')

# Archive every reread tab.
source=ROOT/'source'; source.mkdir(exist_ok=True)
shutil.copy2(YEAR, source/'元表格_年頁_0001-0500_重讀.csv')
shutil.copy2(MONTH, source/'元表格_月頁_0001-0500_重讀.csv')
shutil.copy2(DAY, source/'元表格_日頁_0001-0500_重讀.csv')
print('rebuilt years', len(years), 'days', sum(map(len,days_by_year.values())), 'month snapshot rows',len(month_rows))
