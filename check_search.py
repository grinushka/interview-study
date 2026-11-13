"""Offline search acceptance tests: real interactions, full text, navigation and accessibility."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
URL=(ROOT/'index.html').as_uri()
errors=[]
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    context=browser.new_context(viewport={'width':1440,'height':1000})
    page=context.new_page();page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto(URL)
    page.locator('#search').fill('satisfies')
    assert page.locator('.search-topic').count()>0
    assert page.locator('[data-search-type=theory]').count()>0
    assert page.locator('[data-search-type=question]').count()>0
    assert page.locator('[data-search-type=example]').count()>0
    assert page.locator('.search-topic mark').count()>0
    # Repeated questions are grouped, not shown as a flat list of duplicates.
    assert page.locator('.search-topic').count()<page.locator('.search-result').count()
    page.locator('#search').fill('24 часа')
    assert 'Дедупликация' in page.locator('#search-results').inner_text()
    page.locator('#search-results [data-search-type=example]').first.click()
    page.wait_for_selector('.theory')
    assert page.url.endswith('#example-dedup')
    assert page.locator('#example-dedup').is_visible()
    # Search is available inside lessons; long-form body text is indexed too.
    page.locator('[data-action=open-search]').click()
    assert page.locator('#global-search-dialog').is_visible()
    assert page.locator('#global-search-input').evaluate('(el)=>el===document.activeElement')
    page.locator('#global-search-input').fill('критическую секцию')
    assert 'Дедупликация' in page.locator('#global-search-results').inner_text()
    page.locator('#global-search-results [data-search-type=theory]').first.click()
    page.wait_for_selector('.theory')
    assert page.url.endswith('#topic-dedup')
    page.keyboard.press('Control+k')
    page.locator('#global-search-input').fill('garbage collection')
    assert 'Сборка мусора' in page.locator('#global-search-results').inner_text()
    page.locator('#global-search-input').fill('closures')
    assert 'Замыкания' in page.locator('#global-search-results').inner_text()
    page.locator('#global-search-input').fill('allsettle')
    assert 'Promise' in page.locator('#global-search-results').inner_text()
    page.locator('#global-search-input').fill('объект сохранил ссылку')
    assert 'Массив зависимостей' in page.locator('#global-search-results').inner_text()
    page.locator('#global-search-input').fill('Promise')
    page.locator('#global-search-results [data-type=question]').click()
    assert page.locator('#global-search-results [data-search-type=theory]').count()==0
    assert page.locator('#global-search-results [data-search-type=example]').count()==0
    assert page.locator('#global-search-results [data-search-type=question]').count()>0
    # Questions never include answer excerpts in search cards.
    assert page.locator('#global-search-results .search-result p').count()==0
    page.locator('#global-search-results [data-type=example]').click()
    assert page.locator('#global-search-results [data-search-type=question]').count()==0
    assert page.locator('#global-search-results [data-search-type=example]').count()>0
    page.locator('#global-search-input').fill('zzzzzzzzzzzz')
    assert 'Совпадений нет' in page.locator('#global-search-results').inner_text()
    page.locator('#global-search-input').fill('<img src=x onerror=alert(1)>')
    assert page.locator('#global-search-results img').count()==0
    page.keyboard.press('Escape');assert not page.locator('#global-search-dialog').is_visible()
    page.locator('[data-action=open-search]').click();page.keyboard.press('Escape')
    assert page.locator('[data-action=open-search]').evaluate('(el)=>el===document.activeElement')
    # Opening/cancelling search must leave an in-progress exercise answer untouched.
    page.goto(URL+'?view=lesson&lesson=architecture&question=solid-main')
    page.locator('[data-answer=solid-main]').fill('Мой незавершённый ответ о SOLID')
    page.keyboard.press('Control+k');page.locator('#global-search-input').fill('satisfies')
    page.keyboard.press('Escape')
    assert page.locator('[data-answer=solid-main]').input_value()=='Мой незавершённый ответ о SOLID'
    page.locator('[data-action=open-search]').click()
    page.locator('#global-search-input').fill('satisfies')
    page.locator('#global-search-results [data-type=all]').click()
    page.screenshot(path=str(ROOT/'preview-search-desktop.png'))
    page.keyboard.press('Escape')
    # Native dialog traps focus, closes with Escape and has a full-screen phone layout.
    page.set_viewport_size({'width':390,'height':844})
    page.locator('[data-action=open-search]').click()
    assert page.locator('#global-search-dialog').evaluate('(el)=>Math.abs(el.getBoundingClientRect().width-innerWidth)<2')
    page.locator('#global-search-input').fill('Promise')
    page.screenshot(path=str(ROOT/'preview-search-mobile.png'))
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    assert page.locator('#global-search-dialog').evaluate('(el)=>el.scrollWidth<=el.clientWidth')
    page.keyboard.press('Tab')
    assert page.evaluate('document.activeElement.closest("#global-search-dialog")!==null')
    page.locator('#global-search-results [data-type=question]').click()
    page.locator('#global-search-results [data-search-type=question]').first.click()
    page.wait_for_selector('.question')
    assert 'question=' in page.url
    assert page.locator('.answer:visible').count()==0
    for route in ['?view=review','?view=interview','?view=progress','?view=coverage']:
        page.goto(URL+route);page.locator('[data-action=open-search]').click()
        assert page.locator('#global-search-input').is_visible()
        page.keyboard.press('Escape')
    assert not errors,errors
    browser.close()
print('PASS: grouped full-text search, theory/questions/examples, RU/EN aliases, prefix spelling, highlighting, precise anchors, no answer leakage, safe input, keyboard/focus, preserved draft, all routes, phone layout')
