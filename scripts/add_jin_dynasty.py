from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'data'/'index-data.js'; s=p.read_text(encoding='utf-8'); obj=json.loads(re.search(r'=\s*(\{.*\});',s,re.S).group(1))
pat=re.compile(r'"state":"([^"]*)","ruler":"([^"]*)"')
found=[]; ry={}
for y in range(1335,1455):
 pairs=set(pat.findall((ROOT/'data'/f'{y}.js').read_text(encoding='utf-8')))
 hit=False
 for st,ru in pairs:
  if st=='金':
   hit=True
   if ru: ry.setdefault(ru,set()).add(y)
 if hit: found.append(y)
rulers=[]
for name,v in ry.items():
 ys=sorted(v); rulers.append({'name':name,'years':ys,'range':f'{ys[0]:04d}年至{ys[-1]:04d}年','count':len(ys)})
rulers.sort(key=lambda r:(r['years'][0],r['name']))
entry={'id':'金','label':'金','states':['金'],'years':found,'displayRange':f'{found[0]:04d}年至{found[-1]:04d}年','displayCount':f'凡{len(found)}年','allRulersLabel':f'全部國君（{len(rulers)}）','rulers':rulers}
obj['dynasties']=[d for d in obj['dynasties'] if d['id']!='金']
pos=next(i for i,d in enumerate(obj['dynasties']) if d['id']=='元')
obj['dynasties'].insert(pos,entry)
p.write_text('window.CalendarIndexData = '+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
print(entry['displayRange'],len(rulers),[r['name'] for r in rulers])
