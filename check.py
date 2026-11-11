"""Meaningful offline browser checks. Run: python interview-study/check.py"""
from pathlib import Path
import json, re, importlib.util
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
URL=(ROOT/'index.html').as_uri()
data=json.loads((ROOT/'data.js').read_text(encoding='utf-8').removeprefix('window.STUDY_DATA = ').rstrip(';\n'))
Q={q['id']:q for q in data['questions']}
T={t['id']:t for t in data['topics']}
assert len(data['lessons'])==15
assert len(Q)==len(data['questions'])
assert len(T)==len(data['topics'])
assert all(q['lesson'] in {l['id'] for l in data['lessons']} and q['topic'] in T for q in Q.values())
assert all(r.get('question') in Q for r in data['coverage'] if r['status']=='included')
assert all(any(q['topic']==t['id'] for q in Q.values()) for t in T.values())
assert all(t.get('explanation',{}).get('context') and t['explanation'].get('example') and t['explanation'].get('takeaway') and len(t['explanation'].get('steps',[]))>=3 for t in T.values())
assert len([r for r in data['coverage'] if r['origin'].startswith('Чат')])==36
assert len([q for q in Q if q.startswith('solid-item-')])==5
assert len([q for q in Q if q.startswith('promise-combinators-item-')])==4
assert len([q for q in Q if q.startswith('utilities-item-')])==12
assert all(not re.search(r'^(Есть ли|Был ли|Сработает ли)',q['prompt']) for q in Q.values())
assert not any(re.search(r'Elasticsearch|Kafka|Redis|нормализаци|реляционн|Database joins',q['prompt'],re.I) for q in Q.values())
for f in ROOT.glob('*.html'):
    text=f.read_text(encoding='utf-8')
    for asset in re.findall(r'(?:src|href)="([^"#?]+)"',text):
        if not asset.startswith(('http:','https:')):assert (ROOT/asset).exists(),(f.name,asset)

errors=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,channel='chrome')
    context=browser.new_context(viewport={'width':1440,'height':1050},accept_downloads=True)
    page=context.new_page()
    page.on('pageerror',lambda err:errors.append(str(err)))
    page.goto(URL)
    page.wait_for_selector('.lesson-card')
    assert page.locator('.lesson-card').count()==15
    page.screenshot(path=str(ROOT/'preview-desktop.png'),full_page=False)
    page.locator('#search').fill('satisfies')
    assert page.locator('.search-result').count()>0
    page.locator('[data-search-type="question"]').first.click()
    page.wait_for_selector('.question')
    card=page.locator('.question').filter(has=page.locator('[data-answer="assertions-main"]'))
    if card.count()!=1:card=page.locator('.question').first
    qid=card.get_attribute('data-q')
    card.locator('textarea').fill('Мой ответ: satisfies проверяет совместимость без runtime-валидации.')
    assert not card.locator('.answer').is_visible()
    card.locator('[data-action=reveal]').click()
    card.locator('[data-rating=partial]').click()
    assert card.locator('[data-rating-label]').inner_text()=='Частично'
    page.reload();page.wait_for_selector('.question')
    assert page.locator(f'[data-answer="{qid}"]').input_value().startswith('Мой ответ:')
    assert page.locator(f'[data-q="{qid}"] [data-rating-label]').inner_text()=='Частично'
    # Canonical file route gives one localStorage origin/path for all lesson entry pages.
    page.goto((ROOT/'lesson-01.html').as_uri())
    page.wait_for_url('**index.html?view=lesson&lesson=url')
    page.wait_for_selector('[data-action=read]')
    page.locator('[data-action=read]').first.click()
    page.goto(URL+'?view=lesson&lesson=communication')
    page.locator('[data-action=read]').first.click()
    page.locator('[data-action=mix]').click()
    assert page.locator('#mixed-questions .question').count()==3, {'errors':errors,'html':page.locator('#mixed-questions').inner_html()[:300]}
    assert all(Q[x]['lesson']=='url' for x in page.locator('#mixed-questions .question').evaluate_all('(els)=>els.map(e=>e.dataset.q)'))
    # Order exercise: use accessible controls to reach the correct sequence.
    page.goto(URL+'?view=lesson&lesson=async&question=event-loop-main')
    card=page.locator('[data-q="event-loop-main"]')
    for target in range(5):
        while True:
            values=card.locator('[data-order-value]').evaluate_all('(els)=>els.map(e=>Number(e.dataset.orderValue))')
            position=values.index(target)
            if position==target:break
            card.locator(f'[data-order-value="{target}"] [data-direction="-1"]').click()
    card.locator('[data-action=check-order]').click()
    assert 'Порядок верный' in card.locator('.feedback').inner_text()
    page.reload();page.wait_for_selector('[data-q="event-loop-main"]')
    assert page.locator('[data-q="event-loop-main"] [data-order-value]').evaluate_all('(els)=>els.map(e=>Number(e.dataset.orderValue))')==[0,1,2,3,4]
    # Matching: no answer is selected initially; errors and correct pairing are distinguished.
    page.goto(URL+'?view=lesson&lesson=http&question=statuses-main')
    card=page.locator('[data-q="statuses-main"]')
    card.locator('[data-action=check-match]').click()
    assert 'Сначала выбери' in card.locator('.feedback').inner_text()
    for i in range(5):card.locator(f'[data-pair="{i}"]').select_option(str(i))
    card.locator('[data-action=check-match]').click()
    assert 'Совпало 5 из 5' in card.locator('.feedback').inner_text()
    # Review filters and ten diverse interview questions, including resumption.
    page.goto(URL+'?view=review')
    assert page.locator('#review-questions .question').count()==1
    page.locator('#review-rating').select_option('all')
    assert page.locator('#review-questions .question').count()==15
    page.locator('#review-lesson').select_option('typescript')
    assert all(Q[x]['lesson']=='typescript' for x in page.locator('#review-questions .question').evaluate_all('(els)=>els.map(e=>e.dataset.q)'))
    page.goto(URL+'?view=interview')
    page.locator('[data-action=new-interview]').click()
    run=page.evaluate('JSON.parse(localStorage.getItem("interview-study-v1")).interview')
    assert len(run['ids'])==10 and len({Q[x]['lesson'] for x in run['ids']})==10
    page.locator('[data-action=interview-skip]').click()
    page.reload()
    assert 'Вопрос 2 / 10' in page.locator('#interview-run').inner_text()
    for _ in range(9):page.locator('[data-action=interview-next]').click()
    assert 'Раунд завершён' in page.locator('#interview-run').inner_text()
    page.goto(URL+'?view=progress')
    with page.expect_download() as info:page.locator('[data-action=export]').click()
    export=ROOT/'test-progress.json'
    info.value.save_as(str(export))
    saved=json.loads(export.read_text(encoding='utf-8'))
    assert saved['ratings'][qid]=='partial' and saved['answers'][qid].startswith('Мой ответ:')
    second=browser.new_context(viewport={'width':390,'height':844})
    mobile=second.new_page();mobile.on('pageerror',lambda err:errors.append(str(err)))
    mobile.goto(URL+'?view=progress')
    mobile.locator('#import-file').set_input_files(str(export))
    assert 'импортирован' in mobile.locator('#toast').inner_text()
    mobile.reload()
    assert mobile.evaluate('JSON.parse(localStorage.getItem("interview-study-v1")).ratings')[qid]=='partial'
    mobile.goto(URL)
    mobile.screenshot(path=str(ROOT/'preview-mobile.png'),full_page=False)
    assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth'), 'home overflow'
    # Inspect every route on desktop, and representative long content on mobile.
    for l in data['lessons']:
        page.goto(URL+'?view=lesson&lesson='+l['id'])
        assert page.locator('.theory').count()==len(l['topics'])
        assert page.locator('.worked-example').count()==len(l['topics'])
        assert page.locator('.interview-takeaway').count()==len(l['topics'])
        assert page.locator('h1').inner_text()==l['title']
        page.locator('[data-mode=practice]').click()
        assert page.locator('.question').count()==len([q for q in Q.values() if q['lesson']==l['id']])
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),l['id']
    for suffix in ['?view=lesson&lesson=typescript','?view=lesson&lesson=http&question=statuses-main','?view=coverage','?view=review']:
        mobile.goto(URL+suffix)
        assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth'),suffix
    mobile.goto(URL+'?view=lesson&lesson=async&question=event-loop-main')
    mobile.locator('[data-q="event-loop-main"]').scroll_into_view_if_needed()
    mobile.screenshot(path=str(ROOT/'preview-exercise.png'),full_page=False)
    # Long-form theory is readable at mobile width; reference details can be opened.
    mobile.goto(URL+'?view=lesson&lesson=typescript')
    mobile.locator('#topic-assertions').scroll_into_view_if_needed()
    mobile.locator('#topic-assertions .topic-reference summary').click()
    assert mobile.locator('#topic-assertions .topic-reference dl').is_visible()
    assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth')
    mobile.screenshot(path=str(ROOT/'preview-theory-mobile.png'),full_page=False)
    page.goto(URL+'?view=lesson&lesson=communication')
    page.locator('#topic-broadcast .worked-example').scroll_into_view_if_needed()
    page.screenshot(path=str(ROOT/'preview-theory-desktop.png'),full_page=False)
    plain=browser.new_context(java_script_enabled=False)
    plainpage=plain.new_page();plainpage.goto((ROOT/'lesson-11.html').as_uri())
    assert plainpage.locator('.worked-example').count()==len(next(l for l in data['lessons'] if l['id']=='typescript')['topics'])
    assert 'satisfies' in plainpage.locator('#assertions').inner_text()
    # Reject a malformed import without deleting existing progress.
    bad=ROOT/'test-invalid.json';bad.write_text('{"version":99}',encoding='utf-8')
    mobile.goto(URL+'?view=progress');mobile.locator('#import-file').set_input_files(str(bad))
    assert 'Импорт не выполнен' in mobile.locator('#toast').inner_text()
    assert mobile.evaluate('JSON.parse(localStorage.getItem("interview-study-v1")).ratings')[qid]=='partial'
    # Storage errors must leave the trainer usable and support an export.
    blocked=browser.new_context()
    blocked.add_init_script('Object.defineProperty(window,"localStorage",{get(){throw new Error("blocked")}})')
    bp=blocked.new_page();bp.goto(URL)
    assert bp.locator('#storage-warning').is_visible()
    assert bp.locator('.lesson-card').count()==15
    assert not errors,errors
    export.unlink();bad.unlink()
    browser.close()

print(json.dumps({'result':'PASS','lessons':15,'topics':len(T),'questions':len(Q),'coverage':len(data['coverage']),'checks':['file routes','all lessons','search','self assessment','answer persistence','mixed review','order','matching','interview completion/resume','export/import','invalid import','blocked storage','mobile overflow'],'pageErrors':errors},ensure_ascii=False,indent=2))
