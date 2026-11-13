"""Execute the published solutions with a browser virtual clock and exercise the UI."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
from timer_practice import EXERCISES

ROOT=Path(__file__).resolve().parent
URL=(ROOT/'index.html').as_uri()
D=json.loads((ROOT/'data.js').read_text(encoding='utf-8').removeprefix('window.STUDY_DATA = ').rstrip(';\r\n'))
questions={q['id']:q for q in D['questions']}
assert len(EXERCISES)==7
assert [q['id'] for q in D['questions'] if q['kind']=='code']==[e['id'] for e in EXERCISES]
for item in EXERCISES:
    q=questions[item['id']]
    assert q['lesson']=='async' and q['topic']=='callbacks-practice'
    assert any(b.get('code')==item['solution'] for b in q['answerBlocks'])
    assert q['followups'][0]['answerBlocks']
assert not any(key.startswith('gen-') for t in D['topics'] for key in t['sources'])

with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    def setup(item,name,alternate=False):
        page=browser.new_page();page.goto('about:blank');page.clock.install(time=1_000_000);page.clock.pause_at(1_001_000)
        page.evaluate('''({code,name})=>{
          window.events=[];window.begin=Date.now();
          console.log=(...args)=>events.push([Date.now()-begin,...args]);
          window.fn=new Function(code+'; return '+name)();
        }''',dict(code=item['alternate'] if alternate else item['solution'],name=name))
        return page
    def events(page):return page.evaluate('events')
    # Synchronous work happens only after the delay and before its callback.
    page=setup(EXERCISES[0],'runLater')
    assert page.evaluate('typeof fn(()=>{console.log("work");return 42},value=>console.log("done",value))')=='number'
    page.clock.run_for(2999);assert events(page)==[]
    page.clock.run_for(1);assert events(page)==[[3000,'work'],[3000,'done',42]];page.close()
    # A callback return and future completion are different moments.
    page=setup(EXERCISES[1],'startLater')
    page.evaluate('fn(done=>{console.log("start");setTimeout(()=>done(42),1000)},value=>console.log("done",value))')
    page.clock.run_for(3000);assert events(page)==[[3000,'start']]
    page.clock.run_for(1000);assert events(page)[-1]==[4000,'done',42];page.close()
    # Both Promise versions wait and propagate rejection, without success callback.
    for alternate,name in [(False,'startLater'),(True,'startLaterChain')]:
        for reject in [False,True]:
            page=setup(EXERCISES[2],name,alternate)
            page.evaluate('''reject=>{
              fn(()=>new Promise((resolve,fail)=>setTimeout(()=>reject?fail(new Error('failed')):resolve(42),1000)),
                 value=>console.log('done',value)).catch(error=>console.log('error',error.message));
            }''',reject)
            page.clock.run_for(3999);assert events(page)==[]
            page.clock.run_for(1)
            assert events(page)==([[4000,'error','failed']] if reject else [[4000,'done',42]])
            page.close()
    # Sequential waits are measured from completion of the previous step.
    for alternate,name in [(False,'sequence'),(True,'sequenceAsync')]:
        page=setup(EXERCISES[3],name,alternate);page.evaluate('()=>{fn()}')
        page.clock.run_for(3000);assert events(page)==[[3000,'A']]
        page.clock.run_for(2000);assert events(page)==[[3000,'A'],[5000,'B'],[5000,'done']]
        page.close()
    page=setup(EXERCISES[4],'schedule')
    page.evaluate('()=>{const cancel=fn(()=>console.log("unexpected"));setTimeout(cancel,1000)}')
    page.clock.run_for(5000);assert events(page)==[];page.close()
    for alternate,name in [(False,'repeatInterval'),(True,'repeatTimeout')]:
        page=setup(EXERCISES[5],name,alternate)
        page.evaluate('()=>{fn(n=>console.log(n))}')
        page.clock.run_for(5000);assert events(page)==[[1000,1],[2000,2],[3000,3]];page.close()
    for reject in [False,True]:
        page=setup(EXERCISES[6],'repeatWork')
        page.evaluate('''reject=>{
          window.active=0;window.maxActive=0;
          fn(async()=>{
            active++;maxActive=Math.max(maxActive,active);console.log('start');
            await new Promise(resolve=>setTimeout(resolve,2000));
            active--;if(reject)throw new Error('failed');console.log('end');
          }).catch(error=>console.log('error',error.message));
        }''',reject)
        page.clock.run_for(12000)
        assert page.evaluate('maxActive')==1
        assert events(page)==([[1000,'start'],[3000,'error','failed']] if reject else
            [[1000,'start'],[3000,'end'],[4000,'start'],[6000,'end'],[7000,'start'],[9000,'end'],[9000,'done']])
        page.close()
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(URL+'?view=lesson&lesson=async&question=callbacks-practice-main')
    page.locator('#topic-filter').select_option('callbacks-practice')
    assert page.locator('.question').count()==7
    assert page.locator('textarea.code-answer').count()==7
    card=page.locator('[data-q=callbacks-practice-main]')
    assert not card.locator('.answer').is_visible()
    card.locator('textarea').fill('function runLater(work, onDone) { /* мой черновик */ }')
    card.locator('[data-action=reveal]').click()
    assert 'timer handle' in card.locator('.answer').inner_text()
    assert page.locator('.answer:visible').count()==1
    card.locator('.followup summary').click()
    assert card.locator('.followup details[open]').count()==1
    page.reload()
    assert 'мой черновик' in page.locator('[data-answer=callbacks-practice-main]').input_value()
    assert not page.locator('[data-q=callbacks-practice-main] .answer').is_visible()
    page.locator('[data-q=callbacks-practice-main] [data-action=reveal]').click()
    page.screenshot(path=str(ROOT/'preview-timers-desktop.png'))
    page.set_viewport_size({'width':390,'height':844})
    for item in EXERCISES:
        page.goto(URL+'?view=lesson&lesson=async&question='+item['id'])
        card=page.locator('[data-q="'+item['id']+'"]')
        card.locator('[data-action=reveal]').click()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),item['id']
    page.screenshot(path=str(ROOT/'preview-timers-mobile.png'))
    page.goto(URL);page.locator('#search').fill('repeatWork')
    assert page.locator('[data-search-type=question]').count()>0
    assert page.locator('[data-search-type=question] p').count()==0
    assert not errors,errors
    browser.close()
print('PASS: seven timer exercises, all solutions and alternatives, virtual timing, cancellation, rejection, no overlap, hidden answers, draft persistence, search, mobile')
