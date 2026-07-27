from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'data'/'index-data.js'
s=p.read_text(encoding='utf-8'); obj=json.loads(re.search(r'window\.CalendarIndexData\s*=\s*(\{.*\});',s,re.S).group(1))

def norm(s): return str(s or '').strip().replace('吳','吴').replace('黃','黄')
alias={'孫吴':{'吴','吳'},'北魏':{'魏（北）','北魏'},'西魏':{'魏（西）','西魏'},'東魏':{'魏（東）','東魏'},'北齊':{'齊（北）','北齊'},'北周':{'周（北）','北周'},'後梁':{'後梁','梁（後）'},'後唐':{'後唐','唐（後）'},'後晉':{'後晉','晉（後）'},'後漢':{'後漢','漢（後）'},'後周':{'後周','周（後）'}}
# Unique state/ruler pairs per year, direct regex for speed.
pairs={}
pat=re.compile(r'"state":"([^"]*)","ruler":"([^"]*)"')
for y in range(200,2132):
 txt=(ROOT/'data'/f'{y}.js').read_text(encoding='utf-8')
 pairs[y]=set(pat.findall(txt))
new=[]
for d in obj['dynasties']:
 ys=d.get('years',[])
 if not ys: continue
 states=set(map(norm,d.get('states',[])))|set(map(norm,alias.get(d['id'],set())))
 start,end=min(ys),max(ys); foundyears=[]; ry={}
 for y in range(start,end+1):
  hit=False
  for st,ru in pairs[y]:
   if norm(st) in states:
    hit=True
    if ru: ry.setdefault(ru,set()).add(y)
  if hit: foundyears.append(y)
 rulers=[]
 for name,v in ry.items():
  sy=sorted(v);rulers.append({'name':name,'years':sy,'range':f'{sy[0]:04d}年至{sy[-1]:04d}年','count':len(sy)})
 rulers.sort(key=lambda r:(r['years'][0],r['name']))
 nd=dict(d); nd['states']=sorted(states); nd['years']=foundyears
 if foundyears:
  nd['displayRange']=f'{foundyears[0]:04d}年至{foundyears[-1]:04d}年';nd['displayCount']=f'凡{len(foundyears)}年'
 nd['allRulersLabel']=f'全部國君（{len(rulers)}）';nd['rulers']=rulers
 new.append(nd)
obj['dynasties']=new
p.write_text('window.CalendarIndexData = '+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
print('rebuilt',[(x['id'],len(x['rulers'])) for x in new])
