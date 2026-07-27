from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
TRANS={
'正朔一':[
('1501-01C-01','元','忽必烈（世祖）'),('1514-04C-14','元','鐵穆耳（成宗）'),('1527-05C-21','元','海山（武宗）'),('1531-03C-18','元','愛育黎拔力八達（仁宗）'),('1540-03C-11','元','碩德八剌（英宗）'),('1543-09C-04','元','也孫鐵木兒（泰定帝）'),('1548-08C-01','元','阿速吉八（天順帝）'),('1548-09C-13','元','圖帖睦爾（文宗）'),('1549-01C-28','元','和世㻋（明宗）'),('1549-08C-07','元',''),('1549-08C-15','元','圖帖睦爾（文宗）'),('1552-10C-04','元','懿璘質班（寧宗）'),('1552-11C-27','元',''),('1553-06C-08','元','妥懽帖睦爾（順帝）'),('1591-01C-01','','')],
'正朔二':[
('1501-01C-01','',''),('1588-01C-04','明','朱元璋（太祖）'),('1618-05L-16','明','朱允炆（惠帝）'),('1622-06C-17','明','朱棣（成祖）'),('1644-08C-15','明','朱高熾（仁宗）'),('1645-06C-12','明','朱瞻基（宣宗）'),('1655-01C-10','明','朱祁鎮（英宗）'),('1669-09C-06','明','朱祁鈺（代宗）'),('1677-01C-17','明','朱祁鎮（英宗）'),('1684-01C-22','明','朱見深（憲宗）'),('1707-09C-06','明','朱祐樘（孝宗）'),('1725-05C-18','明','朱厚照（武宗）'),('1741-04C-22','明','朱厚熜（世宗）'),('1786-12C-26','明','朱載坖（穆宗）'),('1792-06C-10','明','朱翊鈞（神宗）'),('1802-09C-19','',''),('1802-09C-29','明','朱翊鈞（神宗）'),('1840-08C-01','明','朱常洛（光宗）'),('1840-09C-06','明','朱由校（熹宗）'),('1847-08C-24','明','朱由檢（思宗）'),('1864-03C-20','明',''),('1864-05C-15','明','朱由崧（弘光帝）'),('1865-05C-23','明',''),('1865-06L-27','明','朱聿鍵（隆武帝）'),('1866-08C-29','明',''),('1866-11C-05','明','朱聿鐭（紹武帝）'),('1866-11C-18','明','朱由榔（永曆帝）'),('1882-01C-02','明','鄭成功（延平王）'),('1882-05C-09','明','鄭經（延平王）'),('1901-01C-29','明','鄭克塽（延平王）'),('1903-07C-01','','')],
'正朔三':[
('1501-01C-01','',''),('1864-01C-01','清','福臨（世祖）'),('1881-01C-08','清',''),('1881-01C-09','清','玄燁（聖祖）'),('1942-11C-13','清','胤禛（世宗）'),('1955-08C-24','清',''),('1955-09C-03','清','弘曆（高宗）'),('2016-01C-01','清','顒琰（仁宗）'),('2040-07C-26','清',''),('2040-08C-27','清','旻寧（宣宗）'),('2070-01C-15','清',''),('2070-01C-26','清','奕詝（文宗）'),('2081-07C-18','清',''),('2081-10C-09','清','載淳（穆宗）'),('2094-12C-06','清',''),('2095-01C-20','清','載湉（德宗）'),('2128-10C-22','清',''),('2128-11C-09','清','溥儀（宣統帝）')]
}

def load(y):
 p=ROOT/'data'/f'{y}.js'; s=p.read_text(encoding='utf-8')
 m=re.search(r'window\.CalendarData\s*=\s*(\{.*?\});\s*\n\nwindow\.CalendarData\.dayIndex',s,re.S)
 if not m: raise RuntimeError(f'parse {y}')
 return p,json.loads(m.group(1))
def save(p,d):
 p.write_text('window.CalendarData = '+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n\nwindow.CalendarData.dayIndex = Object.fromEntries(\n  window.CalendarData.months.flatMap(month => month.days.map(day => [`${day.key}|${day.western.date}`, day]))\n);\n',encoding='utf-8')

pos={g:0 for g in TRANS}; cur={g:('','') for g in TRANS}
for y in range(1501,2132):
 p,d=load(y)
 for mo in d['months']:
  for day in mo['days']:
   key=day['chinese']['date']
   for g,arr in TRANS.items():
    while pos[g]<len(arr) and arr[pos[g]][0] <= key:
     _,st,ru=arr[pos[g]]; cur[g]=(st,ru); pos[g]+=1
   recs={r.get('group'):r for r in day.get('orthodoxies',[])}
   for g,(st,ru) in cur.items():
    if g in recs:
     recs[g]['state']=st; recs[g]['ruler']=ru
 save(p,d)

# Rebuild dynasty rulers with stable dynasty windows.
def norm(s): return str(s or '').strip().replace('吳','吴').replace('黃','黄')
pidx=ROOT/'data'/'index-data.js'; txt=pidx.read_text(encoding='utf-8')
obj=json.loads(re.search(r'window\.CalendarIndexData\s*=\s*(\{.*\});',txt,re.S).group(1))
alias={'孫吴':{'吴','吳'},'北魏':{'魏（北）','北魏'},'西魏':{'魏（西）','西魏'},'東魏':{'魏（東）','東魏'},'北齊':{'齊（北）','北齊'},'北周':{'周（北）','北周'},'後梁':{'後梁','梁（後）'},'後唐':{'後唐','唐（後）'},'後晉':{'後晉','晉（後）'},'後漢':{'後漢','漢（後）'},'後周':{'後周','周（後）'}}
overrides={'宋':(1180,1499),'遼':(1127,1400),'金':(1335,1454),'元':(1480,1590),'明':(1588,1903),'清':(1864,2131)}
pat=re.compile(r'"state":"([^"]*)","ruler":"([^"]*)"')
pairs={}
for y in range(200,2132):
 pairs[y]=set(pat.findall((ROOT/'data'/f'{y}.js').read_text(encoding='utf-8')))
new=[]
for d in obj['dynasties']:
 ys=d.get('years',[])
 if not ys: continue
 states=set(map(norm,d.get('states',[])))|set(map(norm,alias.get(d['id'],set())))
 start,end=overrides.get(d['id'],(min(ys),max(ys)))
 found=[]; ry={}
 for y in range(start,end+1):
  hit=False
  for st,ru in pairs[y]:
   if norm(st) in states:
    hit=True
    if ru: ry.setdefault(ru,set()).add(y)
  if hit: found.append(y)
 rulers=[]
 for name,v in ry.items():
  sy=sorted(v); rulers.append({'name':name,'years':sy,'range':f'{sy[0]:04d}年至{sy[-1]:04d}年','count':len(sy)})
 rulers.sort(key=lambda r:(r['years'][0],r['name']))
 nd=dict(d); nd['states']=sorted(states); nd['years']=found
 if found:
  nd['displayRange']=f'{found[0]:04d}年至{found[-1]:04d}年'; nd['displayCount']=f'凡{len(found)}年'
 nd['allRulersLabel']=f'全部國君（{len(rulers)}）'; nd['rulers']=rulers; new.append(nd)
obj['dynasties']=new
pidx.write_text('window.CalendarIndexData = '+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')

lines=['date\tgroup\tstate\truler']
for g,arr in TRANS.items():
 for date,st,ru in arr: lines.append(f'{date}\t{g}\t{st}\t{ru}')
(ROOT/'source'/'1501-2131_君主變更.tsv').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('updated 1501-2131 rulers and index')
