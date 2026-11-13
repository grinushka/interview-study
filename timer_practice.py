"""Seven small callback/timer exercises from the latest personal Gen note."""

EXERCISES = [
 dict(id='callbacks-practice-main',title='1 / 7 · Подождать, выполнить, уведомить',
      prompt='Напиши runLater(work, onDone): через 3 секунды вызвать синхронную work(), затем передать её результат в onDone. Считай, что work успешно возвращает 42. Что функция возвращает сразу?',
      starter='function runLater(work, onDone) {\n  // Твой код\n}\n// Пример вызова:\nrunLater(() => 6 * 7, result => console.log("Result:", result));',
      solution='function runLater(work, onDone) {\n  return setTimeout(() => {\n    const result = work();\n    onDone(result);\n  }, 3000);\n}',
      explanation='Оба вызова должны находиться внутри отложенного callback. Сначала work возвращает значение, потом onDone получает именно его. Условие задачи считает work синхронной и успешной.',
      timeline='Сейчас: runLater возвращает timer handle → не раньше 3 секунд: work() → сразу после её возврата: onDone(42).',
      pitfall='setTimeout(work(), 3000) вызовет work сейчас и передаст таймеру её результат. Правильно передавать функцию, например () => work().',
      followup=('Как изменится решение, если work возвращает Promise?', 'Нужно дождаться settlement work до onDone: использовать Promise-цепочку или async/await, как в упражнении 3. Возвращаемый timer handle не превращается в Promise результата.')),
 dict(id='callbacks-start-later',title='2 / 7 · Дождаться callback-based работы',
      prompt='Напиши startLater(work, onDone): подождать 3 секунды, затем начать work(done). Эта work ещё через секунду вызывает done(42). Передай результат в onDone только после завершения работы. Считай, что ошибок нет.',
      starter='function startLater(work, onDone) {\n  // Твой код\n}\nfunction work(done) {\n  setTimeout(() => done(42), 1000);\n}',
      solution='function startLater(work, onDone) {\n  return setTimeout(() => {\n    work(onDone);\n  }, 3000);\n}',
      explanation='Передаём onDone как функцию завершения. Именно work знает, когда результат готов. Возврат из work сейчас не означает, что её внутренний таймер уже сработал.',
      timeline='Сейчас: timer handle → не раньше 3 секунд: запуск work → ещё примерно секунда: done(42), то есть переданный onDone.',
      pitfall='work(); onDone(); уведомит слишком рано и не передаст будущий результат. Сигнал готовности должен прийти из work.',
      followup=('Как добавить контракт done(error, result)?', 'Передать обёртку: work((error, result) => { if (error) { onError(error); return; } onDone(result); }). Нужно заранее определить обработчик ошибки и договориться, что work вызывает завершение один раз.')),
 dict(id='callbacks-promise-work',title='3 / 7 · Подождать Promise и обработать ошибку',
      prompt='Напиши startLater(work, onDone): подождать 3 секунды, вызвать work(), возвращающую Promise, дождаться результата и передать его в onDone. Сравни async/await и then. Функция должна вернуть Promise; rejection обработай у вызывающего кода.',
      starter='// work возвращает Promise с результатом 42 через 1 секунду.\nasync function startLater(work, onDone) {\n  // Твой код\n}\n// startLater(work, onDone).catch(onError);',
      solution='const delay = ms => new Promise(resolve => setTimeout(resolve, ms));\n\nasync function startLater(work, onDone) {\n  await delay(3000);\n  const result = await work();\n  return onDone(result);\n}',
      alternate='const delay = ms => new Promise(resolve => setTimeout(resolve, ms));\n\nfunction startLaterChain(work, onDone) {\n  return delay(3000)\n    .then(() => work())\n    .then(result => onDone(result));\n}',
      explanation='Оба варианта связывают ожидания в одну цепочку. await приостанавливает эту async-функцию. В then нужно вернуть work(), чтобы следующий обработчик дождался её результата. Возвращение onDone также связывает его Promise или ошибку с результатом startLater.',
      timeline='Около 3 секунд: work начинает работу → около 4 секунд при успешной work: onDone(42) → Promise startLater завершается после onDone.',
      pitfall='await setTimeout(...) ожидает timer handle, а не будущий callback. Оберни таймер в Promise. При rejection work обработчик успеха onDone не вызывается.',
      followup=('Как обработать ошибку у вызывающего кода?', 'startLater(work, onDone).catch(onError). В async-функции rejection от await становится throw, и возвращённый Promise отклоняется. Синхронная ошибка onDone тоже отклонит этот Promise.')),
 dict(id='callbacks-sequence',title='4 / 7 · Последовательные задержки',
      prompt='Напиши sequence(): вывести A через 3 секунды, затем B через 2 секунды после A, затем done. Сравни вложенные таймеры и async/await. Объясни, от какого момента отсчитывается каждая задержка.',
      starter='function sequence() {\n  // A примерно через 3 секунды\n  // B и done примерно через 5 секунд от начала\n}',
      solution='function sequence() {\n  return setTimeout(() => {\n    console.log("A");\n    setTimeout(() => {\n      console.log("B");\n      console.log("done");\n    }, 2000);\n  }, 3000);\n}',
      alternate='async function sequenceAsync() {\n  const delay = ms => new Promise(resolve => setTimeout(resolve, ms));\n  await delay(3000);\n  console.log("A");\n  await delay(2000);\n  console.log("B");\n  console.log("done");\n}',
      explanation='Вторая задержка начинается только после вывода A. Два таймера, созданные вместе с задержками 3000 и 2000, не описывают такую последовательность: их ожидания начинаются почти одновременно.',
      timeline='Старт → примерно 3 секунды: A → ещё 2 секунды: B → done в том же callback или продолжении функции.',
      pitfall='sequence возвращает handle первого таймера, а sequenceAsync — Promise всей последовательности. Отмена первого таймера после его срабатывания не отменит второй.',
      followup=('Почему реальный вывод может произойти позже 3 и 5 секунд?', 'Указана минимальная задержка до возможности исполнения. Занятый поток, другие задачи, microtasks и throttling фоновой вкладки могут отложить callback. Это не точное расписание реального времени.')),
 dict(id='callbacks-cancel',title='5 / 7 · Вернуть функцию отмены',
      prompt='Напиши schedule(callback): запланировать callback через 3 секунды и сразу вернуть функцию отмены. Покажи, как отменить через секунду, чтобы callback не вывел ничего.',
      starter='function schedule(callback) {\n  // Верни функцию отмены, а не результат clearTimeout.\n}\nconst cancel = schedule(() => console.log("Finished"));\nsetTimeout(cancel, 1000);',
      solution='function schedule(callback) {\n  const timerId = setTimeout(callback, 3000);\n  return () => clearTimeout(timerId);\n}',
      explanation='Замыкание сохраняет timerId и даёт вызывающему коду действие для будущего вызова. Возвращаемая функция cancel сама не выполняется при создании.',
      timeline='Сейчас: создаётся таймер и возвращается cancel → через секунду вызывается cancel → pending callback удалён → на третьей секунде вывода нет.',
      pitfall='return clearTimeout(timerId) отменил бы таймер сразу и вернул undefined. Отмена не может отменить действие callback, который уже выполнился.',
      followup=('Что произойдёт при cancel после завершения callback?', 'Выполненное действие не откатится. clearTimeout относится к ожидающему таймеру; для уже начатой async-операции нужен собственный протокол отмены, например AbortSignal у fetch.')),
 dict(id='callbacks-repeat-three',title='6 / 7 · Три вызова и остановка',
      prompt='Напиши repeat(callback): вызвать callback(1), callback(2), callback(3), первый раз через секунду, затем прекратить повторы. Callback синхронный и успешный. Сравни setInterval и рекурсивный setTimeout.',
      starter='function repeatInterval(callback) {\n  // Три вызова, затем остановка.\n}\n// repeatInterval(n => console.log(n));',
      solution='function repeatInterval(callback) {\n  let count = 0;\n  const id = setInterval(() => {\n    count += 1;\n    if (count === 3) clearInterval(id);\n    callback(count);\n  }, 1000);\n}',
      alternate='function repeatTimeout(callback) {\n  let count = 0;\n  function tick() {\n    count += 1;\n    callback(count);\n    if (count < 3) setTimeout(tick, 1000);\n  }\n  setTimeout(tick, 1000);\n}',
      explanation='Счётчик хранится в замыкании. Interval останавливаем при третьем вызове. Рекурсивный timeout создаёт следующий таймер только после возврата синхронного callback.',
      timeline='Примерно через 1, 2 и 3 секунды: callback получает 1, 2 и 3. Четвёртого вызова нет. При долгом синхронном callback реальная шкала сдвинется.',
      pitfall='Эти решения не ждут Promise, который вернул бы callback. Для асинхронной работы условие другое — смотри упражнение 7.',
      followup=('Как сделать первый вызов немедленным?', 'Для рекурсивного варианта вызвать tick() вместо стартового setTimeout(tick, 1000). Остальные вызовы останутся отложенными. Нужное число вызовов и обработку ошибок всё равно задаёт контракт.')),
 dict(id='callbacks-repeat-async',title='7 / 7 · Async-повторы без наложения',
      prompt='Напиши repeatWork(work): выполнить Promise-based work три раза. Ждать секунду перед первым запуском и секунду после каждого завершения перед следующим. Work занимает 2 секунды. Вывести done после третьего успеха; при rejection остановиться.',
      starter='async function repeatWork(work) {\n  // Не запускай следующую work, пока предыдущая не завершилась.\n}\n// repeatWork(work).catch(console.error);',
      solution='const delay = ms => new Promise(resolve => setTimeout(resolve, ms));\n\nasync function repeatWork(work) {\n  for (let i = 0; i < 3; i += 1) {\n    await delay(1000);\n    await work();\n  }\n  console.log("done");\n}',
      explanation='await work() находится внутри цикла и блокирует переход к следующей итерации этой функции. Rejection выйдет из цикла через отклонённый Promise repeatWork: дальнейших запусков и done не будет.',
      timeline='Примерно: start/end на 1/3 секундах → 4/6 → 7/9 → done. После последнего завершения лишней секунды ожидания нет.',
      pitfall='setInterval(async () => await work(), 1000) не ждёт возвращённый Promise: pending операции могут перекрываться, хотя синхронные участки callback не выполняются одновременно в одном JS-потоке.',
      followup=('Что изменится, если убрать await перед work()?', 'Следующая итерация начнёт своё ожидание сразу после запуска work, не дожидаясь её завершения. Появятся перекрывающиеся pending операции, done может выйти раньше результатов, а rejection work потребует отдельной обработки.')),
]

def add_topic(t, ex, sources):
    sources.update({
      'jsinfo-timers': ('JavaScript.ru: таймеры', 'https://learn.javascript.ru/settimeout-setinterval'),
      'jsinfo-callbacks': ('JavaScript.ru: callbacks', 'https://learn.javascript.ru/callbacks'),
      'jsinfo-async': ('JavaScript.ru: async/await', 'https://learn.javascript.ru/async-await'),
    })
    t('async','callbacks-practice','Практика: callbacks и таймеры · 7 упражнений',
      'Переводи условие во временную последовательность. Сначала выясни, чем работа сообщает завершение: возвратом, callback или Promise.',[
      ('Функция и вызов','fn передаёт функцию; fn() вызывает её сейчас; () => fn(value) создаёт отложенную обёртку.'),
      ('Сейчас и позже','Таймер возвращает handle сейчас, а значение отложенной работы приходит по выбранному контракту.'),
      ('Критерий завершения','Синхронный возврат, done(result) и settlement Promise требуют разной организации последовательности.'),
      ('Отмена и повтор','Хранить handle для отмены; для async-повторов ждать завершения, а не только очередного interval.')],
      EXERCISES[0]['prompt'],'timers promise jsinfo-timers jsinfo-callbacks jsinfo-async',kind='code',notion=True)
    ex('callbacks-practice','Здесь семь небольших задач на написание кода. Это практика механики асинхронности, без разработки приложения. Открой «Вопросы по разделу», попробуй написать решение и только затем раскрой образец. Код в тренажёре не исполняется автоматически.',
      ['Запиши порядок словами: сейчас → ожидание → работа → результат → уведомление.',
       'Выясни, что означает «работа закончилась»: return, вызов done или завершение Promise.',
       'Назови сигнатуру и немедленный результат функции отдельно от будущего результата.',
       'Проверь ошибки, отмену и наложение повторов. Примеры запускай по одному в своей консоли, если хочешь увидеть вывод.'],
      'fn — значение функции; fn() вызывает её немедленно. Обёртка () => fn(value) позволяет передать будущее действие с аргументом. Возвращаемый timer handle нужен для clearTimeout, а не для получения результата fn.',
      'Сначала выбираю сигнал завершения, потом связываю шаги. Синхронную work вызываю внутри timer callback; callback-based work получает onDone; Promise-based work ожидаю через await или возвращаю в then. Для повторов без наложения жду окончание work перед следующей задержкой.',
      code='const later = () => console.log("Потом");\nconst timerId = setTimeout(later, 3000);\n// later передана, а не вызвана при планировании.\n// timerId — handle, не будущий результат console.log.',
      walkthrough=['Задержка задаётся в миллисекундах.','3000 — минимальное ожидание, не обещание точного времени.','Семь упражнений последовательно добавляют новые условия: callback, Promise, несколько задержек, отмену и повторы.'])

def add_questions(questions, byid, registry):
    from revision_content import paragraph, steps, example, block_text
    topic=byid['callbacks-practice']
    for n,item in enumerate(EXERCISES,1):
        blocks=[paragraph(item['explanation']),example('Основное решение',item['solution']),
                steps([item['timeline']], 'Временная шкала'),paragraph(item['pitfall'],'Что легко перепутать')]
        if item.get('alternate'):blocks.insert(2,example('Другой вариант того же порядка',item['alternate']))
        prompt,answer=item['followup']
        q=dict(id=item['id'],topic=topic['id'],lesson='async',kind='code',prompt=item['prompt'],
               exerciseTitle=item['title'],code=item['starter'],answerBlocks=blocks,answer=block_text(blocks),
               followups=[dict(question=prompt,answerBlocks=[paragraph(answer)])],sources=topic['sources'],notion=True)
        if n==1:
            index=next(i for i,q in enumerate(questions) if q['id']==item['id'])
            questions[index]=q
        else:questions.append(q)
        registry.append(dict(origin='Notion · Callbacks practice',title=item['title'],topic=topic['id'],lesson='async',question=item['id'],status='included',url='https://app.notion.com/p/41795f65d6128113ac59c253931bf942'))
