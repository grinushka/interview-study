"""Applied task classification and a few debugging tasks, sharing course question IDs."""

def add_tasks(questions, byid, registry):
    from revision_content import paragraph, example, block_text
    tasks=[
      ('debug-shallow-copy','cloning','Найди ошибку в обновлении профиля. Что изменилось в oldUser и как создать независимую копию изменяемого уровня?',
       'const oldUser = { profile: { name: "Анна" } };\nconst nextUser = { ...oldUser };\nnextUser.profile.name = "Ира";',
       'Spread скопировал только верхний уровень. profile остался общей ссылкой, поэтому oldUser.profile.name тоже стал «Ира». Копировать надо каждый изменяемый уровень.',
       'const nextUser = {\n  ...oldUser,\n  profile: { ...oldUser.profile, name: "Ира" }\n};',
       'Почему два верхних объекта не равны, а profile равны?', 'Spread создаёт новый контейнер, но переносит значения свойств. Значением profile была ссылка на тот же вложенный объект.'),
      ('debug-stale-interval','effect-deps','Найди причину, по которой счётчик после первого тика не растёт. Исправь обновление и добавь cleanup.',
       'useEffect(() => {\n  setInterval(() => setCount(count + 1), 1000);\n}, []);',
       'Callback хранит count из окружения исходного render и каждый раз вычисляет одно значение. Functional updater получает актуальный предыдущий state. Cleanup удаляет подписку таймера при завершении эффекта.',
       'useEffect(() => {\n  const id = setInterval(() => setCount(c => c + 1), 1000);\n  return () => clearInterval(id);\n}, []);',
       'Почему просто убрать [] недостаточно?', 'Эффект будет создавать таймер после каждого commit; без cleanup старые интервалы останутся. Нужно определить корректный жизненный цикл и обновление state.'),
      ('debug-assertion-validation','assertions','Объясни ошибку в обработке внешних данных. Как проверить title перед вызовом строкового метода?',
       'const raw: unknown = { title: 42 };\nconst data = raw as { title: string };\nconsole.log(data.title.toUpperCase());',
       'Assertion не проверяет JSON и не преобразует число в строку. Статический тип обещает строку, но runtime содержит число и вызов метода упадёт. Нужна проверка unknown на границе.',
       'if (typeof raw === "object" && raw !== null\n    && "title" in raw && typeof raw.title === "string") {\n  console.log(raw.title.toUpperCase());\n} else {\n  throw new Error("Некорректный title");\n}',
       'Что изменит satisfies вместо as?', 'satisfies проверяет совместимость выражения при компиляции. Он не валидирует неизвестное внешнее значение в runtime: для него всё равно нужна реальная проверка.'),
      ('debug-dependent-async-scripts','scripts','app.js обращается к глобальному API из vendor.js. Иногда API ещё не существует. Найди причину и предложи способ сохранить порядок.',
       '<script async src="vendor.js"></script>\n<script async src="app.js"></script>',
       'Два async-скрипта выполняются по готовности, а не по порядку HTML. Для зависимых внешних classic scripts можно использовать defer. Другой вариант — выразить зависимости через module imports.',
       '<script defer src="vendor.js"></script>\n<script defer src="app.js"></script>',
       'Какая аналитика подходит для async?', 'Независимая, не требующая готовности соседнего скрипта и не предоставляющая ему обязательный API без отдельного протокола загрузки.'),
      ('debug-component-responsibilities','solid','Компонент таблицы содержит JSX, reconnect WebSocket, проверку прав и форматирование внешнего API. При изменении транспорта приходится переписывать UI. Предложи границы ответственности и объясни, какие принципы помогут.',
       '',
       'Разделить представление таблицы, жизненный цикл соединения, API-адаптер и серверную проверку прав. UI получает нужные данные и действия через узкий контракт. SRP уменьшает независимые причины изменения; DIP помогает заменить транспорт через интерфейс.',
       '',
       'Что не стоит выносить в абстракцию заранее?', 'Не строить универсальную plugin-систему для предполагаемых будущих транспортов без реального требования. Граница должна упрощать текущие изменения и проверку, а не увеличивать число уровней.'),
      ('forms-submit-choice','forms','Форма из 20 полей нужна только при отправке, динамического UI на каждый символ нет. Выбери способ хранения ввода и опиши, что изменится при добавлении live-preview.',
       '',
       'Для начального условия подходит uncontrolled форма с defaultValue и чтением FormData при submit: DOM хранит ввод. Для live-preview может понадобиться controlled state для нужных полей или подписка подходящей формы-библиотеки. Выбор зависит от реакций UI и валидации, а не только числа полей.',
       'function handleSubmit(event) {\n  event.preventDefault();\n  const data = new FormData(event.currentTarget);\n  const title = data.get("title"); // поле имеет name="title"\n  // Проверить и передать данные по контракту API.\n}',
       'Как задать стартовое значение uncontrolled input?', 'Через defaultValue. Это начальное значение, а не управляемый value текущего ввода. Не переключать один input между controlled и uncontrolled без продуманного перехода.'),
    ]
    for id,tid,prompt,code,answer,solution,followup,follow_answer in tasks:
        topic=byid[tid]
        blocks=[paragraph(answer)]
        if solution:blocks.append(example('Один из подходящих вариантов',solution))
        q=dict(id=id,topic=tid,lesson=topic['lesson'],kind='scenario' if id=='forms-submit-choice' else 'debug',
               prompt=prompt,code=code,answerBlocks=blocks,answer=block_text(blocks),sources=topic['sources'],notion=False,
               followups=[dict(question=followup,answerBlocks=[paragraph(follow_answer)])])
        questions.append(q)
        registry.append(dict(origin='Дополнение · Задачник',title=prompt,topic=tid,lesson=topic['lesson'],question=id,status='included'))
    explicit={'cloning-main':'predict','assertions-main':'predict','omit-exclude-main':'predict',
              'effect-deps-main':'predict','keys-vdom-main':'predict','architecture-boundaries-main':'scenario'}
    formats={'code':'code','debug':'debug','scenario':'scenario','order':'order','match':'match'}
    for q in questions:
        value=explicit.get(q['id'],formats.get(q['kind']))
        if value:q['taskFormat']=value
