import urllib.request,urllib.error,json,hashlib,time,re,pathlib
routes=[('GET','/',None),('GET','/login',None),('GET','/register',None)]
for i in range(60):
    try:
        urllib.request.urlopen('http://127.0.0.1:3000/',timeout=3)
        break
    except Exception:
        time.sleep(2);continue
else:
    raise SystemExit('BOOT FAILED')
def normalize(v):
    if isinstance(v,dict):return {k:normalize(x) for k,x in v.items() if k not in ('createdAt','updatedAt','requestId')}
    if isinstance(v,list):return [normalize(x) for x in v]
    return v
out=[]
for method,path,body in routes:
    req=urllib.request.Request('http://127.0.0.1:3000'+path,method=method,headers={'Accept':'text/html,application/json'})
    try:r=urllib.request.urlopen(req,timeout=15)
    except urllib.error.HTTPError as e:r=e
    raw=r.read().decode('utf8','replace');ct=r.headers.get('Content-Type','').split(';')[0]
    try:raw=json.dumps(normalize(json.loads(raw)),sort_keys=True,separators=(',',':'))
    except ValueError:
        raw=re.sub(r'(data-[a-z-]*nuxt[a-z-]*="?)[^"\s>]*',r'\1NORMALIZED',raw,flags=re.I)
        raw=re.sub(r'/_nuxt/[A-Za-z0-9._-]+','/_nuxt/NORMALIZED',raw)
        raw=re.sub(r'"buildId":"[^"]*"','"buildId":"NORMALIZED"',raw)
    out.append(dict(method=method,path=path,status=r.code,content_type=ct,sha256=hashlib.sha256(raw.encode()).hexdigest(),body=raw))
pathlib.Path('surface.actual.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
assert all(x['status']<500 for x in out),'server error in measured surface'
expected=pathlib.Path('surface.json')
if expected.exists():assert json.loads(expected.read_text())==out,'CHARACTERIZATION DRIFT'
print('BOOT + CHARACTERIZATION PASS')
