import csv, json, re
from pathlib import Path

ROOT=Path('/mnt/data/update_year_day_clean')
DAY=Path('/mnt/data/川象曆_日頁_重讀臨時.csv')
YEAR=Path('/mnt/data/川象曆_年頁_重讀臨時.csv')

state_cols=[('漢',7),('魏',8),('晉',9),('漢（蜀）',10),('吴',11)]
month_names={1:'正月',2:'二月',3:'三月',4:'四月',5:'五月',6:'六月',7:'七月',8:'八月',9:'九月',10:'十月',11:'十一月',12:'十二月'}

def val(row,i): return row[i].strip() if i < len(row) and row[i] is not None else ''
def parse_title_cell(text):
    out=[]
    for raw in text.splitlines():
        raw=raw.strip()
        if not raw: continue
        if '：' in raw:
            era,note=raw.split('：',1)
        elif ':' in raw:
            era,note=raw.split(':',1)
        else:
            era,note=raw,''
        out.append({'era':era.strip(),'note':note.strip()})
    return out

def month_name(code):
    m=re.match(r'^(\d{2})([CL])$',code)
    if not m:return code
    n=int(m.group(1)); return ('閏' if m.group(2)=='L' else '')+month_names.get(n,str(n)+'月')

# year page
ymeta={}
with YEAR.open(encoding='utf-8-sig',newline='') as f:
    rows=list(csv.reader(f))
for row in rows[1:]:
    if not row or not val(row,0): continue
    y=int(val(row,0))
    if not 200<=y<=500: continue
    eras=[]
    for state,col in state_cols:
        entries=parse_title_cell(val(row,col))
        if entries: eras.append({'state':state,'entries':entries})
    oldp=ROOT/'data'/f'{y}.js'
    txt=oldp.read_text(encoding='utf-8').split('=',1)[1].lstrip(); old=json.JSONDecoder().raw_decode(txt)[0]['title']
    ymeta[y]={**old,'year':f'{y:04d}','displayYear':y,'ganzhi':val(row,1) or old.get('ganzhi',''),'eras':eras}

# day page stream and group years
all_years={}
with DAY.open(encoding='utf-8-sig',newline='') as f:
    r=csv.reader(f)
    next(r); headers=next(r)
    for row in r:
        key=val(row,0)
        if not key or len(key)<4: continue
        try:y=int(key[:4])
        except:continue
        if not 200<=y<=500: continue
        code=val(row,4); d=val(row,5)
        day={
          'key':key,'ganzhi':val(row,1),'weekday':val(row,9),
          'chinese':{'date':key,'year':val(row,3),'month':code,'day':d,'calendar':val(row,16)},
          'western':{'date':val(row,2),'year':val(row,6),'month':val(row,7),'day':val(row,8),'calendar':val(row,17)},
          'astronomy':{'syzygy':val(row,10),'meanSolarTerm':val(row,11),'moonPhase':val(row,12),'trueSolarTerm':val(row,13),'solarEclipse':val(row,14),'lunarEclipse':val(row,15)},
          'orthodoxies':[]
        }
        for gi,start in enumerate((18,24,30),1):
            state=val(row,start)
            if state:
                day['orthodoxies'].append({'group':f'正朔{"一二三"[gi-1]}','state':state,'ruler':val(row,start+1),'eraYear':val(row,start+2),'month':val(row,start+3),'day':val(row,start+4),'calendar':val(row,start+5)})
        yd=all_years.setdefault(y,[]); yd.append(day)


# Reconstruct title-era order from latest day page, then attach year-page notes.
notes = {
(304,'漢','元和元年'):'癸酉，詔曰：……其改建初九年爲元和元年。（《後漢書·章帝紀》）',
(307,'漢','章和元年'):'秋七月壬戌，詔曰：……今改元和四年爲章和元年。（《後漢書·章帝紀》）',
(325,'漢','元興元年'):'夏四月庚午，大赦天下，改元元興。（《後漢書·和帝紀》；本表該年四月無庚午，以干支庚午定位）',
(334,'漢','元初元年'):'春正月甲子，改元元初。（《後漢書·安帝紀》）',
(340,'漢','永寧元年'):'夏四月丙寅，立皇子保爲皇太子，改元永寧，大赦天下。（《後漢書·安帝紀》）',
(341,'漢','建光元年'):'秋七月己卯，改元建光，大赦天下。（《後漢書·安帝紀》）',
(342,'漢','延光元年'):'三月丙午，改元延光。大赦天下。（《後漢書·安帝紀》）',
(352,'漢','陽嘉元年'):'春正月乙巳，大赦天下，改元陽嘉。（《後漢書·順帝紀》）',
(388,'漢','建寧元年'):'春正月庚子，解犢亭侯入南宮，即皇帝位。（《後漢書·靈帝紀》）',
(392,'漢','熹平元年'):'夏五月己巳，大赦天下，改元熹平。（《後漢書·靈帝紀》）',
(398,'漢','光和元年'):'春三月辛丑，赦天下，改元光和。（《後漢書·靈帝紀》）',
(404,'漢','中平元年'):'十二月己巳，大赦天下，改元中平。（《後漢書·靈帝紀》）',
(409,'漢','光熹元年'):'戊午，皇子辯即皇帝位，年十七。尊皇后曰皇太后，太后臨朝。大赦天下，改元爲光喜。（《後漢書·靈帝紀》）',
(409,'漢','昭寧元年'):'辛未，還宮。大赦天下，改光喜爲昭寧。（《後漢書·靈帝紀》）',
(409,'漢','永漢元年'):'九月甲戌，即皇帝位，年九歲。遷皇太后於永安宮。大赦天下。改昭寧爲永漢。（《後漢書·獻帝紀》）',
(410,'漢','初平元年'):'春正月……辛亥，大赦天下。（《後漢書·獻帝紀》）',
(414,'漢','興平元年'):'春正月辛酉，大赦天下，改元興平。（《後漢書·獻帝紀》）',
(416,'漢','建安元年'):'春正月癸酉，郊祀上帝於安邑，大赦天下，改元建安。（《後漢書·獻帝紀》）',
(440,'漢','延康元年'):'三月，改元延康。（《後漢書·獻帝紀》）',
(440,'魏','黄初元年'):'辛未，魏王登壇受禪……其以延康元年为黄初元年。（《三國志·魏書·文帝紀》裴松之注引《獻帝傳》）',
(440,'漢（蜀）','建安二十五年'):'辛未，魏王登壇受禪……其以延康元年为黄初元年。（《三國志·魏書·文帝紀》裴松之注引《獻帝傳》）',
(441,'漢（蜀）','章武元年'):'四月丙午，皇帝備……受皇帝璽綬……大赦，改年。（《三國志·蜀書·先主傳》）',
(442,'吴','黄武元年'):'冬十月……孫權復叛。（《三國志·魏書·文帝紀》）權遂改年，臨江拒守。（《三國志·吳書·吳主傳》）',
(443,'漢（蜀）','建興元年'):'五月，後主襲位於成都，大赦，改元。（《三國志·蜀書·後主傳》）',
(449,'吴','黄龍元年'):'夏四月，夏口、武昌並言黃龍、鳳皇見。丙申，南郊即皇帝位，大赦，改元。（《三國志·吳書·吳主傳》）',
(453,'魏','青龍元年'):'春二月丁酉，幸摩陂觀龍，於是改年。（《三國志·魏書·明帝紀》）',
(457,'魏','景初元年'):'三月，定曆改年爲孟夏四月。服色尚黃，犧牲用白，戎事乘黑首白馬，建大赤之旂，朝會建大白之旗。改太和曆曰景初曆。（《三國志·魏書·明帝紀》）',
(458,'吴','赤烏元年'):'秋八月，武昌言麒麟見。有司奏言麒麟者太平之應，宜改年號。詔曰可。（《三國志·吳書·吳主傳》）',
(469,'魏','嘉平元年'):'夏四月乙丑，改年。（《三國志·魏書·三少帝紀》）',
(471,'吴','太元元年'):'夏五月，立皇后潘氏，大赦，改年。（《三國志·吳書·吳主傳》）',
(472,'吴','神鳳元年'):'春二月，帝寢疾。（《三國志·吳書·吳主傳》）',
(472,'吴','建興元年'):'夏四月，權薨，時年七十一，諡曰大皇帝。太子亮即尊號，大赦，改元。（《三國志·吳書·三嗣主傳》）',
(474,'魏','正元元年'):'冬十月己丑，公至於玄武館。庚寅，羣臣奏請舍前殿，公以先帝舊處，避止西廂；羣臣又固請，乃御前殿，改元。（《三國志·魏書·三少帝紀》）',
(476,'魏','甘露元年'):'夏六月丙午，改元。（《三國志·魏書·三少帝紀》）',
(476,'吴','太平元年'):'冬十月己酉，大赦，改年。（《三國志·吳書·三嗣主傳》）',
(478,'漢（蜀）','景耀元年'):'春正月，姜維還成都。史官言景星見，於是大赦，改年。（《三國志·蜀書·後主傳》）',
(478,'吴','永安元年'):'冬十月戊寅，行至曲阿，有老公干休叩頭曰：「事久變生，天下喁喁，願陛下速行。」休善之。己卯，行至布塞亭，武衞將軍恩行丞相事，率百僚以乘輿法駕迎於永昌亭，築宮，以武帳爲便殿，設御座。休謙不肯御，百僚上書三四，休乃許之。於是正殿，羣臣以次奉引，休就乘輿，百官陪位。孫綝以兵千人迎於半野，拜於道側。休下車答拜。即日御正殿，大赦，改元。（《三國志·吳書·三嗣主傳》）',
(480,'魏','景元元年'):'六月甲寅，入于洛陽，見皇太后，是日即皇帝位於太極前殿，大赦，改元。（《三國志·魏書·三少帝紀》）',
(483,'漢（蜀）','炎興元年'):'夏，魏大興徒衆，命征西將軍鄧艾、鎮西將軍鍾會、雍州刺史諸葛緒數道並攻。（《三國志·蜀書·後主傳》）',
(484,'魏','咸熙元年'):'夏五月，壬子，進晉公爵爲晉王，增封十郡并前二十。（《三國志·魏書·三少帝紀》）',
(484,'吴','元興元年'):'秋七月，休薨。是月，皓即皇帝位，大赦，改元。（《三國志·吳書·三嗣主傳》）',
(485,'晉','泰始元年'):'十二月丙寅，設壇於南郊，百僚在位及匈奴南單于四夷會者數萬人，柴燎告類於上帝曰：……於是大赦，改元。（《晉書·武帝紀》）',
(485,'吴','甘露元年'):'夏四月，蔣陵言甘露降，於是大赦，改年。（《三國志·吳書·三嗣主傳》）',
(486,'吴','寶鼎元年'):'秋八月，所在言得大鼎，於是大赦，改年。（《三國志·吳書·三嗣主傳》）',
(489,'吴','建衡元年'):'冬十月，改年，大赦。（《三國志·吳書·三嗣主傳》）',
(496,'吴','天璽元年'):'，吳郡言臨平湖自漢末草穢壅塞，今更開通。長老相傳，此湖塞，天下亂，此湖開，天下平。又於湖邊得石函，中有小石，青白色，長四寸，廣二寸餘，刻上作皇帝字，於是改年，大赦。（《三國志·吳書·三嗣主傳》）',
}
state_order=['漢','魏','晉','漢（蜀）','吴']
for y,days in all_years.items():
    seq={s:[] for s in state_order}
    for d in days:
        for rec in d['orthodoxies']:
            st=rec['state']; era=rec['eraYear']
            if st in seq and era and era not in seq[st]: seq[st].append(era)
    groups=[]
    for st in state_order:
        if seq[st]: groups.append({'state':st,'entries':[{'era':era,'note':notes.get((y,st,era),'')} for era in seq[st]]})
    ymeta[y]['eras']=groups

# write data files
for y,days in all_years.items():
    months=[]; cur=None
    for day in days:
        code=day['chinese']['month']
        if cur is None or cur['id']!=code:
            cur={'id':code,'name':month_name(code),'isLeap':code.endswith('L'),'daysInMonth':0,'days':[]}; months.append(cur)
        cur['days'].append(day); cur['daysInMonth']+=1
    title=ymeta[y]
    # actual counts should agree with day page; retain year-page title but flag by data consistency in validation
    obj={'year':f'{y:04d}','displayYear':y,'title':title,'months':months}
    (ROOT/'data'/f'{y}.js').write_text('window.CalendarData = '+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')

# patch index data 200-500
p=ROOT/'data/index-data.js'; s=p.read_text(encoding='utf-8')
prefix='window.CalendarIndexData = '
obj=json.loads(s[len(prefix):].rstrip().rstrip(';'))
by={x['year']:x for x in obj['years']}
for y,m in ymeta.items():
    details=[]; eras=[]; states=[]
    for g in m['eras']:
        states.append(g['state'])
        for e in g['entries']:
            text=e['era'] + ((' '+e['note']) if e['note'] else '')
            details.append({'state':g['state'],'text':text,'era':e['era'],'note':e['note'],'fullText':text})
            eras.append(e['era'])
    solar=m['solarNewYear']
    by[y]={'year':y,'year4':f'{y:04d}','ganzhi':m['ganzhi'],'solarYear':solar.rsplit('-',2)[0] if solar else '',
           'solarNewYear':solar,'eras':eras,'eraDetails':details,'states':states,'href':f'years/{y}.html'}
obj['years']=sorted(by.values(),key=lambda x:x['year'])
p.write_text(prefix+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')

# save source snapshots
(ROOT/'source'/'川象曆_日頁_0200-0500_重讀.csv').write_bytes(DAY.read_bytes())
(ROOT/'source'/'川象曆_年頁_0200-0500_重讀.csv').write_bytes(YEAR.read_bytes())
print('rebuilt',len(all_years),'years',sum(len(v) for v in all_years.values()),'days')
for y in (304,325,334,352,377,388,392,409,440,500):
 print(y, ymeta[y]['eras'])
