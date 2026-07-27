from pathlib import Path
import json,re,zipfile
ROOT=Path(__file__).resolve().parents[1]

# Source-derived transition points from Google Sheet 日_0801-1180.
# Each tuple: Chinese date, state, ruler. Values remain active until next transition.
TRANS={
'正朔一':[
('0801-01C-01','陳','陳頊（宣帝）'),('0802-01C-09','陳',''),('0802-01C-12','陳','陳叔寶（後主）'),
('0809-01C-20','',''),('0837-11C-15','隋','楊侑（恭帝）'),('0838-03C-12','隋','楊侑（恭帝）'),
('0838-05C-20','唐','李淵（高祖）'),('0846-08C-09','唐','李世民（太宗）'),('0869-06C-01','唐','李治（高宗）'),
('0903-12C-09','唐','李顯（中宗）'),('0904-02C-07','唐','李旦（睿宗）'),('0910-09C-09','唐','武曌（則天皇帝）'),
('0925-01C-25','唐','李顯（中宗）'),('0930-06C-07','唐','李重茂（殤帝）'),('0930-06C-24','唐','李旦（睿宗）'),
('0932-08C-03','唐','李隆基（玄宗）'),('0975-11C-25','唐','李亨（肅宗）'),('0982-12C-13','唐','李豫（代宗）'),
('0999-11C-20','唐','李適（德宗）'),('1024-11C-27','唐','李誦（順宗）'),('1025-08C-09','唐','李純（憲宗）'),
('1040-01L-03','唐','李恆（穆宗）'),('1044-01C-26','唐','李湛（敬宗）'),('1046-12C-12','唐','李昂（文宗）'),
('1060-01C-04','唐','李炎（武宗）'),('1066-03C-03','唐','李忱（宣宗）'),('1079-08C-13','唐','李漼（懿宗）'),
('1093-07C-20','唐','李儇（僖宗）'),('1108-03C-08','唐','李曄（昭宗）'),('1124-08C-09','唐','李柷（哀帝）'),
('1127-01C-13','唐','李柷（哀帝）'),('1127-04C-18','梁（後）','朱溫（太祖）'),('1132-06C-03','梁（後）','朱友珪（郢王）'),
('1133-02C-17','梁（後）','朱友貞（末帝）'),('1143-10C-09','唐（後）','李存勗（莊宗）'),('1146-04C-02','唐（後）',''),
('1146-04C-20','唐（後）','李嗣源（明宗）'),('1153-11C-27','唐（後）',''),('1153-12C-01','唐（後）','李從厚（閔帝）'),
('1154-04C-05','唐（後）',''),('1154-04C-06','唐（後）','李從珂（末帝）'),('1156-11L-27','晉（後）','石敬瑭（高祖）'),
('1162-06C-13','晉（後）','石重貴（出帝）'),('1166-12C-18','晉（後）',''),('1167-02C-15','漢（後）','劉知遠（高祖）'),
('1168-01C-28','漢（後）',''),('1168-02C-01','漢（後）','劉承祐（隱帝）'),('1170-11C-23','漢（後）',''),
('1171-01C-05','周（後）','郭威（太祖）'),('1174-01C-18','周（後）',''),('1174-01C-21','周（後）','柴榮（世宗）'),
('1179-06C-20','周（後）','柴宗訓（恭帝）'),('1180-01C-05','宋','趙匡胤（太祖）')],
'正朔二':[
('0801-01C-01','北周','宇文闡（靜帝）'),('0801-02C-13','隋','楊堅（文帝）'),('0824-07C-13','隋','楊廣（煬帝）'),
('0837-11C-15','隋','楊廣（煬帝）'),('0838-03C-12','',''),('1127-01C-13','遼','耶律阿保機（太祖）'),
('1146-07C-28','遼',''),('1147-11C-15','遼','耶律德光（太宗）'),('1167-04C-23','遼','耶律阮（世宗）'),
('1171-09C-05','遼',''),('1171-09C-08','遼','耶律璟（穆宗）')],
'正朔三':[]}

def load(y):
 p=ROOT/'data'/f'{y}.js'; s=p.read_text(encoding='utf-8')
 m=re.search(r'window\.CalendarData\s*=\s*(\{.*?\});\s*\n\nwindow\.CalendarData\.dayIndex',s,re.S)
 if not m: raise RuntimeError(f'parse {y}')
 return p,json.loads(m.group(1))

def save(p,d):
 text='window.CalendarData = '+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n\nwindow.CalendarData.dayIndex = Object.fromEntries(\n  window.CalendarData.months.flatMap(month => month.days.map(day => [`${day.key}|${day.western.date}`, day]))\n);\n'
 p.write_text(text,encoding='utf-8')

# Update state/ruler from transition table, preserving all other source-generated fields.
pos={g:0 for g in TRANS}; current={g:('','') for g in TRANS}
for y in range(801,1181):
 p,d=load(y)
 for mo in d['months']:
  for day in mo['days']:
   key=day['chinese']['date']
   for g,arr in TRANS.items():
    while pos[g] < len(arr) and arr[pos[g]][0] <= key:
     _,st,ru=arr[pos[g]]; current[g]=(st,ru); pos[g]+=1
   recs={r.get('group'):r for r in day.get('orthodoxies',[])}
   for g,(st,ru) in current.items():
    if g in recs:
     recs[g]['state']=st
     recs[g]['ruler']=ru
 save(p,d)

# Rebuild index from all yearly daily data, with robust state aliases.
def norm(s):
 return str(s or '').strip().replace('吳','吴').replace('黃','黄')
def details_from_title(t):
 out=[]
 for eg in t.get('eras',[]):
  for entry in eg.get('entries',[]):
   short=re.sub(r'（.*?）|\(.*?\)','',entry).strip()
   out.append({'state':eg.get('state',''),'text':short,'fullText':entry})
 return out

datasets={}; years=[]
for y in range(200,2132):
 _,d=load(y); datasets[y]=d; t=d['title']; det=details_from_title(t)
 years.append({'year':y,'year4':f'{y:04d}','href':f'years/{y}.html','ganzhi':t.get('ganzhi',''),
 'solarYear':t.get('solarNewYear','').split('-')[0],'eras':[x['text'] for x in det],
 'states':list(dict.fromkeys(x['state'] for x in det)),'eraDetails':det})

oldtxt=(ROOT/'data'/'index-data.js').read_text(encoding='utf-8')
old=json.loads(re.search(r'window\.CalendarIndexData\s*=\s*(\{.*\});',oldtxt,re.S).group(1))
alias={
 '孫吴':{'吴','吳'},'北魏':{'魏（北）','北魏'},'西魏':{'魏（西）','西魏'},'東魏':{'魏（東）','東魏'},
 '北齊':{'齊（北）','北齊'},'北周':{'周（北）','北周'},
 '後梁':{'後梁','梁（後）'},'後唐':{'後唐','唐（後）'},'後晉':{'後晉','晉（後）'},
 '後漢':{'後漢','漢（後）'},'後周':{'後周','周（後）'} }

specs=[]
for x in old['dynasties']:
 ys=x.get('years',[])
 if not ys: continue
 specs.append((x['id'],x['label'],set(map(norm,x.get('states',[])))|set(map(norm,alias.get(x['id'],set()))),min(ys),max(ys)))

dyn=[]
for did,label,states,start,end in specs:
 dys=[]; ruler_years={}
 for y in range(start,end+1):
  found=False
  for mo in datasets[y]['months']:
   for day in mo['days']:
    for o in day.get('orthodoxies',[]):
     if norm(o.get('state')) in states:
      found=True; rn=str(o.get('ruler') or '').strip()
      if rn: ruler_years.setdefault(rn,set()).add(y)
  if found: dys.append(y)
 rulers=[]
 for name,ys in ruler_years.items():
  sy=sorted(ys); rulers.append({'name':name,'years':sy,'range':f'{sy[0]:04d}年至{sy[-1]:04d}年','count':len(sy)})
 rulers.sort(key=lambda r:(r['years'][0],r['name']))
 if dys:
  dyn.append({'id':did,'label':label,'states':sorted(states),'years':dys,
   'displayRange':f'{dys[0]:04d}年至{dys[-1]:04d}年','displayCount':f'凡{len(dys)}年',
   'allRulersLabel':f'全部國君（{len(rulers)}）','rulers':rulers})
(ROOT/'data'/'index-data.js').write_text('window.CalendarIndexData = '+json.dumps({'years':years,'dynasties':dyn},ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
print('updated rulers and rebuilt index')
