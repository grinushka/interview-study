"""Applied-only taskbook, shared progress and independently hidden solutions."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
URL=(ROOT/'index.html').as_uri()
D=json.loads((ROOT/'data.js').read_text(encoding='utf-8').removeprefix('window.STUDY_DATA = ').rstrip(';\r\n'))
Q={q['id']:q for q in D['questions']}
pool=[q for q in Q.values() if q.get('taskFormat')]
assert set(q['lesson'] for q in pool)=={l['id'] for l in D['lessons']}
assert set(q['taskFormat'] for q in pool)=={'code','predict','debug','scenario','order','match'}
assert all(q['answerBlocks'] and q['followups'] for q in pool)
errors=[]
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000})
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((ROOT/'tasks.html').as_uri())
    page.wait_for_url('**index.html?view=tasks')
    assert page.locator('h1').inner_text()=='Задачник'
    assert page.locator('#task-questions .question').count()==10
    assert page.locator('.answer:visible').count()==0
    assert page.locator('.theory').count()==0
    card=page.locator('.question').first;card.locator('[data-action=reveal]').click()
    page.locator('[data-action=tasks-more]').click()
    assert page.locator('.question').count()==20
    assert page.locator('.answer:visible').count()==1 # append preserves an open solution
    for format in ['code','predict','debug','scenario','order','match']:
        page.locator('#tasks-format').select_option(format)
        ids=page.locator('.question').evaluate_all('(els)=>els.map(e=>e.dataset.q)')
        assert ids and all(Q[id]['taskFormat']==format for id in ids)
        assert page.locator('.answer:visible').count()==0
    page.locator('#tasks-format').select_option('code')
    assert page.locator('.question').count()==7
    page.locator('#tasks-lesson').select_option('url')
    assert page.locator('.question').count()==0
    assert not page.locator('[data-action=tasks-random]').is_enabled()
    page.locator('#tasks-format').select_option('')
    assert page.locator('.question').count()>0
    assert page.locator('[data-action=tasks-random]').is_enabled()
    page.locator('#tasks-lesson').select_option('')
    page.locator('[data-action=tasks-five]').click()
    ids=page.locator('.question').evaluate_all('(els)=>els.map(e=>e.dataset.q)')
    assert len(ids)==len(set(ids))==5 and len({Q[id]['lesson'] for id in ids})==5
    assert page.locator('.answer:visible').count()==0
    page.locator('[data-action=tasks-random]').click()
    old=page.locator('.question').get_attribute('data-q')
    page.locator('[data-action=tasks-random]').click()
    assert page.locator('.question').get_attribute('data-q')!=old
    page.locator('#tasks-query').fill('runLater')
    assert page.locator('.question').count()==1
    card=page.locator('.question');card.locator('textarea').fill('Мой сохранённый код <script> — текст')
    card.locator('[data-action=reveal]').click()
    card.locator('[data-rating=partial]').click()
    card.locator('.followup summary').click()
    assert card.locator('.followup details[open]').count()==1
    page.locator('#tasks-rating').select_option('partial')
    assert page.locator('.question').count()==1 and page.locator('.answer:visible').count()==0
    page.goto(URL+'?view=lesson&lesson=async&question=callbacks-practice-main')
    card=page.locator('[data-q=callbacks-practice-main]')
    assert card.locator('textarea').input_value().startswith('Мой сохранённый код')
    assert card.locator('[data-rating=partial]').get_attribute('aria-pressed')=='true'
    assert page.locator('script:not([src])').count()==0
    page.goto(URL+'?view=tasks&question=callbacks-practice-main')
    assert page.locator('.question').count()==1
    assert not page.locator('.answer').is_visible()
    assert page.locator('textarea').input_value().startswith('Мой сохранённый код')
    page.locator('[data-action=reveal]').focus();page.keyboard.press('Enter')
    assert page.locator('.answer').is_visible()
    page.screenshot(path=str(ROOT/'preview-taskbook-desktop.png'))
    page.reload();assert not page.locator('.answer').is_visible()
    page.set_viewport_size({'width':390,'height':844})
    page.goto(URL+'?view=tasks')
    for action in ['tasks-five','tasks-random','tasks-all']:
        page.locator('[data-action='+action+']').click()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert page.locator('.answer:visible').count()==0
    page.locator('#tasks-format').select_option('debug')
    page.locator('.question [data-action=reveal]').first.click()
    assert page.locator('.answer:visible').count()==1
    page.screenshot(path=str(ROOT/'preview-taskbook-mobile.png'))
    assert not errors,errors
    browser.close()
print('PASS: taskbook covers 15 lessons, all 6 formats, filters/empty state, diverse batch, random without immediate repeat, hidden solutions, keyboard, shared progress, drafts, mobile')
