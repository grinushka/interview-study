/* Offline, dependency-free study UI. All routes use one file URL for consistent file:// storage. */
(() => {
  'use strict';
  const D = window.STUDY_DATA;
  const initial = document.body.dataset;
  if (!location.pathname.endsWith('/index.html') && !location.pathname.endsWith('/')) {
    const url = new URL('index.html', location.href);
    url.searchParams.set('view', initial.view || 'home');
    if (initial.lesson) url.searchParams.set('lesson', initial.lesson);
    location.replace(url.href);
    return;
  }
  const KEY = 'interview-study-v1';
  const Q = new Map(D.questions.map(q => [q.id, q]));
  const T = new Map(D.topics.map(t => [t.id, t]));
  const L = new Map(D.lessons.map(l => [l.id, l]));
  const labels = {recall:'Вспомнить без подсказок',scenario:'Выбрать решение',compare:'Сравнить похожее',order:'Восстановить порядок',match:'Сопоставить пары',explain:'Объяснить просто',interview:'Мини-собеседование',experience:'История из опыта'};
  const ratings = {none:'Без оценки',forgot:'Не помню',partial:'Частично',know:'Могу объяснить'};
  const emptyState = () => ({version:1,answers:{},ratings:{},read:{},work:{},updated:{},interview:null});
  let state = emptyState(), storageOK = true, lessonMode = 'theory', reviewIds = [], reviewLimit = 15;
  let mixedIds = [], currentLesson = null, toastTimer;
  const params = new URLSearchParams(location.search);
  const view = ['home','lesson','review','interview','coverage','progress'].includes(params.get('view')) ? params.get('view') : 'home';
  const e = s => String(s ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const link = (v='home', id='', q='') => `index.html?view=${encodeURIComponent(v)}${id?'&lesson='+encodeURIComponent(id):''}${q?'&question='+encodeURIComponent(q):''}`;
  const searchTypes = {all:'Все',theory:'Теория',question:'Вопросы',example:'Примеры'};
  const searchState = {inline:{query:'',type:'all',limit:12},global:{query:'',type:'all',limit:12}};
  const synonymGroups = [
    ['promise','промис'], ['closure','closures','замыкан'], ['context','контекст'],
    ['dependencies','dependency','зависим'], ['garbage','gc','сборк','мусор'],
    ['reference','identity','ссыл'], ['сохран'], ['worker','воркер'], ['render','рендер'],
    ['hydration','гидратац'], ['specificity','специфичност']
  ];
  const searchText = value => normalize(value).replace(/[^\p{L}\p{N}]+/gu,' ').trim();
  function searchTerms(query){
    const stop=new Set(['как','что','это','чем','для','при','или','на','с','и','по','в','the','a','of']);
    return [...new Set(searchText(query).replace(/garbage collection/g,'gc').split(/\s+/).filter(w=>w&&!stop.has(w)))].map(word=>{
      const stem=/[а-я]/.test(word)&&word.length>5?word.replace(/(?:иями|ами|ого|ему|ями|ыми|ими|ение|ения|ией|ия|ие|ые|ий|ый|ой|ов|ам|ах|ях|ом|ем|ку|ки|ка|ы|а|я|у|ю|е|и)$/u,''):word;
      const group=synonymGroups.find(g=>g.some(s=>s===word||s===stem||(/[а-я]/.test(s)&&stem.startsWith(s))));
      return group||[stem];
    });
  }
  const searchDocuments=D.topics.flatMap(t=>{
    const z=t.explanation;
    const theory=[z.context,...z.steps,z.takeaway,t.summary,t.note,...t.items.map(i=>i.name+' '+i.detail)].join(' ');
    const example=[z.example,z.code,t.code,...z.walkthrough].join(' ');
    return [
      {id:t.id+'-theory',topic:t.id,type:'theory',title:t.title,preview:theory,text:theory},
      {id:t.id+'-example',topic:t.id,type:'example',title:t.title+' — пример',preview:z.example,text:example},
      ...D.questions.filter(q=>q.topic===t.id).map(q=>({id:q.id,topic:t.id,type:'question',title:q.prompt,preview:q.prompt,text:[q.prompt,q.answer,...q.followups].join(' ')}))
    ];
  }).map(doc=>({...doc,normalizedTitle:searchText(doc.title),normalizedText:searchText(doc.text),normalizedTopic:searchText(T.get(doc.topic).title+' '+L.get(T.get(doc.topic).lesson).title)}));
  function findDocuments(query){
    const terms=searchTerms(query);if(!terms.length)return [];
    const phrase=searchText(query);
    return searchDocuments.flatMap(doc=>{
      let score=0;
      for(const alternatives of terms){
        if(alternatives.some(term=>doc.normalizedTitle.includes(term)))score+=10;
        else if(alternatives.some(term=>doc.normalizedTopic.includes(term)))score+=6;
        else if(alternatives.some(term=>doc.normalizedText.includes(term)))score+=2;
        else return [];
      }
      if(doc.normalizedTitle===phrase)score+=40;
      else if(doc.normalizedTitle.includes(phrase))score+=15;
      return [{...doc,score}];
    }).sort((a,b)=>b.score-a.score||a.title.localeCompare(b.title,'ru'));
  }
  function highlighted(text,query,short=false){
    const needles=[...new Set(searchTerms(query).flat())].filter(Boolean).sort((a,b)=>b.length-a.length);
    const escaped=needles.map(s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'));
    const regex=escaped.length?new RegExp(escaped.join('|'),'giu'):null;
    let value=String(text);
    if(short&&value.length>210){
      const hit=regex?regex.exec(normalize(value)):null;
      const start=Math.max(0,(hit?.index||0)-65),end=Math.min(value.length,start+210);
      value=(start?'…':'')+value.slice(start,end)+(end<value.length?'…':'');
      if(regex)regex.lastIndex=0;
    }
    if(!regex)return e(value);
    let result='',last=0;
    for(const match of value.matchAll(regex)){
      result+=e(value.slice(last,match.index))+'<mark>'+e(match[0])+'</mark>';last=match.index+match[0].length;
    }
    return result+e(value.slice(last));
  }
  function searchResult(doc,query){
    const t=T.get(doc.topic);
    const href=doc.type==='question'?link('lesson',t.lesson,doc.id):link('lesson',t.lesson)+(doc.type==='example'?'#example-':'#topic-')+t.id;
    return `<a class="search-result" data-search-type="${doc.type}" href="${href}"><div class="row spread"><span class="search-kind">${searchTypes[doc.type]}</span>${doc.type==='question'?`<span class="small muted">${e(ratings[questionRating(doc.id)])}</span>`:''}</div><strong>${highlighted(doc.title,query)}</strong>${doc.type==='question'?'':`<p>${highlighted(doc.preview,query,true)}</p>`}<span class="search-result-action">${doc.type==='question'?'Попробовать ответить':doc.type==='example'?'Открыть разбор':'Читать объяснение'} →</span></a>`;
  }
  function renderSearch(host){
    const ui=searchState[host],box=document.getElementById(host==='global'?'global-search-results':'search-results');
    if(!box)return;
    const query=ui.query.trim();
    if(host==='inline')document.getElementById('lesson-grid').hidden=!!query;
    if(!query){
      box.innerHTML=host==='global'?`<p class="muted small">Ищи по названию, фразе из объяснения или коду. Русские и английские термины тоже подходят.</p><div class="row">${['satisfies','Promise','замыкания','контекст'].map(q=>`<button data-action="search-suggestion" data-host="${host}" data-query="${q}">${q}</button>`).join('')}</div>`:'';return;
    }
    const found=findDocuments(query),counts={all:found.length,theory:0,question:0,example:0};
    found.forEach(doc=>counts[doc.type]++);
    const groups=new Map();
    for(const doc of found){
      if(ui.type!=='all'&&doc.type!==ui.type)continue;
      if(!groups.has(doc.topic))groups.set(doc.topic,{score:doc.score,docs:[]});
      groups.get(doc.topic).docs.push(doc);
    }
    const allGroups=[...groups.entries()].sort((a,b)=>b[1].score-a[1].score);
    box.innerHTML=`<nav class="search-types" aria-label="Тип результата">${Object.entries(searchTypes).map(([id,label])=>`<button data-action="search-filter" data-host="${host}" data-type="${id}" aria-pressed="${ui.type===id}">${label} <span>${counts[id]}</span></button>`).join('')}</nav><p class="small muted search-count" role="status">${allGroups.length?`Тем: ${allGroups.length}. Совпадений: ${ui.type==='all'?counts.all:counts[ui.type]}.`:found.length?'В этом типе нет совпадений. Попробуй «Все».':'Совпадений нет. Попробуй другое слово, английский термин или более короткую фразу.'}</p>${allGroups.slice(0,ui.limit).map(([id,group])=>{
      const t=T.get(id),l=L.get(t.lesson),docs=group.docs;
      const content=docs.filter(d=>d.type!=='question').sort((a,b)=>a.type==='theory'?-1:b.type==='theory'?1:0);
      const questions=docs.filter(d=>d.type==='question');
      return `<section class="search-topic"><div class="search-topic-label">Урок ${String(l.number).padStart(2,'0')} · ${e(l.title)}</div><h3>${highlighted(t.title,query)}</h3>${content.map(d=>searchResult(d,query)).join('')}${questions.slice(0,2).map(d=>searchResult(d,query)).join('')}${questions.length>2?`<details class="search-more-questions"><summary>Ещё вопросов по теме: ${questions.length-2}</summary>${questions.slice(2).map(d=>searchResult(d,query)).join('')}</details>`:''}</section>`;
    }).join('')}${allGroups.length>ui.limit?`<button data-action="search-more" data-host="${host}">Ещё темы (${allGroups.length-ui.limit})</button>`:''}`;
  }
  function ensureSearchDialog(){
    if(document.getElementById('global-search-dialog'))return;
    const dialog=document.createElement('dialog');dialog.id='global-search-dialog';dialog.className='global-search-dialog';dialog.setAttribute('aria-labelledby','global-search-title');
    dialog.innerHTML=`<div class="global-search-header"><div class="row spread"><h2 id="global-search-title">Поиск по всем урокам</h2><button data-action="close-search" aria-label="Закрыть поиск">✕</button></div><label class="small" for="global-search-input">Найти объяснение, вопрос или пример</label><input id="global-search-input" class="search" type="search" maxlength="200" autocomplete="off" placeholder="Например: allSettled, зависимость, замыкания…"></div><div id="global-search-results" class="global-search-results"></div>`;
    document.body.append(dialog);
    dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
  }
  function openSearch(){
    ensureSearchDialog();const dialog=document.getElementById('global-search-dialog');
    renderSearch('global');if(!dialog.open)dialog.showModal();
    const input=document.getElementById('global-search-input');input.value=searchState.global.query;input.focus();input.select();
  }
  function shuffle(arr) {
    const out=[...arr];
    for(let i=out.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[out[i],out[j]]=[out[j],out[i]];}
    return out;
  }
  function validate(raw) {
    if(!raw || typeof raw!=='object' || raw.version!==1 || !raw.answers || !raw.ratings || !raw.read || !['answers','ratings','read'].every(k=>typeof raw[k]==='object'&&!Array.isArray(raw[k]))) throw new Error('Неизвестный формат прогресса. Нужен экспорт этого тренажёра версии 1.');
    const clean=emptyState();
    for(const [id,value] of Object.entries(raw.answers)) if(Q.has(id) && typeof value==='string' && value.length<=100000) clean.answers[id]=value;
    for(const [id,value] of Object.entries(raw.ratings)) if(Q.has(id) && ['forgot','partial','know'].includes(value)) clean.ratings[id]=value;
    for(const [id,value] of Object.entries(raw.read)) if(T.has(id) && typeof value==='boolean') clean.read[id]=value;
    for(const [id,value] of Object.entries(raw.updated||{})) if(Q.has(id) && typeof value==='string') clean.updated[id]=value;
    for(const [id,value] of Object.entries(raw.work||{})) {
      const q=Q.get(id); if(!q || !value || typeof value!=='object') continue;
      if(q.order && Array.isArray(value.order) && value.order.length===q.order.length && new Set(value.order).size===q.order.length && value.order.every(n=>Number.isInteger(n)&&n>=0&&n<q.order.length)) clean.work[id]={order:value.order};
      if(q.pairs && Array.isArray(value.matches) && value.matches.length===q.pairs.length && value.matches.every(n=>Number.isInteger(n)&&n>=-1&&n<q.pairs.length)) clean.work[id]={matches:value.matches};
    }
    const run=raw.interview;
    if(run && Array.isArray(run.ids) && run.ids.length===10 && new Set(run.ids).size===10 && run.ids.every(id=>Q.has(id)) && Number.isInteger(run.index) && run.index>=0 && run.index<=10) clean.interview={ids:run.ids,index:run.index};
    return clean;
  }
  function storageWarning(message) {
    storageOK=false;
    const box=document.getElementById('storage-warning');box.hidden=false;
    box.textContent=message+' Ответы доступны в текущей вкладке. Сохрани JSON через «Прогресс», чтобы не потерять их.';
  }
  try {const raw=localStorage.getItem(KEY);if(raw) state=validate(JSON.parse(raw));localStorage.setItem(KEY,JSON.stringify(state));}
  catch {storageWarning('Браузер не сохранил прогресс или прежний файл повреждён.');}
  function save(){if(!storageOK)return;try{localStorage.setItem(KEY,JSON.stringify(state));}catch{storageWarning('Локальное хранилище недоступно или заполнено.');}}
  function toast(message){const box=document.getElementById('toast');box.textContent=message;clearTimeout(toastTimer);toastTimer=setTimeout(()=>box.textContent='',4500);}
  const questionRating = id => state.ratings[id] || 'none';
  function stats(lesson){
    const qs=D.questions.filter(q=>!lesson||q.lesson===lesson);
    const ts=D.topics.filter(t=>!lesson||t.lesson===lesson);
    return {read:ts.filter(t=>state.read[t.id]).length,total:ts.length,know:qs.filter(q=>questionRating(q.id)==='know').length,rated:qs.filter(q=>questionRating(q.id)!=='none').length,questions:qs.length};
  }
  function shell(content,title){
    const nav=[['home','Уроки'],['review','Повторение'],['interview','Собеседование'],['progress','Прогресс'],['coverage','Реестр тем']];
    document.title=title+' · Собеседование';
    document.getElementById('app').innerHTML=`<div class="layout"><aside class="sidebar"><a class="brand" href="${link()}">собес /<br>можно объяснить<span>Frontend study room</span></a><nav class="main-nav" aria-label="Главная навигация">${nav.map(([v,n])=>`<a href="${link(v)}" ${view===v?'aria-current="page"':''}>${n}</a>`).join('')}</nav><nav class="lesson-nav" aria-label="Все уроки">${D.lessons.map(l=>`<a href="${link('lesson',l.id)}" ${currentLesson===l.id?'aria-current="page"':''}>${String(l.number).padStart(2,'0')} / ${e(l.title)}</a>`).join('')}</nav><div class="footer-note">Твоя заметка + документация.<br>Понять, затем вспомнить.<br><a href="${e(D.notion)}" target="_blank" rel="noopener">Открыть Notion ↗</a></div></aside><div class="content"><div class="topline"><span>ПОДГОТОВКА К СОБЕСЕДОВАНИЯМ</span><button class="global-search-open" data-action="open-search" aria-label="Поиск по всем урокам"><span aria-hidden="true">⌕</span><span class="search-open-label">Поиск по урокам</span><kbd>Ctrl K</kbd></button></div><main id="main" tabindex="-1">${content}</main><footer class="page-footer">Материал обновлён ${e(D.date)}. Ответы оцениваешь ты — по образцу и ключевым пунктам. <a href="${link('progress')}">Сохранить копию прогресса</a></footer></div></div>`;
  }
  function sources(ids,notion=false){return `<div class="sources">${notion?`<a href="${e(D.notion)}" target="_blank" rel="noopener">Твоя заметка Notion ↗</a>`:''}${ids.map(id=>D.sources[id]?`<a href="${e(D.sources[id].url)}" target="_blank" rel="noopener">${e(D.sources[id].title)} ↗</a>`:'').join('')}</div>`;}
  function progressStats(){const s=stats();return `<div class="stats"><div class="stat"><strong>${D.lessons.length}</strong><span>тематических уроков</span></div><div class="stat"><strong>${s.read}<span> / ${s.total}</span></strong><span>разделов прочитано</span></div><div class="stat"><strong>${s.know}<span> / ${s.questions}</span></strong><span>могу объяснить</span></div></div>`;}
  function home(){
    const next=D.lessons.find(l=>l.topics.some(id=>!state.read[id]))||D.lessons[0];
    shell(`<section class="hero"><div class="hero-grid"><div><div class="eyebrow">Теория → вспомнить → объяснить</div><h1>Знать — это суметь<br>рассказать своими словами.</h1><p>Объяснения по шагам, разобранные примеры и вопросы без подсказок. Сначала понять тему, затем научиться рассказывать о ней.</p><div class="row"><a class="button primary" href="${link('lesson',next.id)}">${stats().read?'Продолжить':'Начать с первого урока'} →</a><a class="button" href="${link('review')}">Повторить вопросы</a></div></div><div class="orbit" aria-hidden="true">{ }</div></div></section>${progressStats()}<div class="row spread section-heading"><h2>Твоя программа</h2><span class="small muted">${D.topics.length} разделов · ${D.questions.length} вопросов</span></div><label for="search">Найти объяснение, вопрос или пример</label><input id="search" class="search" maxlength="200" type="search" placeholder="Например: satisfies, Promise, контекст…" autocomplete="off"><div id="search-results"></div><div class="lesson-grid section-heading" id="lesson-grid">${D.lessons.map(l=>{const s=stats(l.id);return `<a class="lesson-card" href="${link('lesson',l.id)}"><span class="card-number">УРОК ${String(l.number).padStart(2,'0')}</span><h3>${e(l.title)}</h3><p>${e(l.subtitle)}</p><div class="card-foot"><span>${l.topics.length} разделов · ${s.questions} вопросов</span><span>${s.know} могу объяснить ↗</span></div><div class="track" aria-label="Прочитано ${s.read} из ${s.total} разделов"><span style="width:${s.read/s.total*100}%"></span></div></a>`;}).join('')}</div><div class="panel"><h2>Как заниматься</h2><p>Прочитай объяснение и проследи пример по шагам. В конце раздела есть короткий ответ для собеседования. Затем попробуй ответить без подсказок и сверься с образцом.</p><p class="small muted">В списках проверяются все элементы: четыре комбинатора Promise, пять принципов SOLID и каждый пункт обозначенного учебного набора. Для сложной теории есть небольшие примеры кода.</p></div>`,'Твоя подготовка');
  }
  function readButton(t){return `<button data-action="read" data-topic="${t.id}" aria-pressed="${!!state.read[t.id]}" class="${state.read[t.id]?'lesson-done':''}">${state.read[t.id]?'✓ Прочитано':'Отметить прочитанным'}</button>`;}
  function theory(t,n){
    const fromNotion=t.notion||D.coverage.some(r=>r.origin==='Notion'&&r.topic===t.id);
    const z=t.explanation, code=z.code||t.code;
    return `<section class="theory" id="topic-${t.id}"><div class="topic-index">РАЗДЕЛ ${String(n+1).padStart(2,'0')}</div><h2>${e(t.title)}</h2><p class="explanation-context">${e(z.context)}</p><h3>Как это работает — по шагам</h3><ol class="explanation-steps">${z.steps.map(step=>`<li>${e(step)}</li>`).join('')}</ol><div class="worked-example" id="example-${t.id}"><h3>Разберём на примере</h3><p>${e(z.example)}</p>${code?`<pre><code>${e(code)}</code></pre>`:''}${z.walkthrough.length?`<ol>${z.walkthrough.map(line=>`<li>${e(line)}</li>`).join('')}</ol>`:''}</div><details class="topic-reference" ${t.drill?'open':''}><summary>Термины и элементы темы · ${t.items.length}</summary><dl>${t.items.map(i=>`<dt>${e(i.name)}</dt><dd>${e(i.detail)}</dd>`).join('')}</dl></details><div class="interview-takeaway"><h3>Коротко для собеседования</h3><p>${e(z.takeaway)}</p></div>${t.note?`<div class="notice">${e(t.note)}</div>`:''}<div class="row spread" style="margin-top:22px">${readButton(t)}<button data-action="topic-practice" data-topic="${t.id}">Вопросы по разделу →</button></div>${sources(t.sources,fromNotion)}</section>`;
  }
  function lesson(){
    const l=L.get(params.get('lesson'));
    if(!l){shell(`<div class="empty"><h1>Урок не найден</h1><a href="${link()}">Вернуться к программе</a></div>`,'Урок не найден');return;}
    currentLesson=l.id; if(params.get('question'))lessonMode='practice';
    const s=stats(l.id);
    shell(`<section class="hero"><div class="eyebrow">Урок ${String(l.number).padStart(2,'0')} / ${D.lessons.length}</div><h1>${e(l.title)}</h1><p>${e(l.subtitle)}. Объяснение, разбор примера и короткий итог для собеседования.</p><div class="row"><span>${l.topics.length} разделов</span><span>·</span><span>${s.questions} вопросов</span></div></section><div class="tabs" aria-label="Режим урока"><button data-action="mode" data-mode="theory" aria-pressed="${lessonMode==='theory'}">01 · Теория</button><button data-action="mode" data-mode="practice" aria-pressed="${lessonMode==='practice'}">02 · Вспомнить и объяснить</button></div><div id="lesson-content"></div><section class="panel" id="mixed"><div class="eyebrow">Переключиться на другую тему</div><h2>Три вопроса вперемешку</h2><p class="small muted" id="mixed-help"></p><button data-action="mix">Получить три вопроса</button><div id="mixed-questions"></div></section><div class="row spread"><a class="button" href="${l.number>1?link('lesson',D.lessons[l.number-2].id):link()}">← ${l.number>1?'Предыдущий урок':'Все уроки'}</a>${l.number<D.lessons.length?`<a class="button primary" href="${link('lesson',D.lessons[l.number].id)}">Следующий урок →</a>`:`<a class="button primary" href="${link('interview')}">Смешанное собеседование →</a>`}</div>`,l.title);
    renderLessonContent();
    if(params.get('question')) setTimeout(()=>document.getElementById('lesson-q-'+params.get('question'))?.scrollIntoView(),50);
  }
  function renderLessonContent(topicFilter=''){
    const l=L.get(currentLesson);if(!l)return;
    const panel=document.getElementById('lesson-content');
    if(lessonMode==='theory')panel.innerHTML=`<nav class="topic-links" aria-label="Разделы урока">${l.topics.map(id=>`<a href="#topic-${id}">${e(T.get(id).title)}</a>`).join('')}</nav>`+l.topics.map((id,n)=>theory(T.get(id),n)).join('');
    else panel.innerHTML=`<div class="notice">Сначала ответь без подсказок. Можно вслух или письменно. Образец и самооценка открываются после твоей попытки.</div><label for="topic-filter">Раздел</label><select id="topic-filter" class="search"><option value="">Все разделы</option>${l.topics.map(id=>`<option value="${id}" ${id===topicFilter?'selected':''}>${e(T.get(id).title)}</option>`).join('')}</select><div id="lesson-questions">${D.questions.filter(q=>q.lesson===l.id&&(!topicFilter||q.topic===topicFilter)).map(q=>exercise(q,'lesson')).join('')}</div>`;
    const s=stats(currentLesson);
    const others=D.lessons.filter(x=>x.id!==currentLesson&&x.topics.some(id=>state.read[id]));
    document.getElementById('mixed-help').textContent=others.length?'Вопросы из других уроков, в которых ты уже отметила прочитанные разделы.':'Другие уроки пока не отмечены прочитанными — повторим текущую тему.';
  }
  function exercise(q,context){
    const dom=context+'-q-'+q.id, rating=questionRating(q.id);
    let interactive='';
    if(q.order){
      const saved=state.work[q.id]?.order;let order=saved||shuffle(q.order.map((_,i)=>i));
      if(!saved&&order.every((n,i)=>n===i)&&order.length>1)[order[0],order[1]]=[order[1],order[0]];
      interactive=`<ol class="order-list">${order.map((n,i)=>`<li data-order-value="${n}"><span class="order-name">${e(q.order[n])}</span><button data-action="move" data-direction="-1" ${i===0?'disabled':''} aria-label="Поднять: ${e(q.order[n])}">↑</button><button data-action="move" data-direction="1" ${i===order.length-1?'disabled':''} aria-label="Опустить: ${e(q.order[n])}">↓</button></li>`).join('')}</ol><button data-action="check-order">Проверить порядок</button><div class="feedback" role="status"></div>`;
    }
    if(q.pairs){
      const options=shuffle(q.pairs.map((_,i)=>i));
      interactive=`<div class="match-grid">${q.pairs.map((pair,i)=>`<label for="${dom}-pair-${i}">${e(pair.name)}<select id="${dom}-pair-${i}" data-pair="${i}"><option value="-1">Выбери объяснение…</option>${options.map(n=>`<option value="${n}" ${state.work[q.id]?.matches?.[i]===n?'selected':''}>${e(q.pairs[n].detail)}</option>`).join('')}</select></label>`).join('')}</div><button data-action="check-match">Проверить пары</button><div class="feedback" role="status"></div>`;
    }
    return `<article class="question" id="${dom}" data-q="${q.id}"><div class="row spread"><span class="pill">${e(labels[q.kind])}</span><span class="small muted" data-rating-label>${e(ratings[rating])}</span></div><h3>${e(q.prompt)}</h3><div class="small muted">${e(L.get(q.lesson).title)} / ${e(T.get(q.topic).title)}</div>${q.code?`<pre><code>${e(q.code)}</code></pre>`:''}${interactive}<label for="${dom}-answer" style="margin-top:15px">Твой ответ <span class="muted">— можно ответить вслух</span></label><textarea id="${dom}-answer" data-answer="${q.id}" placeholder="Сначала попробуй вспомнить…">${e(state.answers[q.id]||'')}</textarea><div class="row"><button class="primary" data-action="reveal" aria-expanded="false" aria-controls="${dom}-solution">Показать образец и свериться</button><a class="small" href="${link('lesson',q.lesson)}#topic-${q.topic}">Вернуться к теории</a></div><div class="answer" id="${dom}-solution" hidden><h3>${q.kind==='experience'?'Структура ответа':'Образец ответа'}</h3><p>${e(q.answer)}</p><details><summary>Ключевые пункты для самопроверки</summary><div class="checklist">${q.check.map((c,i)=>`<label><input type="checkbox"> <span>${e(c)}</span></label>`).join('')}</div></details>${q.followups?.length?`<div class="followups"><p>Уточнения интервьюера</p><ol>${q.followups.map(f=>`<li>${e(f)}</li>`).join('')}</ol></div>`:''}<div class="ratings" aria-label="Самооценка ответа">${['forgot','partial','know'].map(r=>`<button data-action="rate" data-rating="${r}" aria-pressed="${rating===r}">${ratings[r]}</button>`).join('')}</div>${sources(q.sources,q.notion)}</div></article>`;
  }
  function review(){
    shell(`<div class="eyebrow">Повторение</div><h1>Что хочется<br>объяснить увереннее?</h1><p class="muted">Выбери тему и самооценку. Все пункты наборов доступны отдельно, поэтому ничего не теряется при случайном выборе.</p><div class="filters"><label>Тема<select id="review-lesson"><option value="">Все уроки</option>${D.lessons.map(l=>`<option value="${l.id}">${e(l.title)}</option>`).join('')}</select></label><label>Самооценка<select id="review-rating"><option value="weak">Не помню + частично</option><option value="all">Все вопросы</option>${Object.entries(ratings).map(([id,n])=>`<option value="${id}">${n}</option>`).join('')}</select></label><button data-action="shuffle-review">Перемешать</button></div><p id="review-count" class="small muted" aria-live="polite"></p><div id="review-questions"></div><button id="review-more" data-action="more-review" hidden>Показать ещё 15</button>`,'Повторение');
    reviewSelection();
  }
  function reviewSelection(){
    const lesson=document.getElementById('review-lesson').value,r=document.getElementById('review-rating').value;
    reviewIds=shuffle(D.questions.filter(q=>(!lesson||q.lesson===lesson)&&(r==='all'||(r==='weak'?['forgot','partial'].includes(questionRating(q.id)):questionRating(q.id)===r))).map(q=>q.id));
    reviewLimit=15;renderReview();
  }
  function renderReview(){
    document.getElementById('review-count').textContent=`Найдено: ${reviewIds.length}. Показано: ${Math.min(reviewLimit,reviewIds.length)}.`;
    document.getElementById('review-questions').innerHTML=reviewIds.length?reviewIds.slice(0,reviewLimit).map(id=>exercise(Q.get(id),'review')).join(''):`<div class="empty">В этой выборке пока нет вопросов. Выбери «Все вопросы» или «Без оценки», чтобы начать.</div>`;
    document.getElementById('review-more').hidden=reviewLimit>=reviewIds.length;
  }
  function newInterview(){
    const lessonOrder=shuffle(D.lessons);let ids=[];
    for(const l of lessonOrder){const candidates=D.questions.filter(q=>q.lesson===l.id&&!q.id.includes('-item-'));ids.push(shuffle(candidates)[0].id);if(ids.length===10)break;}
    state.interview={ids,index:0};save();renderInterview();
  }
  function interview(){
    shell(`<div class="eyebrow">Практика переключения</div><h1>Десять вопросов.<br>Разные темы.</h1><p class="muted">Ответь как на собеседовании: определение, принцип работы, пример, ограничения. Затем раскрой образец и уточнения.</p><div id="interview-run"></div>`,'Мини-собеседование');renderInterview();
  }
  function renderInterview(){
    const box=document.getElementById('interview-run'),run=state.interview;
    if(!run){box.innerHTML='<div class="panel"><h2>Начать смешанное собеседование</h2><p>Десять вопросов из десяти разных уроков. Можно пропустить вопрос и вернуться к теме позже.</p><button class="primary" data-action="new-interview">Начать собеседование →</button></div>';return;}
    const progress=`<div class="interview-progress" aria-label="Пройдено ${run.index} из 10">${run.ids.map((_,i)=>`<span class="${i<run.index?'done':i===run.index?'current':''}"></span>`).join('')}</div>`;
    if(run.index>=run.ids.length){box.innerHTML=`${progress}<div class="panel"><span class="pill green">Раунд завершён</span><h2 style="margin-top:16px">Ты прошла десять вопросов</h2><ul>${run.ids.map(id=>`<li>${e(Q.get(id).prompt)} <span class="small muted">— ${e(ratings[questionRating(id)])}</span></li>`).join('')}</ul><div class="row"><a class="button primary" href="${link('review')}">Повторить сложное</a><button data-action="new-interview">Новый раунд</button></div></div>`;return;}
    const q=Q.get(run.ids[run.index]);
    box.innerHTML=`${progress}<div class="row spread"><span class="small muted">Вопрос ${run.index+1} / 10</span><button data-action="new-interview">Новый раунд</button></div>${exercise(q,'interview')}<div class="row spread"><button data-action="interview-prev" ${run.index===0?'disabled':''}>← Предыдущий</button><button data-action="interview-skip">Пропустить</button><button class="primary" data-action="interview-next">${run.index===9?'Завершить раунд':'Следующий вопрос →'}</button></div>`;
  }
  function coverage(){
    const included=D.coverage.filter(r=>r.status==='included'),excluded=D.coverage.filter(r=>r.status==='excluded');
    shell(`<div class="eyebrow">Покрытие материала</div><h1>У каждого вопроса<br>есть своё место.</h1><p class="muted">Реестр исходных заголовков Notion и вопросов из чата. Повторы ведут в общий раздел. Исключённые темы не участвуют в обучении.</p><div class="row"><span class="pill green">${included.length} записей включено</span><span class="pill">${D.topics.length} разделов</span><span class="pill">${D.questions.length} вопросов</span></div><label for="coverage-search" style="margin-top:22px">Найти запись</label><input class="search" type="search" id="coverage-search" placeholder="Заголовок или вопрос…"><div id="coverage-table"></div><details class="panel"><summary>Исключено по согласованному плану · ${excluded.length}</summary><ul>${excluded.map(r=>`<li>${e(r.title)} <span class="small muted">— ${e(r.reason)}</span></li>`).join('')}</ul></details>`,'Реестр тем');renderCoverage('');
  }
  function renderCoverage(query){
    const rows=D.coverage.filter(r=>r.status==='included'&&normalize(r.title).includes(normalize(query)));
    document.getElementById('coverage-table').innerHTML=`<p class="small muted">Записей: ${rows.length}</p><div class="table-wrap"><table><thead><tr><th>Источник</th><th>Заголовок / вопрос</th><th>Урок и упражнение</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${e(r.origin)}</td><td class="coverage-title">${e(r.title)}</td><td><a href="${link('lesson',r.lesson,r.question)}">${e(L.get(r.lesson).title)} →</a></td></tr>`).join('')}</tbody></table></div>`;
  }
  function progress(){
    const s=stats();
    shell(`<div class="eyebrow">Твоя работа сохраняется</div><h1>Прочитать и объяснить —<br>разные отметки.</h1><p class="muted">${s.rated} вопросов оценено. Написанные ответы сохраняются при вводе. Изменение самооценки не отмечает теорию прочитанной.</p>${progressStats()}<section class="panel"><h2>Копия прогресса</h2><p>Экспортируй JSON перед переносом папки или сменой браузера. Импорт объединяет данные: совпадающие записи заменяются значениями из файла, остальные сохраняются.</p><button class="primary" data-action="export">Скачать прогресс JSON</button><label for="import-file" style="margin-top:22px">Импортировать сохранённый прогресс</label><input id="import-file" type="file" accept=".json,application/json"><p class="small muted" style="margin-top:12px">Локальная память относится к этому браузеру и пути папки. Файлы не отправляются в сеть.</p></section><div class="table-wrap"><table><thead><tr><th>Урок</th><th>Прочитано</th><th>Могу объяснить</th></tr></thead><tbody>${D.lessons.map(l=>{const v=stats(l.id);return `<tr><td><a href="${link('lesson',l.id)}">${e(l.title)}</a></td><td>${v.read} / ${v.total}</td><td>${v.know} / ${v.questions}</td></tr>`;}).join('')}</tbody></table></div>`,'Твой прогресс');
  }
  function normalize(text){return String(text).toLocaleLowerCase('ru').replaceAll('ё','е');}
  function search(query){
    searchState.inline.query=query;searchState.inline.limit=12;renderSearch('inline');
  }
  function updateRatingLabels(id){
    document.querySelectorAll('.question').forEach(card=>{if(card.dataset.q!==id)return;card.querySelector('[data-rating-label]').textContent=ratings[questionRating(id)];card.querySelectorAll('[data-action=rate]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.rating===questionRating(id))));});
  }
  function markRead(id){state.read[id]=!state.read[id];save();document.querySelectorAll('[data-action=read]').forEach(b=>{if(b.dataset.topic===id){b.setAttribute('aria-pressed',String(!!state.read[id]));b.textContent=state.read[id]?'✓ Прочитано':'Отметить прочитанным';b.classList.toggle('lesson-done',!!state.read[id]);}});toast(state.read[id]?'Раздел отмечен прочитанным':'Отметка чтения снята');}
  document.addEventListener('input',event=>{
    const el=event.target;
    if(el.matches('[data-answer]')){state.answers[el.dataset.answer]=el.value;save();document.querySelectorAll('[data-answer]').forEach(other=>{if(other!==el&&other.dataset.answer===el.dataset.answer)other.value=el.value;});}
    if(el.id==='search')search(el.value);
    if(el.id==='global-search-input'){searchState.global.query=el.value;searchState.global.limit=12;renderSearch('global');}
    if(el.id==='coverage-search')renderCoverage(el.value);
  });
  document.addEventListener('change',async event=>{
    const el=event.target;
    if(el.id==='topic-filter')renderLessonContent(el.value);
    if(el.id==='review-lesson'||el.id==='review-rating')reviewSelection();
    if(el.matches('[data-pair]')){const card=el.closest('[data-q]');state.work[card.dataset.q]={matches:[...card.querySelectorAll('[data-pair]')].map(s=>Number(s.value))};save();}
    if(el.id==='import-file'&&el.files.length){
      try{
        const file=el.files[0];if(file.size>5_000_000)throw new Error('Файл слишком большой: максимум 5 МБ.');
        const clean=validate(JSON.parse(await file.text()));
        for(const field of ['answers','ratings','read','work','updated'])Object.assign(state[field],clean[field]);
        if(clean.interview)state.interview=clean.interview;save();progress();toast('Прогресс импортирован и объединён с текущим.');
      }catch(err){toast('Импорт не выполнен: '+err.message);el.value='';}
    }
  });
  document.addEventListener('click',event=>{
    const b=event.target.closest('[data-action]');if(!b)return;
    const action=b.dataset.action, card=b.closest('[data-q]'), q=card?Q.get(card.dataset.q):null;
    if(action==='open-search')openSearch();
    if(action==='close-search')document.getElementById('global-search-dialog').close();
    if(action==='search-filter'){searchState[b.dataset.host].type=b.dataset.type;searchState[b.dataset.host].limit=12;renderSearch(b.dataset.host);}
    if(action==='search-more'){searchState[b.dataset.host].limit+=12;renderSearch(b.dataset.host);}
    if(action==='search-suggestion'){const ui=searchState[b.dataset.host];ui.query=b.dataset.query;ui.type='all';document.getElementById('global-search-input').value=ui.query;renderSearch(b.dataset.host);}
    if(action==='read')markRead(b.dataset.topic);
    if(action==='mode'){lessonMode=b.dataset.mode;document.querySelectorAll('[data-action=mode]').forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.mode===lessonMode)));renderLessonContent();}
    if(action==='topic-practice'){lessonMode='practice';document.querySelectorAll('[data-action=mode]').forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.mode===lessonMode)));renderLessonContent(b.dataset.topic);document.getElementById('lesson-content').scrollIntoView();}
    if(action==='reveal'){const answer=card.querySelector('.answer');answer.hidden=!answer.hidden;b.setAttribute('aria-expanded',String(!answer.hidden));b.textContent=answer.hidden?'Показать образец и свериться':'Скрыть образец';}
    if(action==='rate'){state.ratings[q.id]=b.dataset.rating;state.updated[q.id]=new Date().toISOString();save();updateRatingLabels(q.id);toast('Самооценка сохранена: '+ratings[b.dataset.rating]);}
    if(action==='mix'){
      const studied=new Set(D.topics.filter(t=>t.lesson!==currentLesson&&state.read[t.id]).map(t=>t.lesson));
      const pool=D.questions.filter(q=>studied.size?studied.has(q.lesson):q.lesson===currentLesson);
      const diverse=[];for(const item of shuffle(pool))if(!diverse.some(x=>x.topic===item.topic)){diverse.push(item);if(diverse.length===3)break;}
      if(diverse.length<3)diverse.push(...shuffle(pool.filter(q=>!diverse.some(x=>x.id===q.id))).slice(0,3-diverse.length));
      mixedIds=diverse.map(q=>q.id);document.getElementById('mixed-questions').innerHTML=diverse.map(q=>exercise(q,'mixed')).join('');
    }
    if(action==='move'){
      const row=b.closest('li'),list=row.parentElement,rows=[...list.children],old=rows.indexOf(row),next=old+Number(b.dataset.direction);
      if(next<0||next>=rows.length)return;
      if(next<old)list.insertBefore(row,rows[next]);else list.insertBefore(rows[next],row);
      [...list.children].forEach((li,i)=>{li.querySelector('[data-direction="-1"]').disabled=i===0;li.querySelector('[data-direction="1"]').disabled=i===rows.length-1;});
      state.work[q.id]={order:[...list.children].map(li=>Number(li.dataset.orderValue))};save();
      const feedback=card.querySelector('.feedback');feedback.textContent='';
      const focus=row.querySelector(`[data-direction="${b.dataset.direction}"]`);(focus.disabled?row.querySelector('button:not(:disabled)'):focus)?.focus();
    }
    if(action==='check-order'){
      const values=[...card.querySelectorAll('[data-order-value]')].map(li=>Number(li.dataset.orderValue));
      state.work[q.id]={order:values};save();const correct=values.every((n,i)=>n===i),feedback=card.querySelector('.feedback');
      feedback.classList.toggle('wrong',!correct);feedback.textContent=correct?'Порядок верный. Теперь объясни связи между этапами.':'Порядок пока отличается. Переставь этапы или раскрой образец с объяснением.';
    }
    if(action==='check-match'){
      const selects=[...card.querySelectorAll('[data-pair]')],filled=selects.every(s=>s.value!=='-1'),correct=selects.filter((s,i)=>Number(s.value)===i).length,feedback=card.querySelector('.feedback');
      feedback.classList.toggle('wrong',correct!==selects.length);feedback.textContent=filled?`Совпало ${correct} из ${selects.length}. ${correct===selects.length?'Объясни различия своими словами.':'Проверь пары и сравни с образцом.'}`:'Сначала выбери объяснение для каждого понятия.';
    }
    if(action==='shuffle-review')reviewSelection();
    if(action==='more-review'){reviewLimit+=15;renderReview();}
    if(action==='new-interview')newInterview();
    if(action==='interview-prev'){state.interview.index=Math.max(0,state.interview.index-1);save();renderInterview();}
    if(action==='interview-next'||action==='interview-skip'){state.interview.index++;save();renderInterview();document.getElementById('interview-run').scrollIntoView();}
    if(action==='export'){
      const blob=new Blob([JSON.stringify({...state,exportedAt:new Date().toISOString()},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='interview-study-progress.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);toast('JSON с ответами и прогрессом скачан.');
    }
  });
  // Keep independent tabs of this same local entry point in sync without overwriting active typing.
  window.addEventListener('storage',event=>{if(event.key===KEY&&event.newValue){try{state=validate(JSON.parse(event.newValue));toast('Прогресс обновлён в другой вкладке. Перезагрузи страницу для обновления отображения.');}catch{ /* Ignore unrelated invalid data. */ }}});
  document.addEventListener('keydown',event=>{
    if(event.key==='Escape'&&document.getElementById('global-search-dialog')?.open){event.preventDefault();document.getElementById('global-search-dialog').close();}
    else if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k'){event.preventDefault();openSearch();}
  });
  ({home,lesson,review,interview,coverage,progress}[view])();
  if(location.hash.startsWith('#topic-')||location.hash.startsWith('#example-'))setTimeout(()=>document.getElementById(location.hash.slice(1))?.scrollIntoView(),50);
})();
