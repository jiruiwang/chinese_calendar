from pathlib import Path
import zipfile,xml.etree.ElementTree as ET,json,re
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/'source'/'川象曆_0501-0800_日表.xlsx'
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
def c(v):
    if v is None:return ''
    s=str(v).strip()
    if re.fullmatch(r'-?\d+\.0',s): s=s[:-2]
    return s.replace('歷','曆').replace('历','曆').replace('錄','録').replace('录','録').replace('吳','吴').replace('黃','黄').replace('陈','陳').replace('后','後')
def cd(v):
    s=c(v);m=re.match(r'^(\d+)-(\d{2}[CL])-(\d{2})$',s);return f'{int(m.group(1)):04d}-{m.group(2)}-{m.group(3)}' if m else s
def wd(v):
    s=c(v);m=re.match(r'^(B?)(\d+)-(\d{2})-(\d{2})$',s);return f'{m.group(1)}{int(m.group(2)):04d}-{m.group(3)}-{m.group(4)}' if m else s
def colnum(ref):
    n=0
    for ch in re.match(r'[A-Z]+',ref).group(): n=n*26+ord(ch)-64
    return n-1
def rows(sheet, shared):
    with zipfile.ZipFile(SRC) as z, z.open(sheet) as f:
        for ev,el in ET.iterparse(f,events=('end',)):
            if el.tag==NS+'row':
                vals=[]
                for ce in el.findall(NS+'c'):
                    idx=colnum(ce.attrib['r'])
                    while len(vals)<=idx: vals.append(None)
                    typ=ce.attrib.get('t'); v=ce.find(NS+'v')
                    if typ=='inlineStr':
                        t=ce.find('.//'+NS+'t'); val=t.text if t is not None else ''
                    elif v is None: val=None
                    elif typ=='s': val=shared[int(v.text)]
                    else: val=v.text
                    vals[idx]=val
                yield vals; el.clear()
def shared_strings():
    out=[]
    with zipfile.ZipFile(SRC) as z, z.open('xl/sharedStrings.xml') as f:
        for ev,el in ET.iterparse(f,events=('end',)):
            if el.tag==NS+'si':
                out.append(''.join(t.text or '' for t in el.iter(NS+'t')));el.clear()
    return out
def mn(code):
    names=['','正月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月']
    return ('閏' if code.endswith('L') else '')+names[int(code[:2])]
def group(r,start,label):
    a=[c(r[start+i]) if start+i<len(r) else '' for i in range(6)]
    return None if not any(a) else {'group':label,'state':a[0],'ruler':a[1],'eraYear':a[2],'month':a[3],'day':a[4],'calendar':a[5]}
def parse_eras(vals):
    out=[]
    for v in vals:
        for line in c(v).splitlines():
            p=line.strip().split(None,1)
            if not p:continue
            st=p[0]; en=p[1] if len(p)>1 else ''
            if out and out[-1]['state']==st: out[-1]['entries'].append(en)
            else: out.append({'state':st,'entries':[en] if en else []})
    return out
ss=shared_strings(); print('shared',len(ss))
meta={}
for i,r in enumerate(rows('xl/worksheets/sheet3.xml',ss)):
    if i==0 or not r or r[0] is None: continue
    y=int(float(r[0]));
    if 501<=y<=800:
        meta[y]={'year':f'{y:04d}','displayYear':y,'ganzhi':c(r[1]),'monthCount':int(float(r[2])),'dayCount':int(float(r[3])),'yuanriGanzhi':c(r[4]),'solarNewYear':wd(r[5]),'winterSolstice':cd(r[6]),'eras':parse_eras(r[7:10])}
months={y:[] for y in range(501,801)}
for i,r in enumerate(rows('xl/worksheets/sheet1.xml',ss)):
    if i<2 or not r or not c(r[0]): continue
    key=cd(r[0]);y=int(key[:4])
    if not 501<=y<=800:continue
    mc=c(r[4]);western=wd(r[2]);wp=western.split('-')
    day={'key':key,'ganzhi':c(r[1]),'weekday':c(r[9]),'chinese':{'date':key,'year':f'{y:04d}','month':mc,'day':c(r[5]).zfill(2),'calendar':c(r[16])},'western':{'date':western,'year':wp[0],'month':wp[1],'day':wp[2],'calendar':c(r[17])},'astronomy':{'syzygy':c(r[10]),'meanSolarTerm':c(r[11]),'moonPhase':c(r[12]),'trueSolarTerm':c(r[13]),'solarEclipse':c(r[14]),'lunarEclipse':c(r[15])},'orthodoxies':[x for x in (group(r,18,'正朔一'),group(r,24,'正朔二'),group(r,30,'正朔三')) if x]}
    if not months[y] or months[y][-1]['id']!=mc or (c(r[5]).zfill(2)=='01' and months[y][-1]['days']): months[y].append({'id':mc,'name':mn(mc),'isLeap':mc.endswith('L'),'daysInMonth':0,'days':[]})
    months[y][-1]['days'].append(day);months[y][-1]['daysInMonth']+=1
for y in range(501,801):
    p={'year':f'{y:04d}','displayYear':y,'title':meta[y],'months':months[y]}
    (ROOT/'data'/f'{y}.js').write_text('window.CalendarData = '+json.dumps(p,ensure_ascii=False,separators=(',',':'))+';\n\nwindow.CalendarData.dayIndex = Object.fromEntries(\n  window.CalendarData.months.flatMap(month => month.days.map(day => [`${day.key}|${day.western.date}`, day]))\n);\n',encoding='utf-8')
print('generated data')
# patch index years only 501-800, preserve others; fix East Han dynasty range/rulers from current daily data 245-440.
ip=ROOT/'data'/'index-data.js'; old=json.loads(re.search(r'=\s*(\{.*\});',ip.read_text(encoding='utf-8'),re.S).group(1))
oldmap={x['year']:x for x in old['years']}
for y in range(501,801):
    t=meta[y]; det=[]
    for g in t['eras']:
        for en in g['entries']:
            det.append({'state':g['state'],'text':re.sub(r'（.*?）|\(.*?\)','',en).strip(),'fullText':en})
    oldmap[y]={'year':y,'year4':f'{y:04d}','href':f'years/{y}.html','ganzhi':t['ganzhi'],'solarYear':t['solarNewYear'].split('-')[0],'eras':[x['text'] for x in det],'states':list(dict.fromkeys(x['state'] for x in det)),'eraDetails':det}
old['years']=[oldmap[y] for y in sorted(oldmap)]
# East Han: include 245-440; derive rulers from day data.
def load(y):
    s=(ROOT/'data'/f'{y}.js').read_text(encoding='utf-8');return json.loads(re.search(r'=\s*(\{.*?\});\s*\n\nwindow.CalendarData.dayIndex',s,re.S).group(1))
eh=next(d for d in old['dynasties'] if d['id']=='東漢'); eh['years']=list(range(245,441));eh['displayRange']='0245年至0440年';eh['displayCount']='凡196年'
ry={}
for y in eh['years']:
    d=load(y)
    for m in d['months']:
        for day in m['days']:
            for o in day.get('orthodoxies',[]):
                if o.get('state')=='漢' and o.get('ruler'): ry.setdefault(o['ruler'],set()).add(y)
eh['rulers']=[]
for name,ys in sorted(ry.items(),key=lambda kv:min(kv[1])):
    a=sorted(ys);eh['rulers'].append({'name':name,'years':a,'range':f'{a[0]:04d}年至{a[-1]:04d}年','count':len(a)})
eh['allRulersLabel']=f'全部國君（{len(eh["rulers"])}）'
ip.write_text('window.CalendarIndexData = '+json.dumps(old,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
print('patched index')
