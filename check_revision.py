"""Content, old-progress compatibility, hidden clarifications and coordination examples."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
from revision_content import LOCK_CODE, IDB_CODE

ROOT=Path(__file__).resolve().parent
URL=(ROOT/'index.html').as_uri()
D=json.loads((ROOT/'data.js').read_text(encoding='utf-8').removeprefix('window.STUDY_DATA = ').rstrip(';\n'))
Q={q['id']:q for q in D['questions']}
T={t['id']:t for t in D['topics']}
old=json.loads((ROOT/'legacy-course.json').read_text(encoding='utf-8'))
assert len(old['questions'])==294 and len(old['topics'])==77
assert set(old['topics'])<=T.keys()
assert old['lessons']==[l['id'] for l in D['lessons']]
for q in old['questions']:
    assert all(Q[q['id']][key]==value for key,value in q.items()),q['id']
for q in Q.values():
    assert q['answerBlocks'] and 'check' not in q
    assert q['followups'],q['id']
    for f in q['followups']:
        assert isinstance(f,dict) and f['question'] and f['answerBlocks'],q['id']
        assert all(b.get('text') or b.get('items') or b.get('code') for b in f['answerBlocks'])
for t in T.values():
    assert all(s in D['sources'] for s in t['sources'])
    assert any(q['topic']==t['id'] for q in Q.values())
    if t['drill']:
        assert all(f"{t['id']}-item-{n+1}" in Q for n in range(len(t['items'])))
assert len([r for r in D['coverage'] if r['origin']=='Notion · Gen notes'])==15
assert all(r['question'] in Q for r in D['coverage'] if r['status']=='included')
assert 'Ключевые пункты для самопроверки' not in (ROOT/'app.js').read_text(encoding='utf-8')
legacy={"version":1,"answers":{"dedup-main":"Мой прежний ответ","chat-2-11":"Ссылка прежняя"},
        "ratings":{"dedup-main":"partial","chat-2-11":"know"},"read":{"dedup":True,"cloning":True},
        "work":{"event-loop-main":{"order":[4,3,2,1,0]},"statuses-main":{"matches":[0,1,2,3,4]}},
        "updated":{},"interview":{"ids":[q['id'] for q in old['questions'][:10]],"index":3}}
errors=[]
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
    page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(URL)
    page.evaluate('(s)=>localStorage.setItem("interview-study-v1",JSON.stringify(s))',legacy)
    page.goto(URL+'?view=lesson&lesson=communication&question=dedup-main')
    card=page.locator('[data-q="dedup-main"]')
    assert card.locator('textarea').input_value()==legacy['answers']['dedup-main']
    assert not card.locator('.answer').is_visible()
    card.locator('[data-action=reveal]').click()
    assert card.locator('.answer-block pre').count()>=2
    assert card.locator('.followup').count()==3
    assert card.locator('.followup details[open]').count()==0
    first=card.locator('.followup').first
    first.locator('summary').focus();page.keyboard.press('Enter')
    assert first.locator('details').get_attribute('open') is not None
    assert card.locator('.followup details[open]').count()==1
    assert 'getItem' in first.inner_text()
    assert card.locator('[data-action=rate]').count()==3
    card.scroll_into_view_if_needed()
    page.screenshot(path=str(ROOT/'preview-revision-desktop.png'))
    page.reload()
    assert not page.locator('[data-q="dedup-main"] .answer').is_visible()
    # Import an actual old-shape fixture, then export and reload.
    fixture=ROOT/'test-legacy-progress.json'
    fixture.write_text(json.dumps(legacy,ensure_ascii=False),encoding='utf-8')
    page.goto(URL+'?view=progress')
    page.locator('#import-file').set_input_files(str(fixture))
    page.reload()
    saved=page.evaluate('JSON.parse(localStorage.getItem("interview-study-v1"))')
    for key in ('answers','ratings','read','work','interview'):assert saved[key]==legacy[key],key
    with page.expect_download() as download:page.locator('[data-action=export]').click()
    exported=ROOT/'test-revision-export.json';download.value.save_as(str(exported))
    for key in ('answers','ratings','read','work','interview'):
        assert json.loads(exported.read_text(encoding='utf-8'))[key]==legacy[key]
    page.goto(URL+'?view=interview')
    assert 'Вопрос 4 / 10' in page.locator('#interview-run').inner_text()
    # Followups are shared by all presentation modes.
    page.locator('[data-action=reveal]').click()
    assert page.locator('.followup summary').count()>0
    page.goto(URL+'?view=review')
    page.locator('[data-action=reveal]').first.click()
    assert page.locator('.answer:visible .followup summary').count()>0
    # Search indexes hidden answers without leaking their text into snippets.
    page.goto(URL);page.locator('#search').fill('ожидаемый дубль')
    assert page.locator('[data-search-type=question]').count()>0
    assert page.locator('[data-search-type=question] p').count()==0
    assert '[object Object]' not in page.locator('#search-results').inner_text()
    for query in ('Web Locks','Notifications','sandbox','storage event','worker alternatives'):
        page.locator('#search').fill(query)
        if query!='worker alternatives':assert page.locator('.search-result').count()>0,query
    # Code is inert: no worker registration or permission prompt on studying.
    assert 'serviceWorker.register' not in (ROOT/'app.js').read_text(encoding='utf-8')
    page.set_viewport_size({'width':390,'height':844})
    page.goto(URL+'?view=lesson&lesson=communication&question=dedup-main')
    card=page.locator('[data-q="dedup-main"]');card.locator('[data-action=reveal]').click()
    first=card.locator('.followup').first;first.locator('summary').click()
    first.scroll_into_view_if_needed()
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.screenshot(path=str(ROOT/'preview-revision-mobile.png'))
    # Run the educational coordination fragments against real browser APIs.
    worker=browser.new_context().new_page();worker.goto(URL)
    lock_result=worker.evaluate('''async (code)=>{
      window.shown=[]; window.showToast=text=>shown.push(text);
      const run=new Function(code+'; return showOnce;')();
      await Promise.all(Array.from({length:20},()=>run({id:'test-lock',text:'one'})));
      return shown.length;
    }''',LOCK_CODE)
    assert lock_result==1
    result=worker.evaluate('''async (code)=>{
      const db=await new Promise((resolve,reject)=>{
        const r=indexedDB.open('revision-claims',1);
        r.onupgradeneeded=()=>r.result.createObjectStore('claims',{keyPath:'id'});
        r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);
      });
      window.shown=[];window.showToast=text=>shown.push(text);
      const run=new Function('db','event','return (async()=>{'+code+'})()');
      await Promise.all(Array.from({length:20},()=>run(db,{id:'test-idb',text:'one'})));
      const count=shown.length;db.close();return count;
    }''',IDB_CODE)
    assert result==1
    fixture.unlink();exported.unlink()
    assert not errors,errors
    browser.close()
print(json.dumps(dict(result='PASS',legacyQuestions=294,questions=len(Q),topics=len(T),notes=15,
                     checks=['old IDs/prompts','old progress import/export/resume','hidden followups','keyboard','review/interview','search','mobile','real lock and IDB claims']),ensure_ascii=False))
