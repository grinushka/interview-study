"""Reviewed teaching additions from Gen notes; no changes to persisted question IDs."""
from member_examples import EXAMPLES as MEMBER_EXAMPLES

def paragraph(text, title='Суть ответа'):
    return dict(type='paragraph', title=title, text=text)

def steps(items, title='Как объяснить по шагам'):
    return dict(type='steps', title=title, items=list(items))

def example(text, code='', walkthrough=()):
    return dict(type='example', title='Разберём на примере', text=text, code=code, items=list(walkthrough))

LOCK_CODE = '''// Все вкладки используют одинаковый lock и ключ.
async function showOnce(event) {
  await navigator.locks.request("notification-history", async () => {
    const key = `shown:${event.id}`;
    const expires = Number(localStorage.getItem(key) || 0);
    if (expires > Date.now()) return;
    // Claim перед показом: выбираем риск пропуска, а не повтора.
    localStorage.setItem(key, String(Date.now() + 86_400_000));
    showToast(event.text); // функция интерфейса приложения
  });
}'''

IDB_CODE = '''// db уже открыт; store claims создан с keyPath: "id".
function claim(db, id) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction("claims", "readwrite");
    let duplicate = false;
    const request = tx.objectStore("claims").add({ id, at: Date.now() });
    request.onerror = (e) => {
      if (request.error.name === "ConstraintError") {
        duplicate = true;
        e.preventDefault(); // ожидаемый дубль не прерывает транзакцию
      }
    };
    tx.oncomplete = () => resolve(!duplicate);
    tx.onabort = () => reject(tx.error || new Error("Transaction aborted"));
  });
}
// Показывать только после commit, а не после request.onsuccess.
if (await claim(db, event.id)) showToast(event.text);'''

LEADER_CODE = '''const bus = new BroadcastChannel("events");
bus.onmessage = ({ data }) => updateUI(data);
const stop = new AbortController();
// Каждая вкладка вызывает этот код; одна получит exclusive lock.
navigator.locks.request("sse-leader", { signal: stop.signal }, async () => {
  if (stop.signal.aborted) return;
  const source = new EventSource("/events");
  source.onmessage = ({ data }) => {
    updateUI(data); // свой BroadcastChannel сообщение не получит
    bus.postMessage(data);
  };
  try {
    await new Promise(resolve => {
      stop.signal.addEventListener("abort", resolve, { once: true });
    });
  } finally { source.close(); }
}).catch(error => {
  if (error.name !== "AbortError") console.error(error);
});
// При явном завершении: stop.abort(); bus.close();'''

POST_CODE = '''const frame = document.querySelector("iframe");
const trusted = "https://widget.example";
window.addEventListener("message", (event) => {
  if (event.origin !== trusted) return;
  if (event.source !== frame.contentWindow) return;
  const data = event.data;
  if (!data || typeof data !== "object") return;
  if (data.type !== "resize" || !Number.isFinite(data.height)) return;
  if (data.height < 100 || data.height > 1200) return;
  frame.style.height = `${data.height}px`;
});
frame.addEventListener("load", () => {
  frame.contentWindow.postMessage({ type: "init" }, trusted);
});'''

def additions(t, ex, sources):
    sources.update({
      'storage-event': ('MDN: storage event', 'https://developer.mozilla.org/en-US/docs/Web/API/Window/storage_event'),
      'shared-worker': ('MDN: SharedWorker', 'https://developer.mozilla.org/en-US/docs/Web/API/SharedWorker'),
      'lock-request': ('MDN: LockManager.request', 'https://developer.mozilla.org/en-US/docs/Web/API/LockManager/request'),
      'idb-add': ('MDN: IDBObjectStore.add', 'https://developer.mozilla.org/en-US/docs/Web/API/IDBObjectStore/add'),
      'notifications': ('MDN: Notifications API', 'https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API'),
      'push': ('MDN: Push API', 'https://developer.mozilla.org/en-US/docs/Web/API/Push_API'),
      'iframe': ('MDN: iframe и sandbox', 'https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe'),
      'notification-tag': ('MDN: Notification.tag', 'https://developer.mozilla.org/en-US/docs/Web/API/Notification/tag'),
      'yield': ('MDN: scheduler.yield', 'https://developer.mozilla.org/en-US/docs/Web/API/Scheduler/yield'),
      'ios-push': ('WebKit: Web Push on iOS', 'https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/'),
    })
    t('communication','worker-alternatives','Альтернативы Workers: какую задачу решаем',
      'Сначала раздели вычисления, React-render, межвкладочное соединение и работу при закрытой странице. У этих задач разные альтернативы.',[
      ('Backend','ZIP, PDF или конвертацию можно вынести на сервер: меньше CPU на устройстве, но нужны сеть, передача данных и серверные ресурсы.'),
      ('Разбиение вычислений','Делить цикл на небольшие части и уступать main thread через scheduler.yield с проверкой поддержки или setTimeout. Общая работа остаётся в UI-потоке.'),
      ('Нативные API','createImageBitmap, OffscreenCanvas и асинхронные методы могут помочь конкретной операции. async в названии не гарантирует отсутствие всей работы на main thread.'),
      ('React concurrency','useTransition и useDeferredValue управляют приоритетами React-render. Произвольный синхронный ZIP-код они не переносят в другой поток.'),
      ('Общая связь вкладок','Web Locks выбирает вкладку-лидера, BroadcastChannel передаёт сообщения. Это альтернатива SharedWorker для подходящих контекстов, а не фоновый сервер.'),
      ('Частичная замена Service Worker','HTTP-кэш ускоряет загрузку онлайн; IndexedDB хранит данные, но не гарантирует загрузку app shell offline. Web Push требует Service Worker.')],
      'Для ZIP, тяжёлого React-списка и одного SSE на несколько вкладок выбери разные решения и объясни ограничения.',
      'workers shared-worker locks bc yield sw',kind='scenario',drill=True,notion=True,
      note='Уточнение к Notion: обещание «около 20 строк» не учитывает reconnect, восстановление данных, завершение и ошибки. Поддержку API проверять для целевых браузеров.')
    ex('worker-alternatives','Перед выбором worker спроси: интерфейс тормозит из-за вычислений, рендера или лишних соединений? Promise и async/await сами по себе не переносят вычисление в другой поток.',
      ['Для тяжёлого ZIP сравни backend и Dedicated Worker. Первый требует сервера, второй сохраняет обработку в браузере, но добавляет передачу данных.',
       'Если нужны короткие вычисления на main thread, разбей их на порции. Между порциями браузер сможет обработать ввод; длительность всей задачи не обязана уменьшиться.',
       'Если дорог именно React-render, изучи state, виртуализацию и приоритеты обновлений. Эти инструменты не ускоряют сторонний синхронный алгоритм.',
       'Для общей SSE-связи используй координатора: SharedWorker либо лидера с Web Locks и BroadcastChannel. Для событий при закрытой странице нужен другой жизненный цикл.'],
      'Возможный пример из приложения: ZIP создаётся на сервере или в worker; фильтрация списка откладывается transition; вкладки делят SSE через лидера. Это три разных решения трёх разных проблем.',
      'ZIP: backend или Dedicated Worker. Тяжёлый список: сначала измерение React-render, затем организация state и подходящая оптимизация. Общий SSE: координатор вкладок. Выбор зависит от места выполнения и жизненного цикла, а не от слова async.',
      code='for (let i = 0; i < items.length; i += 100) {\n  processBatch(items.slice(i, i + 100));\n  if (globalThis.scheduler?.yield) await scheduler.yield();\n  else await new Promise(resolve => setTimeout(resolve, 0));\n}',
      walkthrough=['processBatch — условная функция приложения; каждая порция тоже должна быть короткой.','yield отдаёт управление браузеру; await Promise.resolve() этого не заменяет, потому что добавляет microtask.','Уступка потока улучшает отзывчивость, но не создаёт параллельное вычисление.'])
    t('communication','web-locks','Web Locks: критическая секция и вкладка-лидер',
      'Именованная блокировка согласует работу участников одного origin в общей области хранения. Все участники должны добровольно соблюдать один протокол.',[
      ('Время удержания','Lock удерживается до завершения callback или возвращённого им Promise. Длительная async-операция должна быть await внутри callback.'),
      ('Очередь и режимы','exclusive допускает одного владельца; shared допускает нескольких читателей. Очередь ожидающих не является гарантией своевременной работы фоновой вкладки.'),
      ('ifAvailable','Без ожидания вызывает callback с lock или null. Получение null нужно обработать, оно не означает успешный захват.'),
      ('Отмена ожидания','signal отменяет ожидающий запрос. Уже выданный lock он сам не освобождает: callback должен закончиться через собственный сигнал завершения.'),
      ('Выбор лидера','Одна вкладка держит соединение внутри callback, остальные ждут. После освобождения lock другой участник может стать лидером.'),
      ('Ошибки и диагностика','Обрабатывать rejection request, освобождать ресурсы в finally; query показывает held/pending. steal — исключительный механизм, не откатывающий чужие побочные эффекты.')],
      'Объясни, как одна вкладка держит SSE, как сменится лидер и где нужны cleanup и восстановление событий.',
      'locks lock-request bc sse',kind='scenario',drill=True,notion=True,
      note='Уточнение к Notion: освобождение lock при закрытии вкладки не даёт бесшовный failover. Возможны пауза, потерянные события и throttling. Lock не делает действия ровно однократными.')
    ex('web-locks','Три вкладки не должны открывать три одинаковых SSE-соединения. Одна становится лидером, другие получают её сообщения. Lock координирует владение, BroadcastChannel — доставку внутри браузера.',
      ['Каждая вкладка запрашивает один exclusive lock с одинаковым именем. Только один callback начнёт работу.',
       'Лидер создаёт EventSource и обновляет свой UI сам; сообщения другим вкладкам пересылает в BroadcastChannel.',
       'Callback остаётся pending, пока соединение нужно. finally закрывает EventSource при контролируемом завершении.',
       'После закрытия лидера другой участник может получить lock. Он заново подключается и восстанавливает данные по серверному cursor или snapshot.'],
      'Код показывает протокол владения, но updateUI, формат событий и серверное восстановление принадлежат приложению. stop.abort отменяет ожидание; для владельца дополнительно предусмотрен собственный обработчик abort.',
      'Web Locks даёт одного владельца критической секции среди согласованных участников. Для общего SSE держу lock на время соединения, рассылаю события и отдельно проектирую восстановление. Закрытие вкладки освобождает lock, но не восстанавливает данные.',
      code=LEADER_CODE,walkthrough=['Имя sse-leader должно совпадать во всех вкладках.','Promise удерживает callback незавершённым; событие abort позволяет завершить его явно.','Для production нужны начальный snapshot, обработка auth, storage partition и механизм replay после смены лидера.'])
    t('communication','postmessage-safety','postMessage: доверие к отправителю и данным',
      'Сообщение от окна — внешний вход. Даже ожидаемый origin не доказывает, что данные имеют нужный формат и действие разрешено.',[
      ('targetOrigin','При отправке задавать точный origin получателя. Звёздочка может раскрыть сообщение после навигации окна на другой сайт.'),
      ('event.origin','Сравнивать со строгим allowlist полных origins. includes и startsWith не подходят для проверки доверенного домена.'),
      ('event.source','Проверять ссылку на ожидаемое окно, например iframe.contentWindow. Это различает несколько iframe одного origin.'),
      ('event.data','Проверять тип сообщения, поля и допустимые значения. Не вставлять произвольные данные в innerHTML, eval или URL перехода.'),
      ('Права на действие','Валидная форма сообщения не даёт разрешения на оплату или удаление. Проверять допустимость операции в протоколе и права на сервере.')],
      'Iframe прислал команду resize. Какие проверки нужны перед изменением высоты и почему одного origin недостаточно?',
      'post security iframe',kind='scenario',drill=True,notion=True)
    ex('postmessage-safety','В страницу встроен виджет другого origin. Он просит изменить размер iframe. Родитель должен разрешать только предусмотренную команду от конкретного виджета.',
      ['Сначала проверить event.origin точным сравнением, а затем event.source — относительно нужного iframe.',
       'Проверить, что data — объект известного типа сообщения. Ограничить числовые поля разумным диапазоном.',
       'Выполнить только разрешённое действие. Не интерпретировать вход как HTML или JavaScript.',
       'При ответе указать точный targetOrigin; навигация iframe не должна превратить его в получателя секрета.'],
      'В примере допустима только команда resize с высотой от 100 до 1200. Даже другое окно с тем же origin будет отклонено проверкой source.',
      'Проверяю origin, конкретное окно source, структуру и смысл data. Отправляю с точным targetOrigin. После этого выполняю только разрешённую команду; права на бизнес-операции всё равно проверяет сервер.',
      code=POST_CODE,walkthrough=['origin проверяет сайт отправителя, source — конкретное окно.','Number.isFinite отвергает строки, NaN и Infinity; диапазон ограничивает эффект команды.','Секреты не передаются через wildcard targetOrigin; пример работает с обычным origin iframe, не opaque sandbox.'])
    t('communication','storage-events','storage event: кому приходит изменение',
      'Событие уведомляет другие документы, разделяющие изменённую область storage. Документ, выполнивший запись, своего события не получает.',[
      ('localStorage','Другие вкладки и окна того же origin с общей областью хранения, включая подходящие same-origin iframe.'),
      ('sessionStorage','Другие same-origin документы внутри той же вкладки, обычно iframe. Другая вкладка имеет другую область sessionStorage.'),
      ('Изменение значения','setItem с прежним значением не создаёт изменение. Начальное состояние читать отдельно: storage event не является историей.'),
      ('Поля события','key, oldValue, newValue, storageArea и url. removeItem даёт newValue=null; clear даёт key=null.'),
      ('Синхронизация UI','Писатель обновляет свой UI сам. Получатели фильтруют key и перечитывают или применяют новое значение.')],
      'Вкладка A меняет тему. Назови получателей события среди A, вкладки B того же origin, iframe внутри A и другого сайта; затем замени localStorage на sessionStorage.',
      'storage-event storage bc',kind='scenario',drill=True,notion=True)
    ex('storage-events','Документ — отдельная загруженная страница: iframe тоже документ. Общая область хранения и документ-писатель — разные понятия.',
      ['A и B открыты на https://app.example, внутри A есть iframe этого origin. A меняет значение localStorage.',
       'B и iframe получают событие, A — нет. Другой origin его не получает. Внешние embedding-контексты могут иметь отдельную storage partition.',
       'При sessionStorage B исключается: область ограничена вкладкой A, но same-origin iframe внутри неё может получить событие.',
       'На старте прочитать getItem. При повторной записи того же значения нового события нет. Обновление UI писателя выполняется напрямую.'],
      'Для темы нужен снимок при загрузке и обработчик дальнейших изменений. Нельзя ждать первого storage event, чтобы узнать сохранённую тему.',
      'storage приходит другим документам с общей областью хранения. localStorage обычно связывает same-origin вкладки; sessionStorage — документы внутри одной вкладки. Писатель не получает событие, начальное состояние и свой UI обновляет отдельно.',
      code='const key = "theme";\napplyTheme(localStorage.getItem(key) || "light");\nwindow.addEventListener("storage", event => {\n  if (event.storageArea === localStorage && (event.key === key || event.key === null)) {\n    applyTheme(localStorage.getItem(key) || "light");\n  }\n});\nfunction changeTheme(theme) {\n  localStorage.setItem(key, theme);\n  applyTheme(theme); // писатель своего события не получает\n}',
      walkthrough=['applyTheme — функция интерфейса приложения.','key=null учитывает clear, который удаляет и тему.','Схема: A → localStorage → B и iframe; обратной стрелки события к A нет.'])
    t('communication','iframe-uses','Same-origin iframe: зачем и где граница изоляции',
      'Iframe создаёт отдельный документ со своим CSS и JavaScript-контекстом. Совпадение origin разрешает взаимодействие, но не создаёт независимую границу доверия.',[
      ('Виджеты и legacy','Встроить старую страницу или независимый редактор со своим CSS и глобальными переменными.'),
      ('Предпросмотр и печать','Рендерить шаблон или печатный layout без изменения основного документа.'),
      ('Same-origin доступ','Родитель может обращаться к contentWindow и DOM при отсутствии ограничений sandbox. Общий origin допускает общий storage, но JS-память каждого документа отдельная.'),
      ('sandbox','Без allow-same-origin документ получает opaque origin. Сочетание allow-scripts и allow-same-origin для недоверенного same-origin содержимого может разрушить изоляцию.'),
      ('Недоверенный HTML','Использовать отдельный origin, подходящий sandbox и узкий протокол postMessage. Изоляция CSS сама по себе не защищает от вредоносного JavaScript.')],
      'Выбери iframe для legacy-экрана и предпросмотра недоверенного HTML. Как изменятся origin, sandbox и способ общения?',
      'iframe post security',kind='scenario',drill=True,notion=True,
      note='Уточнение к Notion: скрытый iframe принадлежит конкретной странице и сам по себе не создаёт одно общее соединение для независимых вкладок.')
    ex('iframe-uses','В новом интерфейсе можно временно показывать legacy-экран в iframe. Его стили не смешиваются с родительскими, но доверие к коду определяется origin и sandbox.',
      ['Для доверенного legacy same-origin iframe позволяет интеграцию и отдельный жизненный цикл страницы.',
       'Для печати отдельный документ задаёт собственные размеры и стили; после загрузки вызывается его print.',
       'Для пользовательского HTML сначала нужна граница безопасности: отдельный origin и минимальные разрешения sandbox.',
       'Общение через postMessage требует проверки origin/source/data. Opaque origin sandbox требует отдельной модели протокола и доверия.'],
      'Trusted legacy и пользовательский HTML внешне могут выглядеть одинаково, но нельзя выдавать им одинаковые разрешения.',
      'Iframe полезен для отдельного документа: legacy, редактор, печать. Same-origin упрощает доступ, но не изолирует недоверенный код. Для него выбираю отдельный origin, минимальный sandbox и проверенный протокол сообщений.')
    t('communication','web-notifications','Notifications и Push: показ и доставка',
      'Toast находится внутри страницы. Notifications API показывает системное уведомление. Push API доставляет событие Service Worker, когда страница может быть закрыта.',[
      ('Разрешение','permission: default, granted или denied. Запрашивать по понятному действию пользователя в secure context. Отказ нельзя обходить повторным показом запроса.'),
      ('Показ уведомления','new Notification привязан к странице; для мобильных браузеров использовать persistent notification через registration.showNotification и проверять поддержку.'),
      ('Push','Нужны Service Worker, push subscription и серверная отправка. Подписка и право на показ — связанные, но разные части механизма.'),
      ('tag и оформление','body/icon/data описывают содержимое; tag группирует или заменяет подходящие уведомления. Поддержка actions, image и других опций различается.'),
      ('Клик и видимые клиенты','В Service Worker обработать notificationclick, закрыть уведомление и открыть или сфокусировать разрешённый URL. clients.matchAll помогает найти подходящие окна.')],
      'Сравни toast, системное уведомление открытой страницы и Push при закрытой странице. Опиши разрешение и обработку клика.',
      'notifications push notification-tag sw ios-push',kind='compare',drill=True,notion=True,
      note='Уточнение к Notion: tag заменяет уведомления по правилам API и не является гарантией «ровно один раз». На iOS Web Push связан с web app на Home Screen; поддержка и настройки ОС требуют отдельной проверки.')
    ex('web-notifications','Пользователь хочет получать уведомления о сообщениях. Отдельно решаем доставку события, разрешение и показ. Тренажёр изучает API, но сам не просит доступ и не подключает Push.',
      ['Кнопка «Включить уведомления» объясняет цель. После нажатия проверить API и запросить разрешение.',
       'Для события при открытой странице возможен обычный UI-toast. Системное уведомление требует разрешения.',
       'Для Web Push нужна серверная подписка и Service Worker. Он запускается на событие, а не работает постоянно.',
       'В обработчике клика закрыть notification, найти подходящий клиент или открыть известный разрешённый URL. Не доверять произвольному URL из внешних данных.'],
      'Учебный фрагмент: Service Worker уже зарегистрирован приложением; после разрешения показывается persistent notification. Это демонстрация API, не рабочая Push-подписка.',
      'Notifications отвечает за показ, Push — за доставку к Service Worker. Разрешение запрашиваю после действия пользователя; на мобильных ориентируюсь на showNotification. Для закрытой страницы нужны подписка и сервер, а tag не заменяет дедупликацию событий.',
      code='button.addEventListener("click", async () => {\n  if (!("Notification" in window) || !("serviceWorker" in navigator)) return;\n  const permission = await Notification.requestPermission();\n  if (permission !== "granted") return;\n  const registration = await navigator.serviceWorker.ready;\n  await registration.showNotification("Новое сообщение", {\n    body: "Откройте приложение", tag: "chat-42", data: { path: "/messages/42" }\n  });\n});',
      walkthrough=['ready ожидает активную регистрацию: без заранее зарегистрированного Service Worker пример не завершит ожидание.','tag выбирает группу показанных уведомлений; историю event ID хранить отдельно.','Обработчик notificationclick находится в файле Service Worker, а не в странице.'])

def revise_theory(byid, explanations):
    dedup = byid['dedup']
    dedup['sources'] = ['locks','lock-request','idb-add','bc','notification-tag']
    dedup['notion'] = True
    dedup['note'] = 'Уточнение к Notion: один лидер уменьшает число соединений, но не исключает повторную доставку после reconnect. tag заменяет уведомления и не обеспечивает exactly-once. TTL ограничивает окно дедупликации.'
    z = explanations['dedup']
    z.update(context='Три вкладки получили одно событие с ID n42. Каждая собирается показать toast. Если сначала спросить localStorage, а потом записать результат, две вкладки могут обе прочитать «ещё нет». Нужна атомарная координация решения, а не просто рассылка «я показал».',
      steps=['Назначить стабильный event ID на стороне источника. Повторная доставка того же события должна сохранять ID.',
       'Выбрать архитектуру: лидер с одним соединением или согласованная обработка в нескольких вкладках. Лидер всё равно должен учитывать replay после reconnect.',
       'Для Web Locks все участники защищают общую критическую секцию одинаковым lock, затем читают и записывают общую историю ID внутри callback. Без lock отдельные getItem/setItem дают гонку.',
       'Альтернатива: IndexedDB add с уникальным ключом event ID. Успех claim подтверждать завершением транзакции; существующий ключ означает дубль.',
       'Запись перед показом допускает пропуск при падении. Показ перед записью допускает повтор. Toast и запись истории не образуют общую транзакцию.',
       'Хранить историю ограниченное время и очищать старые ID. После TTL событие может снова считаться новым. Для нескольких устройств и бизнес-эффектов нужна серверная идемпотентность.'],
      example='Учебный вариант выбирает claim перед показом и TTL 24 часа. Это политика «лучше пропустить при сбое, чем показать повторно» в пределах общей истории; ошибки storage нельзя выдавать за успешную обработку.',
      code=LOCK_CODE,
      walkthrough=['Lock общий для истории; в примере все операции с ней идут последовательно.','Запись expires происходит до showToast: другая вкладка после получения lock увидит claim.','Необработанный отказ localStorage или locks должен попасть в обработчик ошибки вызывающего кода. Нельзя молча считать событие показанным.','TTL в примере проверяет свежесть отметки, но физическую очистку старых ключей нужно выполнять отдельно под тем же lock.'],
      takeaway='Для одного показа нужны стабильный event ID, общая история и атомарный claim. Web Locks защищает проверку с записью, IndexedDB add даёт уникальный claim. Отдельно выбираю риск пропуска или повтора при падении; лидер, BroadcastChannel и notification tag сами по себе exactly-once не дают.')
    byid['workers']['sources'] += ['shared-worker']
    byid['workers']['note'] = 'Уточнение к Notion: Service Worker запускается браузером на события и может завершаться между ними. Поддержку SharedWorker и конкретных worker API проверять по compatibility table, а не по старым спискам браузеров.'
    w=explanations['workers']
    w['example']='Возможные применения: Dedicated Worker обрабатывает изображение или ZIP без блокировки UI; SharedWorker централизует SSE для подходящих вкладок; Service Worker принимает Push. Это предложения, а не утверждение о выполненной работе.'
    w['code']='// Страница\nconst worker = new Worker("compute.js");\nworker.onmessage = ({ data }) => renderResult(data);\nworker.postMessage([1, 2, 3]);\n// compute.js\nself.onmessage = ({ data }) => {\n  self.postMessage(data.reduce((sum, n) => sum + n, 0));\n};\n// После работы: worker.terminate();'
    w['walkthrough']=['У страницы и worker разные JS-контексты.','Данные передаются structured clone, а не общей ссылкой на массив.','Worker возвращает результат; DOM обновляет renderResult на странице.']
    w['examples']=[
      example('SharedWorker: подключение страницы к общему worker. Сценарий учебный; обработку ошибок и выбор поддерживаемой платформы добавляет приложение.',
       '// Страница\nconst shared = new SharedWorker("shared.js");\nshared.port.onmessage = ({ data }) => renderResult(data);\nshared.port.postMessage({ type: "hello" });\n// shared.js\nself.onconnect = ({ ports: [port] }) => {\n  port.onmessage = ({ data }) => port.postMessage({ received: data.type });\n};',
       ['У SharedWorker сообщения идут через MessagePort. Назначение onmessage запускает этот port.','Подходящие вкладки с одинаковым URL worker и параметрами подключаются к одному экземпляру; состояние не является постоянным storage.']),
      example('Service Worker: страница регистрирует обработчик, а браузер запускает его на событие. Push подписка и серверная отправка здесь не реализованы.',
       '// Страница, HTTPS или localhost\nawait navigator.serviceWorker.register("sw.js");\n// sw.js\nself.addEventListener("push", event => {\n  event.waitUntil(self.registration.showNotification("Новое событие", {\n    body: "Откройте приложение", tag: "activity"\n  }));\n});',
       ['register создаёт регистрацию, а не вечный процесс.','waitUntil связывает работу с событием, но не обещает неограниченного времени жизни.','В worker нет DOM и localStorage; нужное устойчивое состояние хранится отдельно.'])]
    z['examples']=[example('Атомарный claim через IndexedDB: store claims уже создан с уникальным ключом id. Ниже показан другой протокол координации, а не дополнительный обязательный шаг после Web Locks.',IDB_CODE,
                          ['Одинаковый event ID может быть вставлен только одним участником.','Успех подтверждается завершением transaction.','Очистка истории и сбои между commit и показом проектируются отдельно.'])]
    explanations['web-notifications']['examples']=[example('Обработчик клика находится в Service Worker. Пример открывает заранее известный маршрут; для фокусировки существующего окна можно добавить clients.matchAll.',
      'self.addEventListener("notificationclick", event => {\n  event.notification.close();\n  event.waitUntil(clients.openWindow("/messages"));\n});',
      ['Не передаём произвольный внешний URL из payload напрямую в openWindow.','event.waitUntil позволяет браузеру учитывать async-работу обработчика.'])]
    explanations['render-strategies']['takeaway']='Для личного кабинета часто подходит CSR: данные персональные, публичное индексирование обычно не нужно. Для редко меняющейся статьи SSG готовит HTML заранее. Каталог с допустимой задержкой обновления может использовать ISR с продуманной инвалидацией; для свежего ответа на каждый запрос подходит SSR ценой серверной работы. Hybrid сочетает подходы по маршрутам. HTML от сервера ещё нужно связать с клиентской интерактивностью через hydration.'
    for tid in ('cdn','statuses','api-styles','pagination','auth','cross-context','realtime','state-design','query-libs','react-performance','bundle','seo','scripts','images','svg','architecture-boundaries'):
        explanations[tid]['takeaway']=MAIN_LEADS[tid]
    explanations['web-storage']['takeaway']='Cookie подходит для автоматически передаваемого session ID с выбранной моделью защиты. localStorage — для небольших сохраняемых настроек, sessionStorage — для черновика конкретной вкладки. IndexedDB хранит структурированные offline-данные и Blob асинхронно, Cache API — пары Request/Response. У всех вариантов учитывать область, квоту и возможную недоступность; наличие записи не гарантирует вечное хранение.'
    explanations['hooks-list']['takeaway']='Начинаю с задачи: useState/useReducer хранят отображаемое состояние; useContext читает общий контекст; useRef сохраняет значение без render; useEffect синхронизирует внешнюю систему, useLayoutEffect измеряет layout до paint. useMemo/useCallback помогают оптимизации после измерений; transitions меняют приоритеты. Для остальных хуков ниже указан явный учебный набор с назначением каждого.'
    explanations['utilities']['takeaway']='Partial, Required и Readonly меняют модификаторы свойств; Pick и Omit выбирают ключи объекта; Record строит объект по набору ключей. Exclude и Extract фильтруют union, NonNullable исключает null/undefined. Parameters и ReturnType извлекают части типа функции, Awaited моделирует результат ожидания. Все они преобразуют типы, а не реальные значения.'
    explanations['arrays']['takeaway']='Для преобразования беру map/filter/flatMap, для свёртки reduce, для поиска find/findIndex, для проверки some/every/includes. push, splice, sort и другие изменяющие методы требуют осторожности с React-state. slice/concat и новые toSorted/toReversed/toSpliced/with возвращают новый массив, но вложенные ссылки могут оставаться общими. Для каждого метода называю результат и мутацию.'
    explanations['styling']['takeaway']='CSS Modules дают локальные class names и подходят для build-time CSS. CSS-in-JS удобен для динамики и тем, но SSR требует интеграции, а runtime-варианты добавляют работу в браузере. Обычный CSS прост в доставке, но требует дисциплины каскада и имён. Выбираю по динамике и SSR проекта; Sass преобразует CSS при сборке и не равен SaaS.'

# Answers correspond, in order, to the concrete FOLLOWUPS in build.py.
FOLLOWUP_ANSWERS = {
 'navigation': ('Свежий ответ в кэше может исключить сетевой запрос целиком. Если запрос нужен, переиспользование готового соединения убирает новое установление транспорта и TLS. Парсинг полученного HTML и отображение всё равно нужны.', 'HTTP/3 переносит HTTP поверх QUIC/UDP и использует TLS 1.3 в установлении QUIC. Потеря данных одного потока не задерживает доставку всех других как при общем TCP-потоке HTTP/2; DNS и rendering pipeline от этого не исчезают.'),
 'pipeline': ('Reflow обычно означает повторный layout: пересчёт размеров и координат. Repaint меняет изображение без обязательного изменения геометрии, например при смене цвета. Изменение размеров часто требует обоих этапов.', 'left может менять геометрию layout. transform может перемещать уже подготовленный слой на compositing-стадии. Это зависит от браузера и структуры страницы: отдельный слой не бесплатен и не гарантирован.'),
 'cdn': ('Для персональных ответов использовать корректные Cache-Control, например private для запрета общего кэша или no-store для запрета хранения. Не считать наличие токена или CDN автоматической защитой. Проверить конфигурацию cache key и правила CDN.', 'Узел не находит подходящий свежий ответ и обращается к origin либо следующему уровню кэша. Затем может сохранить ответ, если правила разрешают. Первый запрос поэтому не обязательно ускорится.'),
 'message': ('HTTPS шифрует путь и query в транспортном обмене, но URL остаётся доступен браузеру и серверу: история, логи, аналитика и иногда Referer по действующей политике. Секреты в URL помещать не стоит.', 'Смысл метода, статуса, заголовков и тела сохраняется, но HTTP/2 передаёт бинарные frames в streams, использует pseudo-headers и HPACK. Это не текстовая start-line HTTP/1.1 на проводе.'),
 'methods': ('Идемпотентность касается итогового эффекта на ресурс, а не одинакового статуса. После первого удаления ресурс отсутствует; второй запрос может сообщить 404, не изменяя этот результат.', 'Клиент передаёт стабильный idempotency key для одной логической операции. Сервер атомарно хранит результат и возвращает его при повторе с тем же ключом, проверяя соответствие payload. Одна клиентская блокировка этого не обеспечивает.'),
 'caching': ('no-cache разрешает хранить ответ, но перед повторным использованием требует валидацию. no-store запрещает хранение этого ответа. Например, ETag полезен с no-cache, а конфиденциальный ответ может требовать no-store.', 'Клиент отправляет If-None-Match с сохранённым ETag. Если представление подходит, сервер возвращает 304 без нового тела, и клиент использует сохранённое тело с обновлёнными метаданными.'),
 'rest': ('JSON — формат представления, HTTP — протокол. REST дополнительно задаёт client-server, stateless, cacheability, uniform interface, layered system и необязательный code-on-demand. RPC-вызовы с JSON не становятся REST автоматически.', 'Каждый запрос содержит необходимые данные для проверки и выполнения, включая credentials. Сервер может хранить пользователей и бизнес-данные; нельзя требовать неявный контекст предыдущего шага общения для понимания текущего запроса.'),
 'api-styles': ('Браузерный fetch не предоставляет полный транспортный интерфейс native gRPC, в частности требуемое управление HTTP/2 и trailers. Используют gRPC-Web и совместимый proxy либо другой gateway; возможности streaming зависят от реализации.', 'На сервере ограничивают depth и cost, пагинируют списки, проверяют права, устанавливают timeout и rate limits. Persisted queries и batching загрузчиков помогают, но клиентский выбор полей сам по себе не предотвращает дорогие запросы.'),
 'pagination': ('Позиции записей сместятся. Следующая страница по прежнему offset может повторить уже показанную запись или пропустить другую при удалениях. Для динамической ленты cursor обычно устойчивее.', 'Если несколько записей имеют одинаковую дату, одной даты недостаточно для однозначной границы. Пара createdAt + id задаёт стабильный порядок и позволяет строить условие следующей порции без неопределённых равенств.'),
 'tls': ('Проверяется доверенная цепочка, соответствие имени сайта, срок действия и допустимость сертификата по политике браузера. TLS-handshake подтверждает владение соответствующим ключом. Наличие сертификата не доказывает честность самого сайта.', 'TLS не исправляет XSS, CSRF, неверные права на ресурс или утечку через логи. Он защищает транспорт между сторонами соединения, а приложение всё равно обязано проверять вход и авторизацию.'),
 'cors': ('Для запроса с preflight браузер сначала отправляет OPTIONS. Основной запрос пойдёт только при разрешённых origin, методе и заголовках. Простой запрос может уйти без preflight, даже если чтение ответа затем будет запрещено.', 'CORS в основном ограничивает чтение cross-origin ответа скриптом. CSRF может выполнить действие запросом, чей ответ атакующему читать не нужно. Нужны отдельные меры: SameSite, CSRF-token и проверка origin по ситуации.'),
 'cookies': ('HttpOnly закрывает cookie для document.cookie, но браузер продолжает отправлять её с подходящими запросами. Secure ограничивает отправку защищённым соединением. Ни один атрибут сам по себе не заменяет CSRF-защиту.', 'Современные браузеры требуют Secure для SameSite=None: cookie разрешена в cross-site контексте, но должна передаваться по HTTPS. При этом отдельная политика блокировки third-party cookies всё равно может помешать.'),
 'web-storage': ('HTTP-кэш управляется HTTP-семантикой и заголовками. Cache API — программное хранилище Request/Response: приложение само выбирает записи и их обновление. Сохранение ответа в Cache API само не устанавливает стратегию его актуальности.', 'localStorage разделяется подходящими документами одного origin и сохраняется между сессиями до удаления. sessionStorage ограничен origin и конкретной вкладкой; её same-origin iframe могут разделять область, другие вкладки — нет.'),
 'auth': ('В API перед выполнением операции: сервер проверяет пользователя, действие и конкретный ресурс. Скрытая кнопка и route guard нужны для UX, но запрос можно отправить напрямую.', 'JWT — формат подписанного токена, а не безопасное место хранения. XSS может прочитать доступный JS токен; cookie требует атрибутов и CSRF-модели. Важны срок жизни, проверка подписи, аудитории, отзыв и обновление.'),
 'workers': ('Браузер может завершить Service Worker между событиями. Глобальные переменные исчезают, поэтому важное состояние хранят в устойчивом storage, а обработчики регистрируют при запуске. Бесконечный таймер не превращает его в daemon.', 'Страница отправляет данные через postMessage, worker вычисляет результат и отправляет ответ. На странице onmessage обновляет DOM. Данные обычно клонируются structured clone; transferable позволяет передать владение подходящим буфером.'),
 'broadcast': ('Читает сохранённый snapshot из подходящего storage или API либо запрашивает состояние у уже открытого участника по протоколу request/reply. У BroadcastChannel нет replay; сообщения до подключения новой вкладке не доставляются.', 'Совпадения origin недостаточно: встраивание b.com в a.com может иметь другую partition, чем отдельная вкладка b.com. Для связи с конкретным iframe нужен явно спроектированный postMessage-протокол с проверками доверия.'),
 'cross-context': ('Проверить точный event.origin, event.source === iframe.contentWindow, тип и поля event.data, затем допустимость действия. При отправке указать точный targetOrigin. Доверенный origin не заменяет проверку сообщения.', 'Писатель не получает своё событие. localStorage уведомляет другие документы с общей областью, включая подходящие same-origin вкладки и iframe. sessionStorage — только same-origin документы внутри той же вкладки. При старте нужен getItem.'),
 'dedup': ('Между чтением и записью другая вкладка может прочитать то же отсутствие ключа. В результате обе решат, что событие новое. Нужна общая критическая секция для всей проверки с записью либо уникальный атомарный claim.', 'История не содержит ID, поэтому следующая доставка может показать уведомление повторно. Если сначала записать ID, сбой до показа приведёт к пропуску. Показ toast и commit storage не являются одной транзакцией; это явный выбор политики.'),
 'realtime': ('Нужен серверный протокол replay: стабильные ID, сохранённый cursor и история. EventSource отправляет Last-Event-ID при подходящем reconnect; сервер должен уметь продолжить. Если история недоступна, получить snapshot и согласовать новые события.', 'Для прогресса задачи или ленты обновлений, где сообщения идут сервер → клиент. EventSource даёт текстовый поток и автоматическое переподключение; исходящие команды можно отправлять HTTP-запросами. Двустороннему чату может лучше подойти WebSocket.'),
 'map-set': ('Два литерала {} — разные ссылки, поэтому Set сохранит оба. Если добавить один и тот же объект дважды, запись будет одна. Равенство полей автоматически не проверяется.', 'Итерация хранит порядок добавления, но Set не определяет get(index) или числовые свойства элементов. Третий элемент можно получить через [...set][2], явно создав массив; это требует обхода и дополнительной памяти.'),
 'weak': ('Сборка мусора может удалять недостижимые слабые ключи в недетерминированный момент. Перебор и size сделали бы это наблюдаемой характеристикой. Доступ возможен через известный живой ключ.', 'Достижимый Map сильно удерживает ключи и значения. Если больше нигде объект не нужен, запись в таком Map всё ещё делает его достижимым. Нужны delete, ограничение кэша или подходящая слабая коллекция.'),
 'gc': ('Если из roots нет пути к объектам цикла, сам цикл не мешает tracing GC собрать их. Важна достижимость, а не число взаимных ссылок.', 'В DevTools сравнить heap snapshots до и после повторения сценария и cleanup. Найти retaining path к объекту: listener на живом window может через замыкание удерживать закрытый экран. Удалить подписку и повторить измерение.'),
 'proxy': ('Операция на исходном target не проходит через traps Proxy. Если наружу доступны обе ссылки, часть обращений может обойти наблюдение.', 'get перехватывает чтение свойства верхнего proxy. Если вернуть обычный вложенный объект, его поля остаются обычными. Для глубокой модели нужны дополнительные Proxy, кэш идентичности и аккуратная обработка встроенных типов.'),
 'cloning': ('Date обычно сериализуется в строку. Свойство объекта со значением function опускается, а такой элемент массива становится null. JSON round trip не является универсальным копированием произвольного JS-объекта.', 'Поддерживаются определённые structured-clone типы, включая Date и циклы, но функции и DOM nodes нельзя клонировать. Не сохраняются произвольные прототипы пользовательских классов и дескрипторы так, как при полном дублировании объекта.'),
 'closures': ('Замыкание сохраняет доступ к переменной лексического окружения. Если она меняется, функция читает актуальное значение этого binding. В React каждый render создаёт своё окружение, поэтому callback прежнего render может видеть старые значения.', 'call вызывает функцию сейчас с заданным this и аргументами. bind возвращает новую функцию с зафиксированным this и, возможно, начальными аргументами; выполнение произойдёт при её последующем вызове.'),
 'promise-basics': ('Executor вызывается синхронно во время new Promise. Обработчики then и продолжение await выполняются позже через microtasks. Поэтому синхронный код executor может заблокировать UI.', 'throw в обработчике отклоняет Promise, возвращённый этим then. Ближайший downstream catch или rejection-handler может обработать ошибку. Возвращённое из обработчика значение, наоборот, определяет успешный результат цепочки.'),
 'promise-combinators': ('all([]) fulfilled со значением []; allSettled([]) fulfilled с []; any([]) rejected с AggregateError; race([]) остаётся pending. Даже для уже settled Promise callback then не запускается в текущем стеке.', 'race выбирает первое settlement результата, но не управляет исходными операциями. Для отмены fetch нужен AbortController и переданный signal. Таймаут в race без abort оставляет запрос работающим.'),
 'event-loop': ('Добавляется в конец очереди microtasks. Во время checkpoint очередь продолжают опустошать, включая новые microtasks, прежде чем перейти к следующей task.', 'Цепочка microtasks может долго не отдавать управление браузеру для rendering opportunity и ввода. Promise.resolve в цикле не равен уступке новой task; для длительной работы нужны порции, yield или worker.'),
 'timers': ('Задержка — минимальный срок до возможности поставить callback на выполнение. Текущий стек, microtasks, другие задачи, throttling и ограничения вложенных таймеров могут увеличить ожидание.', 'cleanup вызывает clearInterval при изменении зависимостей или unmount. setCount(c => c + 1) вычисляет новое значение из актуального предыдущего state и не читает устаревший count из замыкания.'),
 'fetch-streams': ('Границы сетевых chunks не совпадают с границами сообщений: JSON может быть разрезан посередине, а chunk может содержать несколько записей. Нужен формат framing, например NDJSON, и буфер неполного фрагмента.', 'Передать signal AbortController в fetch и корректно обработать AbortError. Для UTF-8 использовать TextDecoderStream либо decode с stream:true между chunks и финальный flush: символ может занимать байты в разных chunks.'),
 'render-commit': ('Render рассчитывает описание следующего UI. Если итоговые host-узлы и свойства не изменились, commit не обязан менять DOM. Сам факт вызова компонента не равен DOM-мутации.', 'React может повторить или отбросить render. Запрос, запись или подписка внутри него могут случиться лишний раз без соответствующего commit. Внешнюю синхронизацию размещают в effect с cleanup, действия пользователя — в handlers.'),
 'keys-vdom': ('React сопоставляет элементы среди соседей с учётом key и типа. Стабильный ID помогает сохранить локальный state за той же записью при перестановке, а не за её прежней позицией.', 'Каждый элемент выглядит новым: прежние компоненты размонтируются, новые монтируются. Теряются локальные state и фокус, повторяется setup эффектов и растёт работа.'),
 'fiber': ('React может приостановить расчёт менее срочного transition-render и обработать urgent update, например ввод. Затем продолжить или пересчитать transition с актуальными данными; чистота render позволяет такой повтор.', 'Concurrent rendering — планирование и прерываемый расчёт React-работы. Это не запуск компонентов в нескольких JS-потоках. Длинный синхронный вызов внутри компонента всё ещё блокирует поток до возврата.'),
 'effect-deps': ('При очередном render React сравнит obj по Object.is; ссылка та же, поэтому эта зависимость не изменилась и эффекта из-за мутации не будет. Без нового render проверка зависимостей вообще не запускается.', '[] означает отсутствие реактивных зависимостей у данного эффекта, а не глобальную однократность. Новый mount запускает setup снова; в Strict Mode development React дополнительно проверяет цикл setup → cleanup → setup.'),
 'effects-purpose': ('Для каждого setup перечислить ресурс и обратное действие: подписка → unsubscribe, таймер → clear, соединение → close. Development Strict Mode помогает обнаружить несбалансированный setup. Cleanup не должен случайно отменять новый независимый ресурс.', 'Фильтрацию списка и вычисление полной цены из props/state обычно вычисляют при render; при измеренной стоимости возможен useMemo. Effect нужен для внешней системы, а не для дублирования производного state.'),
 'effect-timing': ('Он выполняется перед paint и может блокировать отображение. Долгие измерения, синхронные вычисления и обновления state внутри него удлиняют путь до кадра. Использовать только для действительно нужной до paint синхронизации layout.', 'Для обычных несвязанных с взаимодействием обновлений React обычно даёт браузеру paint раньше эффекта. Но interaction updates и работа, вызванная layout effect, могут изменить момент выполнения. useEffect не является строгим API «после каждого paint».'),
 'context': ('memo сравнивает props, но компонент, читающий изменившийся context, получает его новое значение. Объект provider сравнивается по Object.is; memo не превращает useContext в selector по полю.', 'Отделить ввод формы от редко меняющихся theme/user и разделить contexts по назначению. Держать provider ближе к потребителям. Стабилизировать value имеет смысл для устранения лишних новых ссылок, но не для скрытия реального изменения.'),
 'state-design': ('Отфильтрованный список при известных items и query обычно вычисляется из них. Если хранить ещё и filteredItems, возникают два источника истины и риск рассинхронизации. Дорогую производную можно мемоизировать после измерения.', 'Обновление state начинает render от компонента-владельца. Если ввод расположен высоко, затрагивается большая ветка. Локальный state формы и правильная композиция уменьшают область работы; обновление общего context всё ещё может пересечь эту границу.'),
 'flux-redux': ('Reducer должен быть чистым: одинаковые state/action дают одинаковый результат без внешних эффектов. Запрос имеет время, ошибки и внешний мир; его размещают в middleware, thunk или query-слое и dispatch результата.', 'Dispatch проходит через цепочку middleware перед достижением reducer. Middleware может читать store, передавать action дальше через next, запускать async-работу и отправлять дополнительные actions. Reducer вычисляет следующий state синхронно.'),
 'forms': ('defaultValue задаёт начальное значение uncontrolled input, а дальнейший ввод хранит DOM. value задаёт текущее контролируемое значение; React должен обновлять его через state и onChange. Позднее изменение defaultValue не является управлением текущим вводом.', 'Использовать FormData(event.currentTarget) для именованных полей либо ref.current.value. Обработчик submit может выполнить preventDefault и затем валидацию; значение находится в DOM, поэтому отдельный state на каждый символ не обязателен.'),
 'suspense-lazy': ('Effect выполняется после commit, а обычный Promise fetch из него не сообщает Suspense о приостановке render. Нужен поддерживаемый Suspense data source или явные loading/error состояния.', 'Отклонённый import React.lazy передаёт ошибку ближайшей Error Boundary. Suspense показывает ожидание, а не error UI. Для retry важно учитывать поведение загрузчика и кэша модуля.'),
 'react-versions': ('Назвать реальные версии и выполненные задачи отдельно от изученных возможностей. Если миграции не было, прямо обозначить это и описать гипотетический план, не придумывая результат.', 'Проверить release/upgrade guides, peer dependencies и поддержку библиотек. Обновлять контролируемо, проверять effects/Strict Mode, типы, hydration и критические пользовательские сценарии. Сравнить метрики и предусмотреть откат.'),
 'never': ('После switch по discriminant остаточный вариант передают в assertNever(value: never). Если union расширили, но ветку не добавили, значение уже не never и TypeScript показывает ошибку в этой точке.', 'void описывает отсутствие используемого результата функции; выполнение может нормально закончиться. never обозначает невозможное значение: функция не возвращается нормально либо ветка недостижима.'),
 'assertions': ('В аннотированном a.green имеет string | [number, number, number], поэтому нужен narrowing перед toUpperCase. В b с satisfies green выводится как string, и строковый метод доступен. Контекст satisfies тоже может влиять на inference; это не правило «тип вообще никогда не меняется».', 'as const меняет статическое представление литералов и readonly-свойств. Runtime-объект остаётся изменяемым через другие доступные ссылки; для runtime-защиты нужен отдельный механизм вроде Object.freeze с учётом его поверхностности.'),
 'narrowing': ('typeof null возвращает "object". Поэтому проверка typeof value === "object" не исключает null; нужно дополнительно value !== null прежде чем читать поля.', 'Проверка if(value) отсекает 0, пустую строку, false, null, undefined и NaN. Если 0 и пустая строка допустимы, проверяй конкретно null/undefined либо нужный discriminant.'),
 'omit-exclude': ('Exclude сравнивает целые члены union с целевым типом. Объект {a: string, b: number} не является union своих ключей, поэтому Exclude<Obj, "a"> не удалит a. Для ключа нужен Omit<Obj, "a">.', 'Для naked type parameter T условный тип распределяется: каждый член union проверяется на совместимость с U. Совместимые превращаются в never, остальные сохраняются; never исчезает из объединения.'),
 'generics-variance': ('При Consumer<T> = (value: T) => void и strictFunctionTypes Consumer<Animal> можно использовать как Consumer<Dog>: он умеет принять любого Animal, включая Dog. Обратная подстановка опасна: обработчик Dog не обязан принимать Cat.', 'Для параметров методов TypeScript сохраняет бивариантное исключение в некоторых проверках совместимости. Function property проверяется контравариантно при strictFunctionTypes. Поэтому одинаковая на вид запись интерфейса может иметь разную безопасность подстановки.'),
 'react-performance': ('Повторить один сценарий на одинаковых данных и устройстве. React Profiler показывает стоимость commit/render; Performance panel — long tasks, layout и paint. Сравнить задержку взаимодействия и реальные затраты, а не только число render.', 'Собственный state компонента и прочитанный им context могут обновить его независимо от равных props. Новая ссылка на callback или объект тоже не равна прежней при обычном сравнении props.'),
 'vitals': ('CLS измеряет неожиданные сдвиги layout в учитываемых окнах сессии. Заданные размеры изображений и резерв места под динамические блоки помогают, если именно они вызывают сдвиги.', 'Лабораторная среда не представляет все устройства, сеть, длительные сессии и взаимодействия. Нужны полевые данные и распределение, обычно p75, а лаборатория помогает воспроизвести и диагностировать причину.'),
 'bundle': ('Network показывает transfer size и content size. Performance показывает parse, compile, evaluation и long tasks. Сжатие снижает передачу, но не обязано пропорционально уменьшить стоимость выполнения JS.', 'Главное LCP-изображение, критические стили и код текущего первого экрана обычно нельзя откладывать без оценки. Lazy полезен для не нужного сейчас; слишком мелкое дробление добавляет waterfall и служебные затраты.'),
 'render-strategies': ('Когда пользователю нужен свежий или персональный ответ, который нельзя безопасно и своевременно подготовить заранее. Можно использовать SSR или CSR для этой части, а публичную стабильную часть оставить статической. ISR допускает определённую задержку актуальности.', 'SSR отдаёт HTML для начального отображения. Клиент загружает нужный JS и гидратирует интерактивные части. Данные и первый клиентский render должны соответствовать серверному результату.'),
 'hydration': ('Math.random на сервере и клиенте может дать разные значения для первого render. React обнаружит несовпадение ожидаемого UI с HTML. Передать стабильное значение с сервера или отложить клиентскую часть до подходящего этапа.', 'SSR описывает получение HTML на сервере. Server Components описывают модель выполнения компонентов и передачи результата, включая отсутствие их кода в клиентском bundle. Клиентские компоненты также могут участвовать в серверном HTML, поэтому это не синонимы.'),
 'solid': ('Нарушение SRP: компонент одновременно показывает таблицу, управляет transport reconnect и формирует формат аналитики. Разделение UI, подписки и адаптера снижает число причин изменения одного модуля. Важно не дробление ради числа файлов, а границы ответственности.', 'Интерфейс для двух реально существующих способов оплаты может быть оправдан. Универсальная plugin-система для предполагаемых будущих способов без требований добавляет цену и нарушает YAGNI. Сначала назвать текущий сценарий изменения.'),
 'design-patterns': ('Опиши только реальный случай: задача → выбранный паттерн → альтернативы → твой вклад → проверенный результат. Если такого случая не было, назови это учебным примером и объясни механизм без вымышленной истории.', 'Назвать дополнительные интерфейсы, абстракции и сложность отладки. Затем сравнить с прямой функцией или явным условием для текущего масштаба. Польза должна выражаться в конкретной заменяемости или уменьшении связанных изменений.'),
 'module-federation': ('Согласовать версии и shared/singleton-политику, особенно для React. Проверять контракт host/remote и совместимость при сборке и загрузке. singleton не гарантирует магическое согласование несовместимых API.', 'Изолировать загрузку remote через Error Boundary, timeout на уровне загрузчика и fallback UI; сохранить навигацию host. Проверять отдельно недоступность сети, ошибку модуля и несовместимость контракта. При необходимости отключать проблемный remote конфигурацией.'),
}

EXTRA_FOLLOWUPS = {
 'web-locks': [
  ('Почему abort signal не остановил код владельца?', 'Signal в options request отменяет ожидание выдачи, но уже запущенный callback должен сам завершить работу. В примере он слушает тот же signal, закрывает EventSource в finally и возвращается.'),
  ('Как восстановить события после смены лидера?', 'Получить устойчивый cursor и запросить replay у сервера либо новый snapshot. BroadcastChannel не хранит историю; автоматическое получение lock не восстанавливает пропущенные данные.')],
 'worker-alternatives': [
  ('Почему await Promise.resolve() внутри ZIP-цикла не спасает отзывчивость?', 'Продолжения попадают в microtasks, которые опустошаются до следующей task и rendering opportunity. Нужна реальная уступка потока, worker или перенос вычислений на сервер.'),
  ('Что потеряем, заменив Service Worker на IndexedDB?', 'Сохраним данные, но не получим перехват загрузки app shell и Web Push при закрытой странице. Хранилище не имеет жизненного цикла Service Worker.')],
 'postmessage-safety': [
  ('Зачем source, если origin уже проверен?', 'Два разных iframe могут иметь один origin. Проверка source привязывает сообщение к ожидаемому окну; затем всё равно требуется валидация data.'),
  ('Что меняется после навигации iframe?', 'Ссылка на окно может сохраняться, а документ и origin — измениться. Точный targetOrigin ограничивает доставку; входящие сообщения повторно проверяют на каждом событии.')],
 'storage-events': [
  ('Как получить тему сразу после открытия вкладки?', 'Синхронно прочитать localStorage.getItem и применить значение; затем подписаться на дальнейшие изменения с учётом порядка и возможной синхронизации. Сам storage event прошлое значение не воспроизводит.'),
  ('Почему запись темы не обновила UI в той же вкладке?', 'Писатель не получает свой storage event. После записи он должен вызвать обновление UI напрямую. Запись прежнего значения также не создаёт нового события для остальных.')],
 'iframe-uses': [
  ('Почему same-origin iframe не является безопасной песочницей?', 'Без ограничений sandbox его код может обращаться к родителю и общим ресурсам origin. Изоляция CSS и отдельных global objects не запрещает доступ к данным.'),
  ('Почему скрытый iframe не заменяет SharedWorker для всех вкладок?', 'Он принадлежит конкретной странице. Независимые вкладки не получают автоматически ссылку на одно общее окно; нужна отдельная координация и модель жизненного цикла.')],
 'web-notifications': [
  ('Почему tag не заменяет event ID?', 'tag относится к показанным уведомлениям и их замене по правилам API. Он не хранит бизнес-историю обработки, не атомарно координирует вкладки и не отменяет повторный звук приложения.'),
  ('Что делать после denied?', 'Не обходить отказ. Показать понятное состояние в интерфейсе и при необходимости объяснить, где пользователь сам может изменить настройку. Основные функции должны оставаться доступны без уведомлений.')],
}

MAIN_LEADS = {
 'cdn': 'Для статики с версионированными именами поставлю CDN ближе к пользователям и разрешу длительное кэширование. Сначала измерю задержку и cache hit rate. Персональные API-ответы нельзя класть в общий кэш без правильных правил разделения и доступа.',
 'statuses': '1xx — промежуточная информация, 2xx — успех, 3xx — перенаправление или работа с сохранённым представлением, 4xx — проблема запроса со стороны клиента, 5xx — ошибка сервера. 401 требует корректной аутентификации; 403 означает отказ в доступе; 404 — ресурс не найден; 500 — внутренняя ошибка; 503 — временная недоступность. Интерфейс выбирает действие по конкретному коду и контракту API.',
 'api-styles': 'REST описывает архитектурные ограничения работы с ресурсами; SOAP задаёт XML-сообщения и протокол; GraphQL позволяет клиенту выбрать поля по схеме; gRPC задаёт RPC-контракт, часто через Protobuf. Для браузера у gRPC нужен подходящий gateway/gRPC-Web. Выбор зависит от клиентов, контракта и транспорта, а не от формата JSON против XML.',
 'pagination': 'Для меняющейся бесконечной ленты выберу cursor по стабильному порядку, например createdAt + id. Следующая порция начинается после последнего элемента. Offset проще для страниц с номерами, но вставка перед текущей позицией может дать повторы. Cursor не гарантирует snapshot: это отдельное требование к API.',
 'auth': 'Проверка должна отказать на сервере до удаления: текущий пользователь должен иметь право удалить именно этот ресурс. Скрытая кнопка — только удобство интерфейса. Дополнительно нужны корректная аутентификация и защита выбранного способа передачи credentials.',
 'cross-context': 'Тему same-origin вкладок можно передавать через BroadcastChannel либо хранить в localStorage с обработкой storage event. Начальную тему прочитаю из storage. Результат cross-origin iframe получу через postMessage с точным targetOrigin и проверками origin, source и data.',
 'realtime': 'Для чата с частым двусторонним обменом рассмотрю WebSocket. Для серверного прогресса задачи подойдёт SSE: команды можно отправлять обычным HTTP. При ограничениях инфраструктуры long polling работает поверх повторяемых HTTP-запросов. Во всех вариантах отдельно нужны auth, ошибки, cursor и восстановление пропущенных событий.',
 'state-design': 'State строки поиска держу рядом с input и не поднимаю его выше необходимого. Список вычисляю из query и исходных items, не дублируя отфильтрованные данные в state. Если тяжёл именно render списка, измерю и рассмотрю виртуализацию, memo и deferred update; это разные меры против разных причин.',
 'query-libs': 'Для server state выбираю query-библиотеку с кэшем, повторными запросами и инвалидацией: RTK Query удобен в Redux-приложении, TanStack Query или SWR — при соответствующей модели проекта. Redux и MobX могут управлять сложным client state. Они не заменяют автоматически политику свежести серверных данных.',
 'react-performance': 'Сначала воспроизведу задержку и измерю React Profiler и Performance panel. Разделю стоимость фильтрации, render и DOM/layout. Затем выберу изменение по причине: локальный state, memo для стабильных props, виртуализация списка или worker для CPU-алгоритма. Повторю тот же сценарий и сравню длительность взаимодействия.',
 'bundle': 'Сравню состав production bundle анализатором, transfer size в Network и выполнение JS в Performance. Удалю лишние зависимости, проверю tree shaking, разделю код по действительно отложенным маршрутам, настрою сжатие и кэширование версионированных файлов. React.memo не уменьшает размер скачиваемого bundle.',
 'seo': 'Проверю доступность URL, статусы и redirects, robots/noindex, canonical, ссылки и sitemap. Затем сравню исходный HTML и результат выполнения JS, проверю основное содержимое, title и структурированные данные. Стратегию SSR/SSG меняю, если проблема действительно в доставке или обработке контента, а не в запрете индексации.',
 'scripts': 'Независимой аналитике подойдёт async: она выполнится по готовности. Для двух зависимых classic scripts подходит defer с правильным порядком в документе: загрузка параллельная, выполнение после parsing в порядке документа. type=module имеет отдельный граф импортов и по умолчанию отложенное выполнение.',
 'images': 'Для медленного главного фото проверю запрос, размер, формат и приоритет; LCP-изображение не загружаю lazy без причины. Для CLS заранее задам width/height или aspect-ratio. srcset/sizes помогут передать подходящий размер; CSS-уменьшение уже скачанного большого файла сеть не ускоряет.',
 'svg': 'Логотип обычно выгодно хранить в SVG: он масштабируется и описывается небольшим набором фигур. Фото — raster вроде AVIF/WebP/JPEG. Для сложной карты сравню число элементов и интерактивность: огромный SVG DOM может быть дорогим; canvas или raster tiles могут подойти лучше. Недоверенный inline SVG требует безопасной обработки.',
 'architecture-boundaries': 'Для поиска сначала уточню объём данных, задержку, фильтры, URL-состояние и доступность. Разделю поле ввода, модель запроса, API-адаптер, результаты и навигацию. Отменю устаревший запрос или проигнорирую его результат, предусмотрю loading/error/empty и измерю задержку. SSR или client search выбираются по требованиям, а не заранее.',
}

ITEM_EXAMPLES = {
 'useState': 'Счётчик: const [count, setCount] = useState(0); обновление setCount(c => c + 1). State вызывает render, обычная переменная — нет.',
 'useReducer': 'Корзина: dispatch({type: "add", item}); reducer чисто вычисляет следующий state. Запрос оплаты выполняется за пределами reducer.',
 'useContext': 'Компонент читает useContext(ThemeContext); изменение value provider обновляет читателя даже при memo и прежних props.',
 'useRef': 'const inputRef = useRef(null); ref хранит DOM-ссылку. Изменение ref.current не вызывает render; это не замена отображаемого state.',
 'useEffect': 'useEffect(() => { const id = setInterval(tick, 1000); return () => clearInterval(id); }, [tick]); cleanup уравновешивает setup.',
 'useLayoutEffect': 'После изменения DOM измерить tooltip через getBoundingClientRect и обновить позицию до paint. Тяжёлая работа внутри задержит кадр.',
 'useMemo': 'const visible = useMemo(() => filter(items, query), [items, query]); кэш вычисления полезен при измеренной стоимости и стабильных зависимостях.',
 'useCallback': 'const onSelect = useCallback(id => setSelected(id), []); стабильная ссылка может помочь memo-ребёнку. Само выполнение функции не кэшируется.',
 'useTransition': 'Срочно обновить ввод, а тяжёлое изменение списка пометить startTransition. Уже начатый длинный синхронный алгоритм это не прервёт.',
 'useDeferredValue': 'const deferredQuery = useDeferredValue(query); дорогой список может отставать от актуального input. Это не фиксированный debounce и не автоматическое ограничение запросов.',
 'useId': 'const id = useId(); связать label htmlFor и input id. Это идентификатор доступности, а key списка должен происходить из данных.',
 'useImperativeHandle': 'Открыть родителю узкий handle {focus()} вместо всего DOM-узла. Вызывать useImperativeHandle на верхнем уровне компонента.',
 'useSyncExternalStore': 'Передать subscribe и getSnapshot для внешнего store; для SSR предусмотреть getServerSnapshot. Snapshot должен стабильно отражать изменения.',
 'useDebugValue': 'В custom hook useOnlineStatus вызвать useDebugValue(online ? "Online" : "Offline"); метка помогает React DevTools, но не меняет UI.',
 'useInsertionEffect': 'Библиотека CSS-in-JS вставляет правила до layout effects. Для обычного fetch или измерений компонентов этот хук не предназначен.',
 'useActionState': 'Форма получает state и pending результата Action: const [state, action, pending] = useActionState(save, initial). Валидация и серверные права остаются отдельными.',
 'useOptimistic': 'Пока сохранение ожидается, показать предварительно добавленный комментарий; после ошибки согласовать UI с подтверждённым state. Это не подтверждение серверного успеха.',
 'useEffectEvent': 'Обработчик события эффекта читает актуальные props/state без переподключения подписки. Не использовать его как способ скрыть настоящую реактивную зависимость.',
 'Partial<T>': 'type Patch = Partial<{name: string; age: number}>; допустим {name: "Аня"}. Вложенные объекты автоматически partial не становятся.',
 'Required<T>': 'type Full = Required<{name?: string}>; свойство name теперь обязательно. Реальный объект runtime не дополняется.',
 'Readonly<T>': 'Readonly<{count: number}> запрещает присваивание count через этот тип. Это поверхностная статическая защита, не Object.freeze.',
 'Pick<T, K>': 'Pick<{id: string; name: string}, "id"> даёт {id: string}. Runtime-объект с лишними полями сам не преобразуется.',
 'Omit<T, K>': 'Omit<{id: string; name: string}, "id"> даёт {name: string}. Для удаления поля из значения нужен отдельный runtime-код.',
 'Record<K, V>': 'Record<"ru" | "en", string> требует строковые значения для ru и en. Это не отдельная Map в runtime.',
 'Exclude<T, U>': 'Exclude<"a" | "b", "a"> даёт "b". Проверяются члены union, не свойства объекта.',
 'Extract<T, U>': 'Extract<string | number | boolean, string | number> даёт string | number: сохраняются совместимые члены union.',
 'NonNullable<T>': 'NonNullable<string | null | undefined> даёт string. 0, false и пустая строка не исключаются.',
 'Parameters<F>': 'Parameters<(id: string, retry: number) => void> даёт [id: string, retry: number], tuple параметров.',
 'ReturnType<F>': 'ReturnType<() => Promise<number>> даёт Promise<number>. Для результата ожидания дополнительно нужен Awaited.',
 'Awaited<T>': 'Awaited<Promise<Promise<number>>> моделирует рекурсивное ожидание и даёт number. Никакой Promise в runtime этот тип не запускает.',
 'Promise.all': 'Для независимых обязательных данных: Promise.all([loadUser(), loadOrders()]). При одном rejection общий результат отклоняется; порядок массива соответствует входу.',
 'Promise.allSettled': 'Для независимых результатов массовой операции: allSettled возвращает status и value/reason каждого элемента после завершения всех.',
 'Promise.any': 'Несколько зеркал: нужен первый успешный результат. Если все отклонены, итог — AggregateError; отклонение одного не завершает any.',
 'Promise.race': 'Запрос и таймер: результат определяется первым fulfilled или rejected. Проигравшая операция продолжает работу без отдельного abort.',
 'S — Single Responsibility': 'UI таблицы и адаптер аналитики имеют разные причины изменения. Выделить адаптер, сохранив ясный контракт; не превращать каждую строку в отдельный модуль.',
 'O — Open/Closed': 'Новый способ форматирования добавить как стратегию через существующий контракт, если такой сценарий расширения реален. Не строить plugin-систему заранее.',
 'L — Liskov Substitution': 'Реализация read-only хранилища не должна подменять writable store и внезапно бросать ошибку в save. Контракт включает поведение, а не только одинаковые имена методов.',
 'I — Interface Segregation': 'Компоненту просмотра передать read-интерфейс, а не большой объект с delete, edit и export. Потребитель зависит только от нужных операций.',
 'D — Dependency Inversion': 'Модель поиска зависит от searchApi(query), а конкретный HTTP-клиент подключается адаптером. Проверить модель можно с тестовым адаптером.',
}

# Narrow chat prompts get narrow answers instead of a shared topic dump.
CHAT_ANSWERS = {
 'chat-2-1': 'Назови реальные версии React, проекты и задачи, с которыми работала. Отдельно обозначь, что только изучала. Не нужно заявлять опыт с новой версией лишь потому, что прочитала документацию.',
 'chat-2-2': 'Если была миграция: исходная и целевая версии → причина → несовместимости → твои действия → проверки → наблюдаемый результат. Если миграции не было, прямо скажи и объясни план: upgrade guide, зависимости, критические сценарии и возможность отката.',
 'chat-2-3': 'Раздели возможности по версиям: React 18 — automatic batching, transitions и новая модель root; React 19 — Actions, useActionState, useOptimistic и use; React 19.2 — useEffectEvent и Activity; React 19.3 — ViewTransition и Fragment Refs. Уточни требования версии и интеграции по официальной документации; знание возможности не равно опыту её использования.',
 'chat-2-7': 'Массив зависимостей перечисляет читаемые реактивные значения. После commit React сравнивает каждую позицию через Object.is; при изменении выполняет прежний cleanup и новый setup. Эти правила одинаковы для useEffect и useLayoutEffect; отличается момент выполнения относительно paint.',
 'chat-2-8': 'Без второго аргумента эффект выполняет setup после каждого подходящего commit этого компонента. Перед повторным setup запускается прежний cleanup. Обновление state внутри эффекта может создать цикл, если каждый commit снова меняет state.',
 'chat-2-9': '[] означает, что setup не зависит от реактивных значений render. Он запускается при mount и очищается при unmount; новый mount запускает его снова. В development Strict Mode возможен дополнительный цикл проверки setup/cleanup. Чтение меняющихся props внутри такого эффекта требует пересмотра зависимостей.',
 'chat-2-10': 'React сравнивает зависимости по позициям через Object.is. Объекты и функции сравниваются по ссылке, а не по полям. Два новых {} различны, а мутированный прежний объект остаётся тем же dependency. Сравнение происходит при render/commit, не при произвольной мутации.',
 'chat-2-11': 'Мутация obj.name сама по себе не запускает React-render. Если render произошёл по другой причине, [obj] всё равно содержит прежнюю ссылку, поэтому useLayoutEffect из-за этой зависимости не перезапустится. Новый объект в state меняет ссылку; [obj.name] выражает зависимость от поля при наличии render.',
 'chat-2-12': 'После измерений: держать state ближе к потребителю, не дублировать производные данные, разделять contexts, стабилизировать props там, где помогает memo, мемоизировать дорогие вычисления, виртуализировать длинные списки и разделять код. Transition меняет приоритет работы, а не устраняет её стоимость.',
 'chat-2-13': 'Воспроизвести конкретное взаимодействие и записать React Profiler плюс Performance trace. Найти дорогие renders, причины обновления, long tasks, layout и сеть. Выбрать изменение по обнаруженной причине и повторить тот же сценарий на тех же данных.',
 'chat-3-2': 'as Type не валидирует и не преобразует значение. Ошибка API останется ошибкой runtime даже после двойного assertion через unknown. Внешний unknown надо проверить схемой или корректными guards; assertion оставлять для доказанного знания, которое TypeScript сам не вывел.',
 'chat-3-5': 'Exclude<T, U> реализует распределяемое условие T extends U ? never : T. Каждый член union проверяется отдельно: Exclude<"a" | "b" | 1, string> даёт 1. Поле внутри объектного типа этот механизм не удаляет.',
 'chat-3-6': 'Type Guard — проверка, после которой TypeScript может сузить тип. Встроенные варианты: typeof, instanceof, in и equality. Пользовательский predicate возвращает value is T; его реализация должна действительно доказывать T, иначе компилятор поверит ложному обещанию.',
 'chat-3-7': 'Используют typeof, instanceof, in, equality, discriminated union и анализ ветвлений/возвратов. Пользовательский type predicate или assertion function расширяет набор доказательств. Truthiness удобна только если потеря 0 и пустой строки допустима.',
 'chat-3-8': 'TypeScript использует typeof, instanceof, in, equality и truthiness с анализом потока управления. По общему literal discriminant он различает варианты union. Проверка typeof value === "object" не исключает null; if(value) исключит также допустимые 0 и пустую строку.',
 'chat-3-9': 'Аннотация : Type задаёт тип переменной; as Type утверждает совместимость без проверки runtime; satisfies Type проверяет выражение на совместимость, сохраняя полезную конкретику вывода. Например, satisfies для palette позволяет проверить ключи и значения и сохранить green как string. Это не валидация данных API.',
 'chat-4-1': 'Из изучаемых принципов: SOLID помогает обсуждать ответственность, расширяемость и зависимости; KISS — выбирать понятное решение; DRY — не дублировать одно знание; YAGNI — не строить возможности без текущей необходимости. Для каждого полезнее привести задачу и цену применения, чем только расшифровку.',
 'chat-4-3': 'KISS — выбирать самое простое решение, достаточное для требований. DRY — хранить одно знание в одном месте; похожие строки кода ещё не обязательно одно знание. Два похожих компонента не стоит объединять, если их дальнейшие изменения независимы и общая обёртка потребует множества флагов.',
}

CHAT_EXAMPLES = {
 'chat-2-8': ('Без массива cleanup и setup повторяются при каждом commit.', 'useEffect(() => {\n  syncExternalSystem();\n  return () => disconnect();\n});'),
 'chat-2-9': ('Подписка не читает изменяющиеся props или state; обработчик обновляет state через setter.', 'useEffect(() => {\n  const resize = () => setWidth(window.innerWidth);\n  window.addEventListener("resize", resize);\n  return () => window.removeEventListener("resize", resize);\n}, []);'),
 'chat-2-10': ('Сравнение ссылок происходит тем же правилом Object.is.', 'const obj = { name: "old" };\nconst same = obj;\nobj.name = "new";\nObject.is(obj, same); // true\nObject.is(obj, { name: "new" }); // false'),
 'chat-2-11': ('Первое действие не уведомляет React; второе создаёт новую ссылку.', 'obj.name = "new"; // прежняя ссылка, render не вызван\nsetObj(previous => ({ ...previous, name: "new" }));\n// Новый render получает новый obj: [obj] изменяется.'),
 'chat-3-2': ('Assertion не превратит число в строку и не проверит API.', 'const value: unknown = 42;\nconst title = value as string; // обещание компилятору\n// title.toUpperCase() бросит TypeError в runtime\nif (typeof value === "string") value.toUpperCase();'),
 'chat-3-5': ('Из union исключаются целые совместимые варианты.', 'type A = Exclude<"a" | "b" | 1, string>; // 1\ntype B = Exclude<{ a: string; b: number }, "a">;\n// B всё ещё содержит a и b\ntype C = Omit<{ a: string; b: number }, "a">; // {b: number}'),
 'chat-3-6': ('Guard действительно проверяет поле, которое обещает в predicate.', 'function isUser(value: unknown): value is { name: string } {\n  return typeof value === "object" && value !== null\n    && "name" in value && typeof value.name === "string";\n}'),
}

FOLLOWUP_CODE = {
 ('cross-context',0): POST_CODE,
 ('dedup',0): '// Возможная последовательность без lock:\n// A: getItem(id) -> null\n// B: getItem(id) -> null\n// A: showToast(); setItem(id, "shown")\n// B: showToast(); setItem(id, "shown")\n// Итог: два показа, хотя каждая вкладка проверяла ключ.',
 ('map-set',0): 'const one = {};\nnew Set([one, one]).size; // 1\nnew Set([{}, {}]).size;   // 2',
 ('cloning',0): 'const value = { date: new Date("2026-01-01"), fn() {} };\nconst copy = JSON.parse(JSON.stringify(value));\n// copy.date — строка, свойства fn нет',
 ('promise-combinators',0): 'Promise.all([]);        // fulfilled: []\nPromise.allSettled([]); // fulfilled: []\nPromise.any([]);        // rejected: AggregateError; обработать catch\nPromise.race([]);       // pending',
 ('effect-deps',0): 'const same = obj;\nobj.name = "new";\nObject.is(same, obj); // true: dependency [obj] не изменилась',
 ('never',0): 'function assertNever(value: never): never {\n  throw new Error("Unexpected variant");\n}\n// В default исчерпывающего switch: return assertNever(value);',
 ('omit-exclude',1): 'type Filter<T, U> = T extends U ? never : T;\ntype R = Filter<"a" | 1 | false, string>; // 1 | false',
 ('forms',1): 'function onSubmit(event) {\n  event.preventDefault();\n  const data = new FormData(event.currentTarget);\n  const name = data.get("name"); // input должен иметь name="name"\n}',
}

def block_text(blocks):
    return '\n'.join('\n'.join([b.get('title',''), b.get('text',''), b.get('code',''), *b.get('items',[])]) for b in blocks)

EXTRA_FOLLOWUPS.update({
 'statuses': [('Почему не стоит повторять любой 4xx автоматически?', '4xx может означать невалидный ввод, отсутствие прав или ресурса. Без изменения причины повтор ничего не исправит. Retry выбирается по коду и контракту, например 429 может требовать ожидания Retry-After.')],
 'vulnerabilities': [('Почему CSP не заменяет безопасный вывод HTML?', 'CSP ограничивает загрузку и выполнение ресурсов, но её политика может быть неполной, а HTML-инъекция уже меняет документ. Нужны безопасные API вывода, санитизация допустимого HTML и дополнительные меры по механизму угрозы.')],
 'arrays': [('Как sort чисел может изменить исходный массив и дать неожиданный порядок?', 'sort мутирует массив и без comparator сравнивает строковые представления. [2, 10].sort() даёт [10, 2]. Для чисел нужен (a, b) => a - b; toSorted с тем же comparator возвращает новый массив.')],
 'hooks-list': [('Почему useMemo не подходит для хранения критически важного состояния?', 'Это оптимизационный кэш вычисления, который React может отбросить. Значение должно быть корректно пересчитываемым. Для данных жизненного цикла компонента выбирают state или ref по тому, должен ли изменяться UI.')],
 'query-libs': [('Почему свежесть API-данных нельзя определить только наличием их в store?', 'Сохранённые данные могут устареть. Нужны правила stale time, refetch, инвалидации после мутаций и поведения offline. Query-слой управляет этим жизненным циклом, а обычный client store сам по себе его не задаёт.')],
 'hoc-router': [('Что должен настроить сервер для прямого открытия вложенного SPA URL?', 'Нужен подходящий fallback для клиентских маршрутов на HTML приложения с сохранением правильных правил для API и статики. Иначе переход внутри SPA работает, а reload /profile возвращает серверный 404.')],
 'ts-basics': [('Почему TypeScript не заметит неверный JSON от API во время выполнения?', 'Типы стираются при компиляции. Внешнее значение нужно считать unknown и проверять runtime-схемой или корректными guards. Аннотация интерфейса и assertion не выполняют такую проверку.')],
 'utilities': [('Почему Omit<User, "password"> не удалит password из JSON?', 'Omit преобразует тип, но не значение. Если исходный объект по-прежнему содержит password, сериализация может отправить его. Создать публичный объект runtime и проверить границу выдачи данных.')],
 'build-tools': [('Почему успешная сборка TypeScript через transpiler не гарантирует отсутствие ошибок типов?', 'Некоторые инструменты только удаляют синтаксис типов и преобразуют код. Запускать отдельный tsc --noEmit или предусмотренный typecheck в pipeline, а не полагаться на emit bundle.')],
 'observability': [('Как связать жалобу пользователя, ошибку и медленный API-вызов?', 'Собрать разрешённый context: время, release, route и correlation/trace ID. Ошибка со stack и breadcrumbs показывает путь, trace — где потрачено время, метрики — масштаб. Не отправлять секреты и лишние персональные данные.')],
 'seo': [('Почему SSR не поможет, если страница закрыта noindex?', 'SSR меняет способ доставки HTML, а noindex явно управляет индексацией. Сначала проверить статус, robots/noindex, canonical и доступность содержимого; смена rendering strategy не отменяет эти правила.')],
 'specificity': [('Почему :where(#app) .item не получает вес ID-селектора?', ':where имеет нулевую специфичность вместе с аргументами. Вклад остаётся только у .item. При этом origin, importance и cascade layers могут решить конфликт раньше сравнения специфичности.')],
 'styling': [('Почему при SSR важно согласовать генерацию CSS на сервере и клиенте?', 'Разные class names, порядок вставки или отсутствующие критические стили могут вызвать неверный вид и hydration-проблемы. Библиотека должна иметь подходящую SSR-интеграцию; CSS Modules и runtime CSS-in-JS решают это разными механизмами.')],
 'scripts': [('Почему два async-скрипта нельзя считать выполненными в порядке HTML?', 'Каждый выполняется по готовности загрузки, поэтому второй может стартовать раньше первого. Для зависимых classic scripts используют defer с правильным порядком либо явные module imports.')],
 'images': [('Почему width: 200px не уменьшает размер скачанного изображения?', 'CSS меняет отображение уже выбранного ресурса. Для меньшей передачи нужны подходящий исходный файл, формат и responsive images через srcset/sizes. width/height дополнительно помогают зарезервировать геометрию.')],
 'svg': [('Почему SVG из непроверенной строки нельзя просто вставить через innerHTML?', 'SVG может содержать активное содержимое, обработчики и внешние ссылки. Нужны доверенный источник, подходящая санитизация и безопасный способ встраивания; расширение .svg не доказывает безопасность.')],
 'internationalization': [('Почему строка «найдено N товаров» требует больше, чем перевода слова?', 'В языках различаются plural rules. Нужны локализованные сообщения с формами количества, форматирование чисел, дат и валют через locale-aware API и проверка длины текста в UI.')],
 'kiss-dry-yagni': [('Когда два похожих компонента лучше оставить раздельными?', 'Когда похожа форма кода, но знания и причины изменения независимы. Общая обёртка с множеством флагов увеличит связанность. Выделять только реальное общее правило, когда граница стала ясной.')],
 'architecture-boundaries': [('Как не показать ответ от старого поискового запроса вместо нового?', 'Отменять предыдущий запрос через AbortController и/или сопоставлять ответ с актуальным request ID. При race старый ответ может завершиться позже нового; защита нужна на границе обновления state.')],
 'http-versions': [('Почему multiplexing HTTP/2 не устраняет блокировку из-за потери TCP-пакета?', 'Потоки HTTP/2 делят упорядоченный byte stream TCP. Недостающие байты задерживают передачу последующих данных приложению. QUIC разделяет транспортные потоки, хотя сеть и congestion control остаются общими ресурсами.')],
 'architecture-methods': [('Почему папки atoms и molecules не задают границы бизнес-логики?', 'Atomic Design описывает композицию UI. Правила зависимостей, доменные сценарии и публичные API модулей надо определить отдельно; названия папок сами не предотвращают связанность.')],
 'experience-story': [('Как рассказать о результате, если точных процентов нет?', 'Назови проверенные факты: исчез воспроизводимый баг, сократилось число запросов, прошли конкретные сценарии. Отдельно скажи, чего не измеряла. Не придумывай числа ради убедительности.')],
})

# Explicit examples for each member of the studied array set.
for name,expression in {
 'map':'[1, 2].map(n => n * 2) → [2, 4]', 'filter':'[1, 2, 3].filter(n => n > 1) → [2, 3]',
 'reduce':'[1, 2].reduce((sum, n) => sum + n, 0) → 3', 'reduceRight':'["a", "b"].reduceRight((s, x) => s + x, "") → "ba"',
 'flatMap':'[1, 2].flatMap(n => [n, n]) → [1, 1, 2, 2]', 'find':'[1, 3].find(n => n > 2) → 3; без совпадения undefined',
 'findIndex':'[1, 3].findIndex(n => n > 2) → 1; без совпадения -1', 'includes':'[NaN].includes(NaN) → true',
 'indexOf':'["a", "b", "a"].indexOf("a") → 0', 'lastIndexOf':'["a", "b", "a"].lastIndexOf("a") → 2',
 'some':'[1, 2].some(n => n > 1) → true; для [] результат false', 'every':'[1, 2].every(n => n > 0) → true; для [] результат true',
 'push':'const a=[1]; a.push(2) возвращает 2, а a становится [1,2]', 'pop':'const a=[1,2]; a.pop() возвращает 2, а a становится [1]',
 'shift':'const a=[1,2]; a.shift() возвращает 1, а a становится [2]', 'unshift':'const a=[2]; a.unshift(1) возвращает 2, а a становится [1,2]',
 'splice':'const a=[1,2,3]; a.splice(1,1,9) возвращает [2], a становится [1,9,3]',
 'sort':'const a=[2,10]; a.sort((x,y)=>x-y) меняет a на [2,10]', 'reverse':'const a=[1,2]; a.reverse() меняет a на [2,1]',
 'fill':'const a=[1,2]; a.fill(0) меняет a на [0,0]; объектное значение было бы общей ссылкой',
 'slice':'const a=[1,2,3]; a.slice(1) → [2,3], a не меняется', 'concat':'[1].concat([2]) → [1,2], исходные массивы не меняются',
 'join':'["a","b"].join("-") → "a-b"', 'toSorted':'[2,1].toSorted((a,b)=>a-b) → новый [1,2]',
 'toReversed':'[1,2].toReversed() → новый [2,1]', 'toSpliced':'[1,2,3].toSpliced(1,1) → новый [1,3]', 'with':'[1,2].with(0,9) → новый [9,2]',
}.items(): ITEM_EXAMPLES[name]=expression + '. Учитывай возвращаемое значение и мутацию отдельно от назначения метода.'

def topic_blocks(topic, z):
    blocks=[paragraph(MAIN_LEADS.get(topic['id'], z['takeaway']))]
    if topic.get('order'):
        blocks.append(steps(topic['order'], 'Порядок'))
    blocks.append(steps(z['steps']))
    if topic['drill']:
        blocks.append(steps([i['name'] + ' — ' + i['detail'] for i in topic['items']], 'Весь изучаемый набор'))
    blocks.append(example(z['example'], z['code'] or topic['code'], z['walkthrough']))
    blocks.extend(z.get('examples',[]))
    if topic['note']:
        blocks.append(paragraph(topic['note'], 'Ограничения и уточнения'))
    return blocks

def revise_questions(questions, byid, explanations, followup_questions, registry, sources):
    for tid, examples in MEMBER_EXAMPLES.items():
        assert len(examples)==len(byid[tid]['items']), (tid,len(examples),len(byid[tid]['items']))
    for topic_id in followup_questions:
        assert topic_id in FOLLOWUP_ANSWERS, f'Missing reviewed followup: {topic_id}'
        assert len(followup_questions[topic_id]) == len(FOLLOWUP_ANSWERS[topic_id])
    # Concrete, short questions for previously generic followups.
    for tid, topic in byid.items():
        if tid not in followup_questions and tid not in EXTRA_FOLLOWUPS:
            item=topic['items'][0]
            EXTRA_FOLLOWUPS[tid]=[(f'Объясни роль «{item["name"]}» и приведи пример.', item['detail'] + '\n\nПример: ' + ITEM_EXAMPLES.get(item['name'], explanations[tid]['example']))]
    for q in questions:
        topic=byid[q['topic']]; z=explanations[q['topic']]
        q.pop('check',None)
        if '-item-' in q['id']:
            index=int(q['id'].rsplit('-',1)[1])-1
            item=topic['items'][index]
            blocks=[paragraph(item['detail'], item['name'])]
            if topic['id'] in MEMBER_EXAMPLES:
                sample=MEMBER_EXAMPLES[topic['id']][index]
            elif item['name'] in ITEM_EXAMPLES:
                sample=ITEM_EXAMPLES[item['name']]
            else:
                parts=item['name'].split(' / ')
                assert all(part in ITEM_EXAMPLES for part in parts), (topic['id'],item['name'])
                sample='\n\n'.join(ITEM_EXAMPLES[part] for part in parts)
            blocks.append(example(sample))
        elif q['id'] in CHAT_ANSWERS:
            blocks=[paragraph(CHAT_ANSWERS[q['id']])]
            if q['id'] in CHAT_EXAMPLES:
                text,code=CHAT_EXAMPLES[q['id']]
                blocks.append(example(text,code))
            elif q['topic'] in ('effect-deps','assertions','narrowing','omit-exclude'):
                blocks.append(example(z['example'], z['code'] or topic['code'], z['walkthrough']))
        else:
            blocks=topic_blocks(topic,z)
        if q['kind']=='experience':
            blocks=[paragraph('Используй только реальный опыт. Если такого случая не было, обозначь это и объясни предполагаемый подход.', 'Без выдуманных фактов'),
                    steps(['Контекст: продукт, роль и ограничения.','Задача: наблюдаемая проблема и критерий успеха.','Альтернативы: что рассматривала и почему выбрала решение.','Действия: что сделала лично.','Проверка и результат: известные факты без придуманных процентов.','Вывод: что бы повторила или изменила.'],'Структура рассказа'),
                    paragraph(CHAT_ANSWERS.get(q['id'],z['takeaway']),'Теоретический ориентир')]
            if q['id']=='chat-4-4':
                blocks.append(steps([i['name']+' — '+i['detail'] for i in topic['items']], 'Изучаемые паттерны'))
        if q['topic']=='dedup' and not any(b.get('code')==IDB_CODE for b in blocks):
            blocks.append(example('Вариант без Web Locks: add вставляет только новый ключ. В этом примере store уже создан, истечение TTL и очистка должны проектироваться отдельно. После успешного claim остаётся риск падения до показа.', IDB_CODE,
                                  ['ConstraintError — ожидаемый дубль; прочие ошибки завершают операцию ошибкой.','Результат считается подтверждённым после tx.oncomplete. Успех отдельного request ещё не commit.','Здесь не обещается exactly-once: claim фиксируется до побочного эффекта.']))
        q['answerBlocks']=blocks
        # Plain text is retained for interoperability and search; UI renders only structured blocks.
        q['answer']=block_text(blocks)
        if q['topic'] in followup_questions:
            pairs=list(zip(followup_questions[q['topic']], FOLLOWUP_ANSWERS[q['topic']]))
        else:
            pairs=EXTRA_FOLLOWUPS[q['topic']]
        q['followups']=[dict(question=prompt, answerBlocks=[paragraph(answer)]) for prompt,answer in pairs]
        for i, f in enumerate(q['followups']):
            code=FOLLOWUP_CODE.get((q['topic'],i))
            if code: f['answerBlocks'].append(example('Фрагмент иллюстрирует именно это уточнение; служебные функции принадлежат приложению.',code))
        if q['topic']=='dedup':
            q['followups'] += [dict(question='Чем claim через IndexedDB отличается от Web Lock?',answerBlocks=[paragraph('add с уникальным ключом может атомарно закрепить ID. Web Lock защищает произвольную async-критическую секцию, но сам не хранит историю после освобождения. Оба решения не делают показ UI и сохранение ID одной транзакцией.'), example('Успех должен означать commit всей транзакции.',IDB_CODE)])]
        q['sources']=topic['sources']
    # New consequence exercises get stable, explicit IDs.
    new_questions=[
      ('dedup-leader-replay','dedup','Вкладка-лидер закрылась после получения события. Новый лидер получает это же событие снова. Опиши восстановление и защиту от повтора.', 'Лидерство ограничивает число соединений, но не отменяет replay. Новый лидер восстанавливает поток по cursor или snapshot, сохраняет стабильные ID и использует общую историю claim. При сбое между claim и показом возможен пропуск; политика должна быть явной.'),
      ('dedup-ttl-replay','dedup','История обработанных ID очищена через сутки, а сервер повторил событие за прошлую неделю. Какой результат возможен и как выбрать срок хранения?', 'После очистки событие снова выглядит новым и может быть показано. TTL должен согласовываться с максимальным replay и допустимыми рисками. Нужны серверные гарантии, ограниченный cursor или более длительная история, если старые события нельзя повторять.'),
      ('postmessage-same-origin-frame','postmessage-safety','Два iframe имеют одинаковый origin. Сообщение пришло от второго вместо ожидаемого первого. Как это обнаружить?', 'Точное сравнение event.origin пропустит оба окна. Проверка event.source === expectedFrame.contentWindow различает их; затем нужно проверить data и допустимость действия.'),
      ('storage-initial-tab','storage-events','Новую вкладку открыли после смены темы, а новых изменений больше нет. Как ей получить тему?', 'Прочитать актуальное значение localStorage при старте и применить к UI. storage event сообщает будущие изменения другим документам, но не воспроизводит историю.'),
      ('locks-wait-versus-holder','web-locks','AbortController сработал, когда callback уже владеет lock. Как завершить соединение и освободить lock?', 'Сигнал отмены ожидания уже не завершит callback. Нужен собственный обработчик завершения: разрешить удерживающий Promise, закрыть EventSource в finally и вернуть управление из callback.'),
      ('notifications-permission-fallback','web-notifications','Пользователь запретил уведомления. Как сохранить полезный интерфейс без повторного запроса разрешения?', 'Не обходить отказ. Оставить историю событий и in-page UI, показывать текущее состояние настройки. При явном желании пользователя объяснить изменение разрешения в настройках браузера.'),
    ]
    for id,tid,prompt,answer in new_questions:
        topic=byid[tid]
        q=dict(id=id,topic=tid,lesson=topic['lesson'],kind='scenario',prompt=prompt,
               answerBlocks=[paragraph(answer)],answer=answer,sources=topic['sources'],notion=True,
               followups=[dict(question=p,answerBlocks=[paragraph(a)]) for p,a in EXTRA_FOLLOWUPS.get(tid,[])])
        if tid=='dedup':
            q['followups']=[dict(question=p,answerBlocks=[paragraph(a)]) for p,a in zip(followup_questions[tid],FOLLOWUP_ANSWERS[tid])]
        questions.append(q)
    note_map=[
     ('41695f65d612818cafa0df3d9e08cbeb','Workers: типы и примеры','workers'),
     ('41695f65d61281a987dfd985af56bfb2','Альтернативы Workers','worker-alternatives'),
     ('41695f65d612819a8bbef889facc7998','Проверки postMessage','postmessage-safety'),
     ('41695f65d6128142881aefe9693bbc93','Получатели storage event','storage-events'),
     ('41695f65d612814281cdf829f012768b','Same-origin iframe','iframe-uses'),
     ('41695f65d6128111be5ccce18c8b9076','Web Locks','web-locks'),
     ('41695f65d612815ab79eda62b995fa71','Дедупликация: детали и сбои','dedup'),
     ('41695f65d6128172b893dfc8da3600fa','Notifications API','web-notifications'),
     ('41795f65d61281ef9f0ffaef9e336e36','Вопросы на следствия','postmessage-safety'),
     ('41795f65d6128129b451dbdd6e40e2b9','Структура и код в образцах','dedup'),
     ('41795f65d61281e49fb5ce3f58fdce68','Скрытые ответы на уточнения','realtime'),
     ('41795f65d612813aa1dcdf32250f3b05','Удалить самопроверку','realtime'),
     ('41795f65d612811e998dd6da75dcf53e','Расширить короткие ответы','render-strategies'),
     ('41795f65d61281dcb8a3eb14ba4aaa39','Сохранить пошаговые примеры','cloning'),
     ('41795f65d61281dba37ffd73dc6713f1','Образец короткого ответа','cloning'),
    ]
    for id,title,tid in note_map:
        # The user moved these implemented notes to Trash. Keep provenance in
        # coverage, but present only accessible documentation links in lessons.
        registry.append(dict(origin='Notion · Gen notes',title=title,topic=tid,lesson=byid[tid]['lesson'],question=tid+'-main',status='included',sourceArchived=True,url=f'https://app.notion.com/p/{id}'))
    for tid in ('worker-alternatives','web-locks','postmessage-safety','storage-events','iframe-uses','web-notifications'):
        registry.append(dict(origin='Дополнение · Gen notes',title=byid[tid]['title'],topic=tid,lesson='communication',question=tid+'-main',status='included'))
