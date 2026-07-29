from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
ASSOC={'元':'正朔一','明':'正朔二','清':'正朔三'}
SRC={(1836,'清','天命元年'):'《清太祖高皇帝實錄》（康熙本）卷五—卷十',(1846,'清','天命十一年'):'《清太宗文皇帝實錄》卷一'}
reform=re.compile(r'[（(][^）)]*(?:改元|改年)[^）)]*[）)]')

def load(y):
 p=DATA/f'{y}.js'; s=p.read_text(encoding='utf-8')
 m=re.search(r'window\.CalendarData\s*=\s*(\{.*?\});\s*\n\nwindow\.CalendarData\.dayIndex',s,re.S)
 return p,json.loads(m.group(1))
def save(p,d):
 p.write_text('window.CalendarData = '+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n\nwindow.CalendarData.dayIndex = Object.fromEntries(\n  window.CalendarData.months.flatMap(month => month.days.map(day => [`${day.key}|${day.western.date}`, day]))\n);\n',encoding='utf-8')

def clean_entry(x):
 if isinstance(x,str): return reform.sub('',x).strip()
 z=dict(x); z['era']=reform.sub('',z.get('era','')).strip(); return z

# strip reform parentheticals for all 0501-2131
for y in range(501,2132):
 p,d=load(y)
 for e in d.get('title',{}).get('eras',[]):
  e['entries']=[clean_entry(x) for x in e.get('entries',[])]
 save(p,d)


def cn(n):
 ones=['','一','二','三','四','五','六','七','八','九']
 if n<10:return ones[n]
 if n<20:return '十'+ones[n-10]
 if n<100:return ones[n//10]+'十'+ones[n%10]
 return str(n)
def qing_entries(y):
 if 1836<=y<=1846:return [f'天命{cn(y-1835)}年' if y>1836 else '天命元年']
 if 1847<=y<=1855:return [f'天聰{cn(y-1846)}年' if y>1847 else '天聰元年']
 if y==1856:return ['天聰十年','崇德元年']
 ranges=[(1857,1863,'崇德',1855),(1864,1881,'順治',1863),(1882,1942,'康熙',1881),(1943,1955,'雍正',1942),(1956,2015,'乾隆',1955),(2016,2040,'嘉慶',2015),(2041,2070,'道光',2040),(2071,2081,'咸豐',2070),(2082,2094,'同治',2081),(2095,2128,'光緒',2094),(2129,2131,'宣統',2128)]
 for a,b,name,base in ranges:
  if a<=y<=b:
   n=y-base; return [name+('元' if n==1 else cn(n))+'年']
 return []

# rebuild 1501-2131 title eras from daily records, preserving 元/明/清 year-page order
for y in range(1501,2132):
 p,d=load(y); eras=[]
 for state,group in ASSOC.items():
  vals=[]
  for mo in d['months']:
   for day in mo['days']:
    for r in day.get('orthodoxies',[]):
     if r.get('group')==group:
      v=reform.sub('',str(r.get('eraYear') or '')).strip()
      if v and v not in vals: vals.append(v)
  if state=='清' and not vals: vals=qing_entries(y)
  if vals:
   entries=[]
   for v in vals:
    src=SRC.get((y,state,v))
    entries.append({'era':v,'source':src} if src else v)
   eras.append({'state':state,'entries':entries})
 d['title']['eras']=eras
 save(p,d)

# rebuild year index fields from titles
p=DATA/'index-data.js'; s=p.read_text(encoding='utf-8'); obj=json.loads(re.search(r'window\.CalendarIndexData\s*=\s*(\{.*\});',s,re.S).group(1))
for rec in obj['years']:
 y=int(rec['year'])
 if y<501: continue
 _,d=load(y); details=[]; states=[]; era_texts=[]
 for e in d['title'].get('eras',[]):
  st=e['state']; states.append(st)
  for x in e.get('entries',[]):
   if isinstance(x,str): era=x; src=''
   else: era=x.get('era',''); src=x.get('source','')
   details.append({'state':st,'text':era,'fullText':era+(('：'+src) if src else '')})
   era_texts.append(era)
 rec['eras']=era_texts; rec['eraDetails']=details; rec['states']=states
p.write_text('window.CalendarIndexData = '+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
print('done')
