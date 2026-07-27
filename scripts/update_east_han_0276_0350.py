from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
BOUNDARIES='''
0276-01C-01\t建武中元元年
0277-01C-01\t建武中元二年
0278-01C-01\t永平元年
0279-01C-01\t永平二年
0280-01C-01\t永平三年
0281-01C-01\t永平四年
0282-01C-01\t永平五年
0283-01C-01\t永平六年
0284-01C-01\t永平七年
0285-01C-01\t永平八年
0286-01C-01\t永平九年
0287-01C-01\t永平十年
0288-01C-01\t永平十一年
0289-01C-01\t永平十二年
0290-01C-01\t永平十三年
0291-01C-01\t永平十四年
0292-01C-01\t永平十五年
0293-01C-01\t永平十六年
0294-01C-01\t永平十七年
0295-01C-01\t永平十八年
0296-01C-01\t建初元年
0297-01C-01\t建初二年
0298-01C-01\t建初三年
0299-01C-01\t建初四年
0300-01C-01\t建初五年
0301-01C-01\t建初六年
0302-01C-01\t建初七年
0303-01C-01\t建初八年
0304-01C-01\t建初九年
0304-08C-20\t元和元年
0305-01C-01\t元和二年
0306-01C-01\t元和三年
0307-01C-01\t元和四年
0307-07C-26\t章和元年
0308-01C-01\t章和二年
0309-01C-01\t永元元年
0310-01C-01\t永元二年
0311-01C-01\t永元三年
0312-01C-01\t永元四年
0313-01C-01\t永元五年
0314-01C-01\t永元六年
0315-01C-01\t永元七年
0316-01C-01\t永元八年
0317-01C-01\t永元九年
0318-01C-01\t永元十年
0319-01C-01\t永元十一年
0320-01C-01\t永元十二年
0321-01C-01\t永元十三年
0322-01C-01\t永元十四年
0323-01C-01\t永元十五年
0324-01C-01\t永元十六年
0325-01C-01\t永元十七年
0325-05C-18\t元興元年
0326-01C-01\t延平元年
0327-01C-01\t永初元年
0328-01C-01\t永初二年
0329-01C-01\t永初三年
0330-01C-01\t永初四年
0331-01C-01\t永初五年
0332-01C-01\t永初六年
0333-01C-01\t永初七年
0334-01C-01\t永初八年
0334-01C-02\t元初元年
0335-01C-01\t元初二年
0336-01C-01\t元初三年
0337-01C-01\t元初四年
0338-01C-01\t元初五年
0339-01C-01\t元初六年
0340-01C-01\t元初七年
0340-04C-10\t永寧元年
0341-01C-01\t永寧二年
0341-07C-01\t建光元年
0342-01C-01\t建光二年
0342-03C-02\t延光元年
0343-01C-01\t延光二年
0344-01C-01\t延光三年
0345-01C-01\t延光四年
0346-01C-01\t永建元年
0347-01C-01\t永建二年
0348-01C-01\t永建三年
0349-01C-01\t永建四年
0350-01C-01\t永建五年
'''.strip()

bounds={}
for line in BOUNDARIES.splitlines():
    k,e=line.split('\t')
    bounds.setdefault(int(k[:4]),[]).append((k,e))

CN_MONTH={'01C':'正月','02C':'二月','03C':'三月','04C':'四月','05C':'五月','06C':'六月','07C':'七月','08C':'八月','09C':'九月','10C':'十月','11C':'十一月','12C':'十二月',
          '01L':'閏正月','02L':'閏二月','03L':'閏三月','04L':'閏四月','05L':'閏五月','06L':'閏六月','07L':'閏七月','08L':'閏八月','09L':'閏九月','10L':'閏十月','11L':'閏十一月','12L':'閏十二月'}
CN_NUM={1:'一',2:'二',3:'三',4:'四',5:'五',6:'六',7:'七',8:'八',9:'九',10:'十',11:'十一',12:'十二',13:'十三',14:'十四',15:'十五',16:'十六',17:'十七',18:'十八',19:'十九',20:'二十',21:'二十一',22:'二十二',23:'二十三',24:'二十四',25:'二十五',26:'二十六',27:'二十七',28:'二十八',29:'二十九',30:'三十'}

def load(y):
    p=ROOT/'data'/f'{y}.js'; s=p.read_text(encoding='utf-8')
    m=re.search(r'window\.CalendarData\s*=\s*(\{.*?\});\s*\n\nwindow\.CalendarData\.dayIndex',s,re.S)
    return p,json.loads(m.group(1))

def save(p,d):
    p.write_text('window.CalendarData = '+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n\nwindow.CalendarData.dayIndex = Object.fromEntries(\n  window.CalendarData.months.flatMap(month => month.days.map(day => [`${day.key}|${day.western.date}`, day]))\n);\n',encoding='utf-8')

def rebuild_title(d):
    first_key=d['months'][0]['days'][0]['key']
    order=[]; entries={}; seen=set()
    for m in d['months']:
        for day in m['days']:
            for rec in day.get('orthodoxies',[]):
                st=rec.get('state',''); era=rec.get('eraYear','')
                if not st or not era: continue
                if st not in entries: entries[st]=[]; order.append(st)
                pair=(st,era)
                if pair in seen: continue
                seen.add(pair)
                label=era
                if day['key']!=first_key:
                    label=f"{era}（{rec.get('month','')}{rec.get('day','')}改元）"
                entries[st].append(label)
    d['title']['eras']=[{'state':st,'entries':entries[st]} for st in order]

changed=0
for y in range(276,351):
    p,d=load(y)
    b=dict(bounds[y]); current=None
    for m in d['months']:
        for day in m['days']:
            if day['key'] in b: current=b[day['key']]
            if current is None: raise RuntimeError((y,day['key']))
            for rec in day.get('orthodoxies',[]):
                if rec.get('group')=='正朔一' and rec.get('state')=='漢':
                    if rec.get('eraYear')!=current: changed+=1
                    rec['eraYear']=current
    rebuild_title(d); save(p,d)

# Incorporate the subsequently re-read source corrections already requested by the user.
# 0352: 陽嘉元年 begins 正月二十八日.
for y, changes in {352:[('0352-01C-01','永建七年'),('0352-01C-28','陽嘉元年')],
                   392:[('0392-01C-01','建寧五年'),('0392-05C-16','熹平元年')]}.items():
    p,d=load(y); b=dict(changes); current=None
    for m in d['months']:
        for day in m['days']:
            if day['key'] in b: current=b[day['key']]
            for rec in day.get('orthodoxies',[]):
                if rec.get('group')=='正朔一' and rec.get('state')=='漢': rec['eraYear']=current
    rebuild_title(d); save(p,d)

# 0377 source now aligns 漢 date with 中曆 date; undo the earlier one-day manual offset.
p,d=load(377)
for m in d['months']:
    for day in m['days']:
        key=day['key']; mid=key[5:8]; n=int(key[-2:])
        for rec in day.get('orthodoxies',[]):
            if rec.get('group')=='正朔一' and rec.get('state')=='漢':
                rec['eraYear']='永壽三年'; rec['month']=CN_MONTH[mid]; rec['day']=CN_NUM[n]+'日'
rebuild_title(d); save(p,d)

# Rebuild index records for every touched year.
ip=ROOT/'data'/'index-data.js'; txt=ip.read_text(encoding='utf-8')
obj=json.loads(re.search(r'window\.CalendarIndexData\s*=\s*(\{.*\});',txt,re.S).group(1))
mp={x['year']:x for x in obj['years']}
for y in list(range(276,351))+[352,377,388,392]:
    _,d=load(y); t=d['title']; details=[]
    for g in t.get('eras',[]):
        for full in g.get('entries',[]):
            base=re.sub(r'（.*?）|\(.*?\)','',full).strip()
            details.append({'state':g['state'],'text':base,'fullText':full})
    mp[y]={'year':y,'year4':f'{y:04d}','href':f'years/{y}.html','ganzhi':t['ganzhi'],'solarYear':t['solarNewYear'].split('-')[0],
           'eras':[x['text'] for x in details],'states':list(dict.fromkeys(x['state'] for x in details)),'eraDetails':details}
obj['years']=[mp[y] for y in sorted(mp)]
ip.write_text('window.CalendarIndexData = '+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')

(ROOT/'source'/'0276-0350_年號分界_重讀.tsv').write_text('中曆紀日\t年號\n'+BOUNDARIES+'\n',encoding='utf-8')
print('daily era values changed in 0276-0350:',changed)
