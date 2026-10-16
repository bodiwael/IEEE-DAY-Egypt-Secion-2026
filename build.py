#!/usr/bin/env python3
"""Reads Master_Sheet.xlsx -> builds site/ (encrypted attendee data + staff logins), backend/Code.gs, staff_codes.csv
   Usage: pip install openpyxl cryptography   then   python3 build.py [Master_Sheet.xlsx]"""
import openpyxl,json,os,re,base64,hashlib,secrets,csv,sys,shutil
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
H=os.path.dirname(os.path.abspath(__file__));XL=sys.argv[1] if len(sys.argv)>1 else H+'/Master_Sheet.xlsx'
SALT='ieee26fy';CATS={'VIP':'VIP','Former Officers':'FO','YP':'YP','SAC':'SAC','Ambassador':'AMB','Attendees':'AT','Volunteers':'VOL'}
ROLES={'bus','gate','kit','lunch','a1','a2','a3','back','admin'}
A={'id':['id','ticket id'],'name':['name'],'email':['email'],'point':['point'],'branch':['student branch','branch'],'nid':['national id','nationalid','nid'],'tshirt':['t-shirt size','tshirt','t-shirt','size'],'phone':['phone','mobile']}
b=lambda x:base64.b64encode(x).decode();nz=lambda s:re.sub(r'[^A-Z0-9]','',str(s).upper())
def s(v):
    if v is None:return ''
    if isinstance(v,float) and v.is_integer():v=int(v)
    return str(v).strip()
wb=openpyxl.load_workbook(XL,data_only=True);P=[];warn=[];seen={}
for ws in wb:
    if ws.title in('Staff','READ ME'):continue
    rows=list(ws.iter_rows(values_only=True));hd=[s(x).lower() for x in rows[0]]
    ix={k:next((hd.index(a) for a in v if a in hd),None) for k,v in A.items()}
    miss=[k for k in('id','name','email') if ix[k] is None]
    if miss:warn.append(f'sheet {ws.title}: missing column {miss}');continue
    g=lambda r,k:s(r[ix[k]]) if ix[k] is not None and ix[k]<len(r) else ''
    cat=CATS.get(ws.title,ws.title[:3].upper())
    for r in rows[1:]:
        if not g(r,'id') and not g(r,'name'):continue
        i=g(r,'id').zfill(3);u=cat+i;pt=g(r,'point');pt=pt if pt in('Ramsis','October') else 'No'
        nid=g(r,'nid')
        if re.search(r'E\+',nid):warn.append(f'{ws.title} {i}: National ID damaged by Excel (scientific notation) - format column as Text')
        em=g(r,'email').lower()
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$',em):warn.append(f'{ws.title} {i}: invalid email "{em}"')
        if u in seen:warn.append(f'DUPLICATE ticket {u}')
        seen[u]=1;P.append([u,i,' '.join(g(r,'name').split()),em,pt,cat,g(r,'branch'),nid,g(r,'tshirt').upper(),g(r,'phone')])
sheet=wb['Staff'];T={};srows=list(sheet.iter_rows(values_only=True));sh=[s(x).lower() for x in srows[0]]
col=lambda n:sh.index(n)
for r in srows[1:]:
    if not s(r[0]):continue
    sid=nz(r[0]);role=s(r[col('role')]).lower()
    if role not in ROLES:warn.append(f'Staff {sid}: bad role "{role}"');continue
    T[sid]=dict(n=s(r[col('name')]),r=role,bus=s(r[col('bus')]),pt=s(r[col('point')]),e=s(r[col('email')]))
codes={}
if os.path.exists(H+'/staff_codes.csv'):codes={r['staff_id']:r['code'] for r in csv.DictReader(open(H+'/staff_codes.csv'))}
al='ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
for sid in T:codes.setdefault(sid,''.join(secrets.choice(al) for _ in range(8)))
K=os.urandom(32);iv=os.urandom(12)
DATA=[b(iv),b(AESGCM(K).encrypt(iv,json.dumps({'P':P,'T':T},separators=(',',':'),ensure_ascii=False).encode(),None))]
Wr={}
for sid in T:
    sa,iv2=os.urandom(16),os.urandom(12);k=PBKDF2HMAC(hashes.SHA256(),32,sa,200000).derive(codes[sid].encode())
    Wr[sid]=[b(sa),b(iv2),b(AESGCM(k).encrypt(iv2,K,None))]
os.makedirs(H+'/site',exist_ok=True)
t=open(H+'/template.html').read().replace('__DATA__',json.dumps(DATA)).replace('__W__',json.dumps(Wr)).replace('__SALT__',SALT).replace('__BANNER__','data:image/jpeg;base64,'+b(open(H+'/assets/banner.jpg','rb').read()))
open(H+'/site/index.html','w').write(t)
for f in('sw.js','manifest.json','icon-192.png','icon-512.png'):shutil.copy(H+'/assets/'+f,H+'/site/'+f)
open(H+'/site/.nojekyll','w').write('')
hs={sid:hashlib.sha256((SALT+c).encode()).hexdigest() for sid,c in codes.items() if sid in T}
open(H+'/backend/Code.gs','w').write(open(H+'/backend/Code.gs.tpl').read().replace('__STAFF__',json.dumps(hs)))
w=csv.writer(open(H+'/staff_codes.csv','w',newline=''));w.writerow(['staff_id','name','role','bus','code'])
for sid,x in T.items():w.writerow([sid,x['n'],x['r'],x['bus'],codes[sid]])
print(f'OK: {len(P)} people, {len(T)} staff. NID filled:{sum(1 for p in P if p[7])} T-shirt filled:{sum(1 for p in P if p[8])} phone:{sum(1 for p in P if p[9])}')
for x in warn[:30]:print('WARNING:',x)
print(f'({len(warn)} warnings)')
