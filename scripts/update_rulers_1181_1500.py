from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
TRANS={
'正朔一':[
('1181-01C-01','宋','趙匡胤（太祖）'),('1196-10C-20','宋','趙炅（太宗）'),('1217-03C-29','宋','趙恆（真宗）'),('1242-02C-01','宋','趙禎（仁宗）'),('1283-04C-01','宋','趙曙（英宗）'),('1287-01C-01','宋','趙頊（神宗）'),('1305-02C-01','宋','趙煦（哲宗）'),('1320-01C-01','宋','趙佶（徽宗）'),('1345-12C-24','宋','趙桓（欽宗）'),('1347-05C-01','宋','趙構（高宗）'),('1382-06C-11','宋','趙昚（孝宗）'),('1409-02C-01','宋','趙惇（光宗）'),('1414-07C-03','宋','趙擴（寧宗）'),('1444-08L-03','宋','趙昀（理宗）'),('1484-10C-26','宋','趙禥（度宗）'),('1494-07C-09','宋','趙㬎（恭帝）'),('1496-05C-01','宋','趙昰（端宗）'),('1498-04C-17','宋','趙昺（帝昺）'),('1499-02C-07','','')],
'正朔二':[
('1181-01C-01','遼','耶律璟（穆宗）'),('1189-02C-22','遼','耶律賢（景宗）'),('1202-09C-01','遼','耶律隆緒（聖宗）'),('1251-06C-01','遼','耶律宗真（興宗）'),('1275-08C-01','遼','耶律洪基（道宗）'),('1321-02C-01','遼','耶律延禧（天祚帝）'),('1344-02C-05','遼','耶律大石（德宗）'),('1364-01C-01','遼','蕭塔不煙（感天后）'),('1371-01C-01','遼',''),('1384-01C-01','遼','耶律普速完（承天后）'),('1398-01C-01','遼','耶律直魯古（末主）'),('1401-01C-01','',''),('1480-01C-01','元',''),('1480-05C-19','元','忽必烈（世祖）')],
'正朔三':[
('1335-01C-01','金','完顏阿骨打（太祖）'),('1343-09C-16','金','完顏晟（太宗）'),('1355-01C-01','金','完顏亶（熙宗）'),('1369-12C-01','金','完顏亮（海陵王）'),('1381-10C-01','金','完顏雍（世宗）'),('1410-01C-01','金','完顏璟（章宗）'),('1428-11C-01','金','完顏永濟（衛紹王）'),('1429-01C-02','金','完顏璟（章宗）'),('1429-01C-28','金','完顏永濟（衛紹王）'),('1433-09C-01','金','完顏珣（宣宗）'),('1444-01C-01','金','完顏守緒（哀宗）'),('1454-01C-11','','')]
}

def load(y):
 p=ROOT/'data'/f'{y}.js'; s=p.read_text(encoding='utf-8')
 m=re.search(r'window\.CalendarData\s*=\s*(\{.*?\});\s*\n\nwindow\.CalendarData\.dayIndex',s,re.S)
 if not m: raise RuntimeError(f'parse {y}')
 return p,json.loads(m.group(1))
def save(p,d):
 p.write_text('window.CalendarData = '+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n\nwindow.CalendarData.dayIndex = Object.fromEntries(\n  window.CalendarData.months.flatMap(month => month.days.map(day => [`${day.key}|${day.western.date}`, day]))\n);\n',encoding='utf-8')

pos={g:0 for g in TRANS}; cur={g:('','') for g in TRANS}
for y in range(1181,1501):
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

# Rebuild dynasty rulers, preserving dynasty-specific historical windows.
def norm(s): return str(s or '').strip().replace('吳','吴').replace('黃','黄')
pidx=ROOT/'data'/'index-data.js'; txt=pidx.read_text(encoding='utf-8')
obj=json.loads(re.search(r'window\.CalendarIndexData\s*=\s*(\{.*\});',txt,re.S).group(1))
alias={'孫吴':{'吴','吳'},'北魏':{'魏（北）','北魏'},'西魏':{'魏（西）','西魏'},'東魏':{'魏（東）','東魏'},'北齊':{'齊（北）','北齊'},'北周':{'周（北）','北周'},'後梁':{'後梁','梁（後）'},'後唐':{'後唐','唐（後）'},'後晉':{'後晉','晉（後）'},'後漢':{'後漢','漢（後）'},'後周':{'後周','周（後）'}}
overrides={'宋':(1180,1499),'遼':(1127,1400),'金':(1335,1454),'元':(1480,1590)}
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

# Save extracted transition source.
lines=['date\tgroup\tstate\truler']
for g,arr in TRANS.items():
 for date,st,ru in arr: lines.append(f'{date}\t{g}\t{st}\t{ru}')
(ROOT/'source'/'1181-1500_君主變更.tsv').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('updated 1181-1500 rulers and index')
