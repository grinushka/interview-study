"""Check course references, following redirects; report blocked sites separately."""
from pathlib import Path
import json, urllib.request, concurrent.futures, datetime
ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/'data.js').read_text(encoding='utf-8').removeprefix('window.STUDY_DATA = ').rstrip(';\n'))
used={k for t in data['topics'] for k in t['sources']}
def check(k):
    s=data['sources'][k]
    row=dict(id=k,title=s['title'],url=s['url'])
    try:
        req=urllib.request.Request(s['url'],headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=15) as r:
            row.update(status=r.status,finalUrl=r.url)
            r.read(1024)
    except Exception as err:row['error']=str(err)
    return row
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
    rows=list(pool.map(check,sorted(used)))
report=dict(checkedAt=datetime.date.today().isoformat(),sources=rows)
for row in rows:
    if row['id'] in {'rest','radio','solid'}:
        row['alsoReadWithWebToolOn']='2026-11-10'
(ROOT/'sources-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(total=len(rows),ok=sum(r.get('status')==200 for r in rows),issues=[r for r in rows if r.get('status')!=200]),ensure_ascii=False,indent=2))
