import csv, json, re, shutil
from pathlib import Path

ROOT=Path('/mnt/data/rebuild500')
DAY=Path('/mnt/data/中國歷朝正朔日曆_日頁_1至500_重讀.csv')
YEAR=Path('/mnt/data/中國歷朝正朔日曆_年頁_1至500_重讀.csv')
MONTH=Path('/mnt/data/中國歷朝正朔日曆_月頁_1至500_重讀.csv')
month_names={1:'正月',2:'二月',3:'三月',4:'四月',5:'五月',6:'六月',7:'七月',8:'八月',9:'九月',10:'十月',11:'十一月',12:'十二月'}

def v(row,i): return row[i].strip() if i<len(row) and row[i] is not None else ''
def month_name(code):
 m=re.match(r'^(\d{2})([CL])$',code)
 if not m:return code
 n=int(m.group(1)); return ('閏' if m.group(2)=='L' else '')+month_names.get(n,f'{n}月')
def is_era_only(line):
 return len(line)<=16 and bool(re.search(r'(?:元|[一二三四五六七八九十百]+)年$',line))
def split_cell(text):
 entries=[]; current=None
 for raw in str(text or '').splitlines():
  line=raw.strip()
  if not line: continue
  sep='：' if '：' in line else (':' if ':' in line else None)
  if sep:
   era,note=line.split(sep,1)
   current={'era':era.strip(),'notes':[note.strip()] if note.strip() else []}; entries.append(current)
  elif is_era_only(line):
   current={'era':line,'notes':[]}; entries.append(current)
  elif current:
   current['notes'].append(line)
  else:
   current={'era':line,'notes':[]}; entries.append(current)
 return entries

# Daily page: authoritative for each date, month boundaries, and fallback annual era.
days_by_year={y:[] for y in range(1,501)}
with DAY.open(encoding='utf-8-sig',newline='') as f:
 r=csv.reader(f); next(r); next(r)
 for row in r:
  cy=v(row,3)
  if not cy.isdigit() or not 1<=int(cy)<=500: continue
  y=int(cy)
  day={'key':v(row,0),'ganzhi':v(row,1),'weekday':v(row,9),
       'chinese':{'date':v(row,0),'year':cy,'month':v(row,4),'day':v(row,5),'calendar':v(row,16)},
       'western':{'date':v(row,2),'year':v(row,6),'month':v(row,7),'day':v(row,8),'calendar':v(row,17)},
       'astronomy':{'syzygy':v(row,10),'meanSolarTerm':v(row,11),'moonPhase':v(row,12),'trueSolarTerm':v(row,13),'solarEclipse':v(row,14),'lunarEclipse':v(row,15)},
       'orthodoxies':[],
       'events':{'calendarChange':v(row,36),'newRuler':v(row,37),'eraChange':v(row,38),'source':v(row,39)}}
  for gi,start in enumerate((18,24,30),1):
   state=v(row,start)
   if state: day['orthodoxies'].append({'group':f'正朔{"一二三"[gi-1]}','state':state,'ruler':v(row,start+1),'eraYear':v(row,start+2),'month':v(row,start+3),'day':v(row,start+4),'calendar':v(row,start+5)})
  days_by_year[y].append(day)

# Year page explicit cells override daily fallback; blank cells are completed from the final date of that state's annual record.
raw={}
with YEAR.open(encoding='utf-8-sig',newline='') as f:
 rows=list(csv.reader(f))
headers=rows[0]; states=headers[7:14]
for row in rows[1:]:
 if v(row,0).isdigit() and 1<=int(v(row,0))<=500: raw[int(v(row,0))]=row

def final_era_for_state(ds,state):
 aliases={state,state.replace('吴','吳'),state.replace('吳','吴')}
 for d in reversed(ds):
  for o in reversed(d['orthodoxies']):
   if o['state'] in aliases and o['eraYear']:
    return o['eraYear']
 return ''

years={}
for y in range(1,501):
 row=raw.get(y,[]); ds=days_by_year[y]
 if not ds: raise RuntimeError(f'No daily rows for {y}')
 eras=[]
 for idx,state in enumerate(states,7):
  cell=v(row,idx)
  entries=split_cell(cell) if cell else []
  if not entries:
   fallback=final_era_for_state(ds,state)
   if fallback: entries=[{'era':fallback,'notes':[]}]
  if entries: eras.append({'state':state,'entries':entries})
 years[y]={'year':f'{y:04d}','displayYear':y,'ganzhi':v(row,1) or ds[0]['ganzhi'],
  'monthCount':int(v(row,2)) if v(row,2).isdigit() else None,
  'dayCount':int(v(row,3)) if v(row,3).isdigit() else len(ds),
  'yuanriGanzhi':v(row,4) if v(row,4) and not v(row,4).startswith('#') else ds[0]['ganzhi'],
  'solarNewYear':v(row,5) if v(row,5) and not v(row,5).startswith('#') else ds[0]['western']['date'],
  'winterSolstice':v(row,6) if v(row,6) and not v(row,6).startswith('#') else '',
  'eras':eras}

for y in range(1,501):
 ds=days_by_year[y]; months=[]; cur=None
 for d in ds:
  code=d['chinese']['month']
  if cur is None or cur['id']!=code:
   cur={'id':code,'name':month_name(code),'isLeap':code.endswith('L'),'daysInMonth':0,'days':[]}; months.append(cur)
  cur['days'].append(d); cur['daysInMonth']+=1
 years[y]['monthCount']=years[y]['monthCount'] or len(months)
 obj={'year':f'{y:04d}','displayYear':y,'title':years[y],'months':months}
 (ROOT/'data'/f'{y}.js').write_text('window.CalendarData = '+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')

p=ROOT/'data/index-data.js'; s=p.read_text(encoding='utf-8'); prefix='window.CalendarIndexData = '
obj=json.loads(s[len(prefix):].rstrip().rstrip(';')); by={int(x['year']):x for x in obj['years']}
for y,t in years.items():
 details=[]; era_names=[]; state_names=[]
 for group in t['eras']:
  state_names.append(group['state'])
  for ent in group['entries']:
   notes=ent.get('notes',[]); note='\n'.join(notes)
   details.append({'state':group['state'],'text':ent['era'],'era':ent['era'],'note':note,'notes':notes,'fullText':ent['era']+((' '+note) if note else '')}); era_names.append(ent['era'])
 solar=t['solarNewYear']; solar_year=solar.rsplit('-',2)[0] if '-' in solar else ''
 by[y]={'year':y,'year4':f'{y:04d}','ganzhi':t['ganzhi'],'solarYear':solar_year,'solarNewYear':solar,'eras':era_names,'eraDetails':details,'states':state_names,'href':f'years/{y}.html'}
obj['years']=sorted(by.values(),key=lambda x:x['year']); p.write_text(prefix+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')

source=ROOT/'source'; source.mkdir(exist_ok=True)
shutil.copy2(YEAR,source/'元表格_年頁_0001-0500_重讀.csv'); shutil.copy2(DAY,source/'元表格_日頁_0001-0500_重讀.csv'); shutil.copy2(MONTH,source/'元表格_月頁_0001-0500_重讀.csv')
print('rebuilt',len(years),'years',sum(len(x) for x in days_by_year.values()),'days')
