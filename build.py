"""Build the offline course. No third-party dependencies; only this folder is written."""
from pathlib import Path
import json, html, re
from explanations import EXPLANATIONS

ROOT = Path(__file__).resolve().parent
NOTION = 'https://app.notion.com/p/questions-37395f65d61280cf83b9ec0b1f33492d'
S = {
 'browser': ('MDN: как работает браузер','https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/How_browsers_work'),
 'http': ('MDN: HTTP','https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview'),
 'methods': ('MDN: HTTP methods','https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods'),
 'cache': ('MDN: HTTP caching','https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching'),
 'rest': ('Fielding: REST constraints','https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm'),
 'graphql': ('GraphQL: Learn','https://graphql.org/learn/'),
 'grpc': ('gRPC: core concepts','https://grpc.io/docs/what-is-grpc/core-concepts/'),
 'cors': ('MDN: CORS','https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS'),
 'cookies': ('MDN: Set-Cookie','https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie'),
 'storage': ('MDN: Web Storage','https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API'),
 'idb': ('MDN: IndexedDB','https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API'),
 'security': ('OWASP: Cheat Sheets','https://cheatsheetseries.owasp.org/'),
 'workers': ('MDN: Web Workers','https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API'),
 'sw': ('MDN: Service Workers','https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API'),
 'bc': ('MDN: BroadcastChannel','https://developer.mozilla.org/en-US/docs/Web/API/Broadcast_Channel_API'),
 'post': ('MDN: window.postMessage','https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage'),
 'locks': ('MDN: Web Locks','https://developer.mozilla.org/en-US/docs/Web/API/Web_Locks_API'),
 'ws': ('MDN: WebSockets','https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API'),
 'sse': ('MDN: Server-sent events','https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events'),
 'collections': ('MDN: Keyed collections','https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Keyed_collections'),
 'gc': ('MDN: управление памятью','https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Memory_management'),
 'proxy': ('MDN: Proxy','https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Proxy'),
 'array': ('MDN: Array','https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array'),
 'clone': ('MDN: structuredClone','https://developer.mozilla.org/en-US/docs/Web/API/Window/structuredClone'),
 'closure': ('MDN: Closures','https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures'),
 'functions': ('MDN: Function','https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function'),
 'promise': ('MDN: Promise','https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise'),
 'loop': ('MDN: microtasks','https://developer.mozilla.org/en-US/docs/Web/API/HTML_DOM_API/Microtask_guide'),
 'timers': ('MDN: setTimeout','https://developer.mozilla.org/en-US/docs/Web/API/Window/setTimeout'),
 'streams': ('MDN: Streams API','https://developer.mozilla.org/en-US/docs/Web/API/Streams_API'),
 'react': ('React: render and commit','https://react.dev/learn/render-and-commit'),
 'keys': ('React: preserving state','https://react.dev/learn/preserving-and-resetting-state'),
 'hooks': ('React: встроенные хуки','https://react.dev/reference/react/hooks'),
 'effect': ('React: useEffect','https://react.dev/reference/react/useEffect'),
 'layout': ('React: useLayoutEffect','https://react.dev/reference/react/useLayoutEffect'),
 'context': ('React: useContext','https://react.dev/reference/react/useContext'),
 'state': ('React: choosing state structure','https://react.dev/learn/choosing-the-state-structure'),
 'redux': ('Redux: fundamentals','https://redux.js.org/tutorials/fundamentals/part-2-concepts-data-flow'),
 'rtk': ('Redux Toolkit: RTK Query','https://redux-toolkit.js.org/rtk-query/overview'),
 'query': ('TanStack Query: overview','https://tanstack.com/query/latest/docs/framework/react/overview'),
 'swr': ('SWR: getting started','https://swr.vercel.app/docs/getting-started'),
 'mobx': ('MobX: introduction','https://mobx.js.org/README.html'),
 'input': ('React: input','https://react.dev/reference/react-dom/components/input'),
 'router': ('React Router: routing','https://reactrouter.com/start/declarative/routing'),
 'suspense': ('React: Suspense','https://react.dev/reference/react/Suspense'),
 'react19': ('React 19: release','https://react.dev/blog/2024/12/05/react-19'),
 'upgrade': ('React 19: upgrade guide','https://react.dev/blog/2024/04/25/react-19-upgrade-guide'),
 'ts': ('TypeScript: everyday types','https://www.typescriptlang.org/docs/handbook/2/everyday-types.html'),
 'narrow': ('TypeScript: narrowing','https://www.typescriptlang.org/docs/handbook/2/narrowing.html'),
 'satisfies': ('TypeScript: satisfies','https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html'),
 'utility': ('TypeScript: Utility Types','https://www.typescriptlang.org/docs/handbook/utility-types.html'),
 'generics': ('TypeScript: generics и variance','https://www.typescriptlang.org/docs/handbook/2/generics.html'),
 'profiler': ('React: Profiler','https://react.dev/reference/react/Profiler'),
 'memo': ('React: memo','https://react.dev/reference/react/memo'),
 'vitals': ('web.dev: Core Web Vitals','https://web.dev/articles/vitals'),
 'splitting': ('Webpack: code splitting','https://webpack.js.org/guides/code-splitting/'),
 'otel': ('OpenTelemetry: signals','https://opentelemetry.io/docs/concepts/signals/'),
 'sentry': ('Sentry: JavaScript','https://docs.sentry.io/platforms/javascript/'),
 'prometheus': ('Prometheus: overview','https://prometheus.io/docs/introduction/overview/'),
 'grafana': ('Grafana: fundamentals','https://grafana.com/docs/grafana/latest/fundamentals/'),
 'render': ('web.dev: rendering on the web','https://web.dev/articles/rendering-on-the-web'),
 'hydrate': ('React: hydrateRoot','https://react.dev/reference/react-dom/client/hydrateRoot'),
 'isr': ('Next.js: ISR','https://nextjs.org/docs/app/guides/incremental-static-regeneration'),
 'seo': ('Google: SEO starter guide','https://developers.google.com/search/docs/fundamentals/seo-starter-guide'),
 'css': ('MDN: specificity','https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_cascade/Specificity'),
 'script': ('MDN: script','https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/script'),
 'images': ('MDN: responsive images','https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images'),
 'svg': ('MDN: SVG','https://developer.mozilla.org/en-US/docs/Web/SVG'),
 'i18n': ('W3C: localization vs internationalization','https://www.w3.org/International/questions/qa-i18n'),
 'solid': ('Robert C. Martin: SOLID relevance','https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html'),
 'yagni': ('Martin Fowler: YAGNI','https://martinfowler.com/bliki/Yagni.html'),
 'patterns': ('React: sharing logic with custom hooks','https://react.dev/learn/reusing-logic-with-custom-hooks'),
 'mf': ('Webpack: Module Federation','https://webpack.js.org/concepts/module-federation/'),
 'radio': ('GreatFrontEnd: RADIO framework','https://www.greatfrontend.com/front-end-system-design-playbook/framework'),
}

LESSONS = [
 ('url','От URL до страницы','Путь запроса и работа браузера'),
 ('http','HTTP и API','Методы, кэширование и контракты'),
 ('security','Безопасность и хранение','Границы доступа и данные в браузере'),
 ('communication','Workers и обмен сообщениями','Вкладки, iframe и сервер'),
 ('javascript','Объекты и память','Коллекции, ссылки и замыкания'),
 ('async','Асинхронность','Promises, очереди и порядок выполнения'),
 ('react-render','React: рендеринг','Идентичность, Fiber и обновления'),
 ('react-effects','React: хуки и эффекты','Зависимости и внешние системы'),
 ('react-state','React: состояние и данные','Context, store и server state'),
 ('react-app','React: приложение','Формы, маршруты и миграции'),
 ('typescript','TypeScript','Типы, проверки и преобразования'),
 ('performance','Производительность','Измерить, найти причину, улучшить'),
 ('rendering','Рендеринг и SEO','Где появляется HTML'),
 ('html-css','HTML, CSS и изображения','Загрузка и отображение ресурсов'),
 ('architecture','Архитектура и принципы','Объяснять решения и компромиссы'),
]
topics = []
def t(lesson, id, title, summary, items, question, sources, *, kind='recall', note='', code='', notion=True, drill=False, aliases=()):
    topic = dict(lesson=lesson,id=id,title=title,summary=summary,items=[dict(name=a,detail=b) for a,b in items],question=question,sources=sources.split(),kind=kind,note=note,code=code,notion=notion,drill=drill,aliases=list(aliases))
    topics.append(topic)
    return topic

# 01. Network navigation and browser pipeline.
t('url','navigation','От адреса до первого изображения страницы',
 'Браузер разбирает URL, находит ресурс локально или запрашивает его по сети, а затем постепенно строит и отображает документ. Это не ожидание полной загрузки всех ресурсов.',[
 ('URL и локальный ответ','Разобрать схему, host, порт, путь и query. Управляющий Service Worker может обработать запрос; HTTP-кэш может дать свежий ответ или потребовать проверки.'),
 ('DNS','Если адрес ещё неизвестен и нужен сетевой запрос, получить IP по имени. Кэши сокращают эту работу.'),
 ('Соединение','Для HTTPS поверх HTTP/1.1 или HTTP/2 используются TCP и TLS. Уже открытое соединение можно переиспользовать; HTTP/3 использует QUIC поверх UDP.'),
 ('Запрос и ответ','Метод, URL и заголовки описывают запрос; статус, заголовки и тело — ответ. HTML может поступать частями.'),
 ('Парсинг и отображение','Парсить HTML, находить CSS/JS/изображения, строить DOM/CSSOM, вычислять стили, layout, paint и compositing.')],
 'Опиши путь от ввода URL до первого отображения страницы. Какие этапы могут быть пропущены?', 'browser http',
 note='Уточнение к Notion: TLS нужен в объяснении HTTPS; TCP не является транспортом HTTP/3. Service Worker, HTTP-кэш и DNS — не одна обязательная линейная очередь проверок.')
t('url','pipeline','Фазы рендеринга страницы','Удобная модель: разобрать документ → вычислить стили → геометрию → команды рисования → собрать слои. Изменение страницы не всегда запускает все стадии.',[
 ('DOM и CSSOM','DOM описывает документ, CSSOM — правила стилей. JavaScript может изменить оба; CSSOM не создаётся выполнением JavaScript.'),
 ('Style и render tree','Вычислить применимые стили. display:none исключает элемент из layout, visibility:hidden сохраняет занимаемое место.'),
 ('Layout / reflow','Вычислить размеры и положение. Изменение ширины или чтение геометрии после записи стилей может потребовать нового layout.'),
 ('Paint','Подготовить отрисовку текста, фона, границ и других визуальных частей.'),
 ('Compositing','Собрать подготовленные слои. Некоторые transform/opacity-анимации обходятся без нового layout и paint; это зависит от слоёв и реализации.')],
 'Восстанови порядок стадий после получения HTML и объясни назначение каждой.', 'browser',kind='order',
 note='Уточнение к Notion: отдельный compositor layer не гарантирован для любого transform или position:fixed; большое число слоёв расходует память.')
t('url','cdn','CDN и путь через инфраструктуру','CDN приближает к пользователю копии ресурсов и иногда выполняет код на edge. Cache miss обычно ведёт к origin-серверу.',[
 ('CDN','Уменьшает сетевую задержку и нагрузку на origin, но требует корректных cache keys и правил инвалидирования.'),
 ('Прокси и балансировщик','Прокси пересылает запросы, балансировщик распределяет их между экземплярами сервиса; функции могут совмещаться.'),
 ('Кэш приватных данных','Общие кэши не должны выдавать ответ одного пользователя другому. Учитывать Cache-Control, Vary и авторизацию.')],
 'Статика загружается медленно из другой страны. Что даст CDN и какие данные нельзя бездумно кэшировать?', 'http cache',kind='scenario')

# 02. HTTP and API.
t('http','message','HTTP-запрос и ответ','HTTP описывает обмен сообщениями. HTTPS добавляет защищённый транспорт TLS: конфиденциальность, целостность и проверку сервера.',[
 ('Запрос','Метод, адрес ресурса, заголовки и необязательное тело. В HTTP/2 и HTTP/3 представление бинарное, а не текстовая start line.'),
 ('Ответ','Статус, заголовки и необязательное тело. Заголовки описывают формат, кэш, cookies и политики.'),
 ('Query и body','Query — часть URL, удобная для фильтрации и ссылок; body — содержимое запроса, например JSON. HTTPS шифрует оба при передаче, но URL может попасть в историю и логи.')],
 'Из каких частей состоят HTTP-запрос и ответ? Сравни query и body.', 'http',kind='compare')
t('http','methods','Методы HTTP и идемпотентность','Идемпотентность означает одинаковый предполагаемый эффект повторных одинаковых запросов на сервере; коды ответов могут различаться.',[
 ('GET','Получить представление. Safe и идемпотентный; сервер не должен использовать его для изменения бизнес-состояния.'),
 ('HEAD','Семантика GET без тела ответа. Проверка метаданных; отдельные заголовки, вычисляемые при генерации тела, могут отсутствовать.'),
 ('POST','Передать данные для обработки. По общему контракту не идемпотентный; API может добавить idempotency key.'),
 ('PUT','Создать или заменить состояние ресурса по известному URI. Идемпотентный.'),
 ('PATCH','Применить частичные изменения. Идемпотентность зависит от операции: присвоить значение и увеличить счётчик — разные случаи.'),
 ('DELETE','Удалить связь ресурса с URI. Идемпотентный по эффекту, даже если второй ответ — 404.'),
 ('OPTIONS','Узнать доступные варианты взаимодействия; используется в CORS preflight.')],
 'Перечисли изучаемые HTTP-методы, назначение и идемпотентность каждого.', 'methods',drill=True,
 note='Уточнение к Notion: повторный ответ не обязан совпадать с первым; POST не обязательно создаёт ресурс, а ETag не обязан быть хэшем.')
t('http','statuses','Классы статусов HTTP','Статус сообщает результат обработки HTTP-запроса. Его нужно читать вместе с контрактом API и телом ошибки.',[
 ('1xx','Информация о промежуточной обработке: 100 Continue; 101 Switching Protocols используется при классическом WebSocket upgrade.'),
 ('2xx','Успех: 200 OK, 201 Created, 204 No Content.'),
 ('3xx','Перенаправление и работа с представлениями: 301/308 постоянный redirect, 302/307 временный, 304 Not Modified — повторно использовать кэш.'),
 ('4xx','Ошибка запроса/доступа: 400, 401 — отсутствуют подходящие credentials, 403 — доступ запрещён, 404, 409 — конфликт, 429 — ограничение частоты.'),
 ('5xx','Проблема сервера: 500, 502 — некорректный ответ upstream, 503 — временно недоступен, 504 — timeout upstream.')],
 'Назови пять классов HTTP-статусов и объясни разницу между 401, 403, 404, 500 и 503.', 'http',kind='match',drill=True)
t('http','caching','HEAD, заголовки и 304','Свежий ответ можно использовать без сети. Устаревший ответ можно валидировать условным запросом и получить 304 без повторной передачи тела.',[
 ('Описание представления','Content-Type — формат; Content-Length — размер тела в байтах, если известен; Content-Encoding — кодирование; Content-Language — язык.'),
 ('Cache-Control','max-age задаёт свежесть; no-cache требует проверки перед повторным использованием; no-store запрещает хранение. private ограничивает общие кэши.'),
 ('ETag / If-None-Match','Сервер задаёт непрозрачный валидатор версии; клиент возвращает его для проверки. Валидатор не обязан быть хэшем.'),
 ('Last-Modified / If-Modified-Since','Дата изменения и условная проверка по времени. Имеет ограниченную точность.'),
 ('Другие заголовки HEAD','Location — redirect; Accept-Ranges — диапазоны; Date/Server — метаданные; Set-Cookie — cookie; CSP/HSTS — политики; Access-Control-* — CORS.')],
 'Ресурс уже есть в кэше. Объясни варианты без запроса, с 304 и с новым 200; зачем здесь HEAD?', 'cache methods',
 note='Уточнение к Notion: no-cache не означает «не хранить»; no-store — отдельная директива. HEAD не заменяет условный GET автоматически.')
t('http','rest','REST и RESTful API','REST — архитектурный стиль. JSON по HTTP сам по себе не доказывает соблюдение REST.',[
 ('Client–server','Разделить интерфейс клиента и ответственность сервера.'),
 ('Stateless','Запрос содержит контекст, нужный для его обработки; это не запрещает серверу хранить ресурсы и бизнес-данные.'),
 ('Cacheable','Ответ сообщает возможность повторного использования.'),
 ('Uniform interface','Идентификация ресурсов, работа с представлениями, самодостаточные сообщения и гипермедиа как двигатель состояния приложения.'),
 ('Layered system','Клиенту не требуется знать обо всех промежуточных слоях.'),
 ('Code on demand — необязательно','Сервер может расширить возможности клиента передаваемым кодом; это единственное необязательное ограничение REST.')],
 'Перечисли ограничения REST и объясни каждое на примере API.', 'rest',drill=True,
 note='Дополнение к Notion: включены необязательный code-on-demand и гипермедиа в uniform interface, часто опускаемые в кратких конспектах.')
t('http','api-styles','REST, SOAP, GraphQL и gRPC','Выбор зависит от клиентов, контрактов, доставки данных и инфраструктуры. Ни один подход не является универсально самым быстрым.',[
 ('REST','Ресурсы и представления, стандартная семантика HTTP, естественное HTTP-кэширование.'),
 ('SOAP','Протокол сообщений на основе XML с формальным контрактом и расширениями; может работать не только поверх HTTP.'),
 ('GraphQL','Схема с типами; query читает выбранные поля, mutation изменяет данные, subscription доставляет обновления. Нужны контроль сложности запросов и решение N+1.'),
 ('gRPC','RPC с описанием сервисов, часто Protocol Buffers, генерацией кода и streaming. Обычный браузер не вызывает native gRPC напрямую: нужен gRPC-Web или другой gateway.')],
 'Сравни REST, SOAP, GraphQL и gRPC по контракту, форме запроса и ограничениям браузера.', 'graphql grpc rest',kind='compare',drill=True)
t('http','pagination','Offset и cursor pagination','Pagination ограничивает объём ответа. Важен стабильный порядок, включая уникальный tie-breaker.',[
 ('Offset','Пропустить N элементов и взять следующую порцию. Удобны номера страниц, но вставки и удаления смещают границы.'),
 ('Cursor','Продолжить после позиции из cursor, например пары createdAt/id. Лучше подходит для ленты, но произвольный переход на страницу сложнее.'),
 ('Ограничения','Cursor не гарантирует snapshot и отсутствие любых повторов при изменении сортировочных полей. Клиенту иногда всё равно нужна дедупликация по ID.')],
 'Для бесконечной ленты выбери pagination и объясни, что произойдёт при новых записях.', 'graphql',kind='scenario')

# 03. Browser security and storage.
t('security','tls','TLS и сертификат','TLS защищает данные в пути и подтверждает сервер при корректной проверке сертификата. Он не делает код приложения автоматически безопасным.',[
 ('Конфиденциальность','Перехватчик не читает содержимое запросов и ответов.'),
 ('Целостность','Изменения защищённых данных обнаруживаются.'),
 ('Аутентичность сервера','Проверяются имя хоста, срок действия и цепочка доверия сертификата.')],
 'Объясни простыми словами три задачи TLS и роль сертификата.', 'http',kind='explain',
 note='Уточнение к Notion: историческое название «SSL-сертификат» обычно относится к сертификату для современного TLS.')
t('security','cors','Origin, CORS и OPTIONS','Origin — схема, host и порт. CORS — браузерный механизм разрешения чтения cross-origin ответов, а не авторизация пользователя.',[
 ('Простой запрос','Может уйти без preflight. Без разрешающих заголовков браузер не предоставит ответ скрипту, хотя сервер мог выполнить действие.'),
 ('Preflight','Для некоторых методов, headers и content types браузер сначала отправляет OPTIONS с Origin и Access-Control-Request-*.'),
 ('Разрешение','Сервер отвечает Access-Control-Allow-Origin, при необходимости Allow-Methods/Allow-Headers. Для credentials нужен Allow-Credentials и конкретный origin вместо *.'),
 ('Граница защиты','curl не применяет браузерный CORS. Защита от CSRF и проверки доступа на сервере нужны отдельно.')],
 'fetch работает в curl, но браузер не даёт прочитать ответ. Объясни проверку CORS и порядок preflight.', 'cors',kind='scenario',
 note='Уточнение к Notion: браузер не всегда блокирует саму отправку cross-origin запроса; часто он блокирует доступ к ответу.')
t('security','cookies','Cookies: назначение и атрибуты','Cookie хранится в браузере и автоматически добавляется к подходящим HTTP-запросам с учётом правил credentials, SameSite и политик браузера.',[
 ('Expires / Max-Age','Дата истечения / время жизни в секундах. При наличии обоих Max-Age имеет приоритет.'),
 ('Domain / Path','Область отправки по домену и пути. Path не является защитной границей доступа к данным.'),
 ('Secure','Ограничить отправку защищённым соединением; существуют специальные localhost-исключения.'),
 ('HttpOnly','Не давать JavaScript читать cookie через document.cookie. Это не предотвращает все последствия XSS.'),
 ('SameSite','Strict/Lax/None ограничивают cross-site отправку. SameSite=None требует Secure; cross-site и cross-origin — разные понятия.'),
 ('Session / persistent','Без Expires/Max-Age cookie сессионная, но восстановление сессии браузера может её восстановить. Типичный лимит одной cookie около 4 KiB.')],
 'Перечисли атрибуты cookies и объясни действие каждого. Какие выберешь для session cookie?', 'cookies',drill=True)
t('security','web-storage','Хранилища браузера','Сравнивай срок жизни, область видимости, структуру данных, синхронность и способ отправки на сервер.',[
 ('Cookies','Небольшие значения, автоматическая отправка подходящим запросам, атрибуты безопасности.'),
 ('localStorage','Синхронные строковые пары ключ–значение, общие для origin и сохраняемые между сессиями. Квота ограничена, доступ может быть запрещён.'),
 ('sessionStorage','Строковые пары для origin и конкретной вкладки. Переживает reload; новая вкладка может получить исходную копию, но далее хранит её отдельно.'),
 ('IndexedDB','Асинхронное транзакционное хранилище структурированных данных и Blob. Подходит для offline и больших наборов; квота и возможное вытеснение зависят от браузера.'),
 ('Cache API','Хранилище пар Request/Response с явным управлением. Используется для offline, не равно автоматическому HTTP-кэшу.')],
 'Сравни пять браузерных хранилищ и выбери варианты для настроек, черновика вкладки и offline-данных.', 'storage idb sw',kind='compare',drill=True,
 note='Уточнение к Notion: квоты не универсальны; IndexedDB доступен и workers, а не только коду страницы.')
t('security','auth','Аутентификация и авторизация','Аутентификация отвечает «кто пользователь», авторизация — «что ему разрешено». Проверка только в интерфейсе не защищает API.',[
 ('Сессия','Браузер хранит идентификатор сессии, сервер связывает его с пользователем. Cookie часто HttpOnly, Secure и с подходящим SameSite.'),
 ('Bearer token','Тот, кто предъявил токен, получает соответствующий доступ. Нужны срок жизни, отзыв/обновление и защита хранения; JWT — формат, а не синоним авторизации.'),
 ('Проверка прав','Каждый защищённый запрос проверяется сервером для действия и ресурса. CASL может описывать правила в UI, но не заменяет сервер.'),
 ('OAuth/OIDC','OAuth делегирует доступ; OpenID Connect добавляет идентификацию. Popup требует проверки origin/state и безопасного обмена результатом.')],
 'Пользователь скрыт от кнопки удаления, но отправляет DELETE вручную. Где должна сработать проверка?', 'security',kind='scenario')
t('security','vulnerabilities','Уязвимости и защита','Защита строится на нескольких независимых мерах. HTTPS, CORS и HttpOnly решают разные задачи.',[
 ('HTML injection / XSS','Вставка недоверенного HTML опасна; использовать контекстное escaping, безопасные DOM API, sanitization для разрешённого HTML. React экранирует текст, но dangerouslySetInnerHTML требует защиты.'),
 ('CSP','Политика источников и выполнения контента; nonce/hash и строгая script-src уменьшают риск исполнения чужого кода. Не замена исправлению XSS.'),
 ('CSRF','Чужой сайт инициирует действие с автоматически прикладываемыми credentials. Защита: SameSite, CSRF-токены, проверка Origin; не выполнять изменения через GET.'),
 ('Broken access control','Проверять права на сервере, включая доступ к конкретному объекту. Скрытая кнопка и случайный ID не являются защитой.'),
 ('Компоненты и мониторинг','Обновлять уязвимые зависимости, ограничивать права, логировать подозрительную активность без секретов и персональных данных.')],
 'Сопоставь угрозы с мерами защиты и объясни, почему одной меры недостаточно.', 'security',kind='match',drill=True)

# 04. Communication.
t('communication','workers','Web Worker, SharedWorker и Service Worker','Worker выполняет JavaScript вне потока UI. DOM напрямую недоступен; данные передаются сообщениями, часто со structured clone или transferable objects.',[
 ('Dedicated Web Worker','Отдельная вычислительная задача: большой разбор файла, расчёты. Не ускоряет сам алгоритм автоматически, но разгружает UI.'),
 ('SharedWorker','Общий worker для нескольких подходящих same-origin контекстов; соединения через MessagePort. Можно централизовать соединение, учитывая поддержку браузеров.'),
 ('Service Worker','Событийный посредник для fetch, offline, push и обновлений. Нужен secure context; браузер может остановить его, поэтому память не является постоянным хранилищем.')],
 'Сравни Web Worker, SharedWorker и Service Worker: задачи, жизненный цикл, доступ к DOM.', 'workers sw',kind='compare',drill=True)
t('communication','broadcast','BroadcastChannel','Контексты с одинаковым именем канала, origin и подходящим storage partition могут обмениваться сообщениями. Канал не сохраняет историю.',[
 ('Создание','new BroadcastChannel("auth"); каждый участник подписывается на message.'),
 ('Передача','postMessage(data) использует structured clone. Объект отправителя не получает своё сообщение через тот же экземпляр; другие экземпляры могут получить.'),
 ('Завершение','Убирать обработчики и вызывать close(), когда канал больше не нужен. Закрытая вкладка пропускает сообщения.')],
 'Объясни, как использовать BroadcastChannel для logout во всех вкладках и что увидит вкладка, открытая позже.', 'bc',kind='explain')
t('communication','cross-context','Как выбрать связь между вкладками и iframe','Сначала выясни, кто с кем общается: same-origin вкладки, конкретное окно другого origin или сервер.',[
 ('Same-origin вкладки','BroadcastChannel для сообщений; storage event для изменений localStorage в других вкладках. Начальное состояние читать отдельно.'),
 ('iframe / popup','window.postMessage при наличии ссылки на окно. Задать точный targetOrigin, проверять event.origin, source и форму данных.'),
 ('Общий координатор','SharedWorker или Service Worker может пересылать сообщения; учитывать разный жизненный цикл.'),
 ('Другие устройства','Локальные каналы не передают данные по сети. Нужен сервер: WebSocket, SSE или запросы.')],
 'Нужно синхронизировать тему в двух вкладках и получить результат от iframe другого origin. Выбери API для каждого случая.', 'post bc storage',kind='scenario')
t('communication','dedup','Дедупликация уведомлений между вкладками','Сообщения о «я уже показал» могут прийти слишком поздно: две вкладки успеют показать уведомление одновременно. Нужны идентичность события и координация.',[
 ('eventId','У каждого логического события должен быть стабильный ID; повторная доставка не создаёт новое событие.'),
 ('Критическая секция','Захватить именованный Web Lock, внутри прочитать общую отметку, при её отсутствии обработать и записать результат. Все участники должны соблюдать протокол.'),
 ('Срок хранения и сбои','Ограничить историю ID по TTL. Падение между записью и показом может потерять уведомление, а между показом и записью — дать повтор.'),
 ('Гарантии','BroadcastChannel сообщает об обновлениях, но не даёт атомарный lock. Для строгих гарантий и нескольких устройств нужна серверная координация и идемпотентность.')],
 'Две вкладки одновременно получили одно уведомление. Опиши протокол дедупликации и поведение при падении вкладки.', 'locks bc',kind='scenario',notion=False)
t('communication','realtime','WebSocket, SSE и long polling','Сравни направления сообщений, восстановление соединения и сложность инфраструктуры.',[
 ('WebSocket','Двусторонний канал с текстовыми и бинарными сообщениями. Reconnect, heartbeat и восстановление пропущенных событий проектируются приложением.'),
 ('SSE / EventSource','Сервер отправляет текстовый поток text/event-stream; браузерный EventSource умеет reconnect. Для возобновления сервер должен учитывать ID событий.'),
 ('Long polling','Запрос ждёт новые данные или timeout, затем клиент открывает следующий. Просто поверх HTTP, но запросы и задержки требуют контроля.')],
 'Выбери транспорт для чата, серверного прогресса задачи и системы с ограниченной инфраструктурой.', 'ws sse',kind='scenario',drill=True,
 note='Уточнение к Notion: WebSocket поддерживает бинарные сообщения, а не только строки.')

# 05. JavaScript objects.
t('javascript','map-set','Map и Set','Map хранит пары ключ–значение, Set — уникальные значения. Оба итерируются в порядке добавления; объекты сравниваются по идентичности.',[
 ('Map','Ключом может быть любое значение. set/get/has/delete/clear, size; итерация keys/values/entries.'),
 ('Set','add/has/delete/clear, size; нет доступа по числовому индексу и метода get(index). Для позиции можно явно создать массив.'),
 ('Равенство','SameValueZero: NaN совпадает с NaN, +0 с -0. Два отдельно созданных объекта — разные значения.')],
 'Чем отличаются Map и Set? Как получить третий добавленный элемент Set и почему set[2] не подходит?', 'collections',kind='compare',drill=True,notion=False)
t('javascript','weak','WeakMap и WeakSet','Слабые коллекции не удерживают объект только фактом включения в коллекцию. Это удобно для метаданных и отметок о посещении объектов.',[
 ('WeakMap','Слабые ключи: объекты и non-registered symbols. Значение доступно через живой ключ; get/set/has/delete.'),
 ('WeakSet','Слабые значения тех же допустимых видов; add/has/delete. Для отметки «этот объект обработан».'),
 ('Наблюдаемость','Нет size, перечисления элементов и clear: результат зависел бы от непредсказуемого GC. Сборка не обязана происходить сразу.')],
 'Сравни WeakMap/WeakSet с Map/Set и объясни связь со сборкой мусора.', 'collections gc',kind='compare',drill=True,notion=False)
t('javascript','gc','Сборка мусора и утечки','Главная модель — достижимость от корней: активных вызовов, глобальных объектов и других живых ссылок. Недостижимый объект может быть освобождён.',[
 ('Mark-and-sweep','Отметить достижимые объекты и освободить недостижимые. Современные движки используют поколения и инкрементальные/параллельные варианты.'),
 ('Циклы','Взаимные ссылки не мешают сборке, если весь цикл недостижим. Само число ссылок не определяет живость в этой модели.'),
 ('Утечки','Неограниченный Map-кэш, забытый listener, interval или замыкание могут удерживать данные. Помогают cleanup, лимиты и heap snapshots.')],
 'Объясни GC простыми словами: когда цикл объектов можно собрать и почему забытая подписка может удерживать память?', 'gc',kind='explain',notion=False)
t('javascript','proxy','Proxy и Reflect','Proxy — объект-посредник над target с handler. Ловушки перехватывают операции; исходный объект при прямом доступе обходит Proxy.',[
 ('get / set','Чтение и запись свойств можно логировать, валидировать или использовать для реактивности. set возвращает boolean успеха.'),
 ('has / deleteProperty / ownKeys','Перехват in, delete и перечисления ключей; обязательны инварианты объекта, например для non-configurable свойств.'),
 ('Reflect','Reflect.get/set помогают выполнить стандартную операцию с receiver. Вложенные объекты не становятся Proxy автоматически.')],
 'Объясни проксирование объекта и ограничения Proxy. Какие операции перехватят get и set?', 'proxy',kind='explain',notion=False)
t('javascript','arrays','Методы массивов','Выбирай метод по результату и мутации. Для функций сравнения и callback учитывай contract метода.',[
 ('Преобразовать','map создаёт массив результатов; filter — подходящих элементов; reduce сворачивает в аккумулятор; flatMap объединяет map и flatten на один уровень.'),
 ('Найти и проверить','find возвращает первый элемент или undefined; findIndex — индекс или -1; some/every проверяют условие; includes ищет значение.'),
 ('Изменить','push/pop/shift/unshift/splice/sort/reverse меняют исходный массив. sort без comparator сравнивает строковые представления.'),
 ('Получить копию','slice/concat не мутируют исходный массив; toSorted/toReversed/toSpliced/with дают новые массивы. Копирование поверхностное.')],
 'Назови методы для преобразования, поиска, проверки и изменения массива; какие из них мутируют исходник?', 'array',drill=True)
t('javascript','cloning','Поверхностное и глубокое копирование','Копия верхнего уровня не означает копию вложенных объектов. Выбор метода зависит от типов данных и нужного поведения.',[
 ('Spread / Object.assign','Поверхностная копия собственных enumerable свойств; вложенные объекты сохраняют ссылки.'),
 ('JSON round trip','Только JSON-совместимые данные: Date станет строкой, функции/undefined теряются или меняют представление, BigInt и циклы обычно приводят к ошибке.'),
 ('structuredClone','Поддерживает циклы, Date, Map, Set, ArrayBuffer; функции и DOM-узлы не клонирует, не сохраняет произвольные прототипы и descriptors.')],
 'Сравни spread, JSON.parse/stringify и structuredClone для объекта с Date, функцией и вложенным объектом.', 'clone',kind='compare')
t('javascript','closures','Замыкания, call/apply/bind','Функция сохраняет доступ к лексическому окружению создания. Она видит переменные окружения, а не обязательно их снимок на момент создания.',[
 ('Замыкание','Счётчик, фабрика обработчика и приватное состояние — типичные примеры; удерживаемые переменные могут удерживать память.'),
 ('call / apply','Сразу вызвать функцию с заданным this; call принимает аргументы отдельно, apply — array-like.'),
 ('bind','Создать функцию с закреплённым this и/или первыми аргументами. Стрелочная функция использует лексический this.'),
 ('Каррирование','Преобразовать f(a,b,c) в цепочку f(a)(b)(c). Отличается от частичного применения, где фиксируется часть аргументов.')],
 'Объясни замыкание на примере счётчика, затем сравни call, apply, bind и каррирование.', 'closure functions',kind='explain',drill=True)

# 06. Async.
t('async','promise-basics','Promise и async/await','Promise представляет будущий результат: pending → fulfilled либо rejected. Состояние после settlement не меняется; executor запускается синхронно.',[
 ('then / catch / finally','then создаёт новый Promise; возвращённое значение продолжает цепочку, throw отклоняет её. catch обрабатывает rejection; finally обычно пропускает прежний результат, но может заменить его ошибкой.'),
 ('async / await','async всегда возвращает Promise. await приостанавливает конкретную async-функцию, а не весь поток; продолжение выполняется асинхронно.'),
 ('Запуск и отмена','Promise сам по себе не означает отдельный поток. Комбинаторы не отменяют другие операции; fetch отменяют через AbortController.'),
 ('Дополнительные static методы','resolve и reject создают результат; withResolvers даёт promise/resolve/reject; try оборачивает синхронный или асинхронный результат вызова. Доступность проверять для целевых браузеров.')],
 'Объясни состояния Promise, цепочки и работу await. Что происходит синхронно, а что позже?', 'promise',kind='explain',drill=True)
t('async','promise-combinators','Четыре комбинатора Promise','Учебный набор: all, allSettled, any, race. Все принимают iterable; порядок массива результатов определяется порядком входа, а не временем завершения.',[
 ('Promise.all','Ждёт все fulfillment и возвращает массив значений; отклоняется при первом rejection. Пустой набор даёт fulfilled [] без ожидания, обработчик then всё равно асинхронный.'),
 ('Promise.allSettled','Ждёт settlement всех и возвращает записи status + value/reason. Rejection отдельной входной операции сам по себе не отклоняет итог.'),
 ('Promise.any','Возвращает первый fulfillment; если все rejected — AggregateError. Пустой iterable также даёт rejection с AggregateError.'),
 ('Promise.race','Повторяет первый settlement: fulfillment или rejection. Пустой iterable оставляет результат pending.')],
 'Назови все четыре комбинатора и сравни условия завершения, ошибки и пустой вход.', 'promise',kind='compare',drill=True,notion=False)
t('async','event-loop','Event loop: task и microtask','В пределах одного JS agent синхронный код выполняется до освобождения стека. После задачи на microtask checkpoint очередь microtasks обрабатывается до опустошения; затем возможны rendering и следующая task.',[
 ('Task','Например callback таймера или обработка события. Таймер задаёт минимальную задержку до готовности, а не точное время исполнения.'),
 ('Microtask','then/catch/finally и продолжение await, а также queueMicrotask. Новые microtasks в очереди выполняются в том же checkpoint.'),
 ('Rendering','Не является отдельной microtask; браузер выбирает rendering opportunities. Длинная очередь microtasks может задержать UI.')],
 'Восстанови порядок вывода A, B, C, D, E и объясни очереди.', 'loop timers',kind='order',code="console.log('A');\nsetTimeout(() => console.log('B'), 0);\nPromise.resolve().then(() => {\n  console.log('C');\n  queueMicrotask(() => console.log('D'));\n});\nconsole.log('E');",notion=True)
topics[-1]['order']=['A — синхронный код','E — синхронный код','C — реакция Promise','D — добавленная microtask','B — callback таймера']
topics[-1]['orderAnswer']='A → E → C → D → B. A и E выполняются в текущем стеке; C и добавленная из C microtask D — до следующей задачи таймера B.'
t('async','timers','setTimeout, setInterval и stale closure','Таймеры планируют будущие задачи, а не блокируют поток. Для освобождения ресурсов сохраняй ID и вызывай clearTimeout/clearInterval.',[
 ('setTimeout','Однократный callback после минимальной задержки. В background и вложенных таймерах браузер может увеличивать задержку.'),
 ('setInterval','Повторяющиеся callbacks, но не гарантия точного интервала. Для последовательных async-запросов безопаснее планировать следующий timeout после завершения.'),
 ('React и замыкание','Callback захватывает значения конкретного render. Для обновления от предыдущего state помогает functional updater; подписки требуют cleanup.')],
 'Сравни timeout и interval. Почему interval в React может видеть старый state и как это исправить?', 'timers effect',kind='compare',drill=True)
t('async','fetch-streams','Fetch и Streams','Поток позволяет обрабатывать ответ частями, не ожидая всего тела в памяти. fetch отклоняется при сетевой ошибке, но не автоматически при HTTP 404/500.',[
 ('Проверка ответа','Проверить response.ok/status и доступность body. json()/text() обычно потребляют тело целиком.'),
 ('Чтение','ReadableStream.getReader() и read() дают chunks до done. TextDecoder с stream:true или TextDecoderStream сохраняет границы многобайтных символов.'),
 ('Управление','Учитывать backpressure, ошибки и отмену через AbortController. Граница chunk не равна границе JSON-сообщения; нужен framing/буфер.')],
 'Большой текстовый ответ нужно показывать постепенно. Опиши обработку chunks, кодировки, ошибок и отмены.', 'streams',kind='scenario')

# 07. React rendering.
t('react-render','render-commit','Render, commit и жизненный цикл','Render вычисляет описание UI; commit применяет изменения. Render должен быть чистым: его можно повторить или отбросить.',[
 ('Trigger','Первый mount или update state; обновление родителя обычно инициирует render дочернего дерева.'),
 ('Render','React вызывает компоненты и сравнивает результат с предыдущим деревом. Повторный render не обязательно означает изменение DOM.'),
 ('Commit','React применяет нужные DOM-изменения и обновляет refs; layout effects привязаны к commit.'),
 ('Mount / update / unmount','У class есть componentDidMount/DidUpdate/WillUnmount. У функций эффекты описывают отдельные процессы синхронизации с cleanup, а не точную замену каждого class lifecycle.')],
 'Восстанови путь обновления React от setState до commit и объясни жизненный цикл.', 'react effect',kind='order')
t('react-render','keys-vdom','Virtual DOM, reconciliation и keys','React хранит описание дерева и сопоставляет элементы между render. Идентичность определяется типом и положением, а в списках — ключом среди siblings.',[
 ('Virtual DOM','Условное имя описания UI в памяти; не копия всего браузерного DOM и не гарантия большей скорости для любого интерфейса.'),
 ('Reconciliation','Сопоставить старое и новое дерево, сохранить подходящие instances/state и определить изменения.'),
 ('Keys','Стабильный ключ из данных помогает сохранять state за правильным элементом. Индекс при перестановках и случайный key могут привязать state неверно или перемонтировать элемент.')],
 'В списке редактируемых строк поменяли порядок. Объясни, почему key=index может перенести ввод к другой строке.', 'keys react',kind='scenario')
t('react-render','fiber','Fiber и concurrent rendering','Fiber — внутренняя структура и архитектура согласования React. Работу render можно делить, приоритизировать, прерывать и начинать заново; commit остаётся согласованным.',[
 ('Stack reconciler','Длинная синхронная обработка дерева затрудняла уступку управления браузеру.'),
 ('Fiber nodes','Единицы работы связаны с компонентами и хранят сведения о state, props и связях дерева; детали реализации не являются публичным API.'),
 ('Приоритеты','Urgent ввод и transition-обновление могут иметь разные приоритеты. Это не параллельное выполнение render в нескольких JS-потоках.'),
 ('Практическое следствие','Чистые render, корректные эффекты и useTransition/useDeferredValue помогают сохранять отзывчивость.')],
 'Объясни Fiber и concurrent rendering простыми словами: какую проблему решают и что можно прервать?', 'react hooks',kind='explain',
 note='Уточнение к Notion: «Fiber 2.0» — не отдельная официальная версия публичного API; внутренние поля и алгоритмы могут меняться.')

# 08. Effects and hooks.
t('react-effects','hooks-list','Хуки: явный учебный набор','Обычные хуки вызывают на верхнем уровне React-компонента или custom hook, в одинаковом порядке; не в условиях и обработчиках. use имеет отдельные правила.',[
 ('useState','Локальное состояние; setter планирует следующий render.'),('useReducer','Локальное состояние с явными actions и reducer.'),('useContext','Прочитать и подписаться на ближайший context.'),('useRef','Стабильный контейнер для DOM/значения; изменение current не запускает render.'),('useEffect','Синхронизировать компонент с внешней системой.'),('useLayoutEffect','Измерить или скорректировать layout до paint.'),('useMemo','Кэшировать вычисление по зависимостям; оптимизация, не семантическая гарантия.'),('useCallback','Кэшировать ссылку на функцию по зависимостям.'),('useTransition','Отметить обновление как неблокирующее и получить pending.'),('useDeferredValue','Отложить менее срочное отображение значения.'),('useId','Создать ID для accessibility, не для ключей списка.'),('useImperativeHandle','Ограничить imperative API, доступный через ref.'),('useSyncExternalStore','Подписаться на внешний store через snapshot.'),('useDebugValue','Подписать custom hook в DevTools.'),('useInsertionEffect','Специализированная интеграция CSS-in-JS библиотек.'),('useActionState','Состояние результата action и pending.'),('useOptimistic','Временное оптимистическое представление при action.'),('useEffectEvent','Вынести нереактивную логику, вызываемую из эффекта; не способ скрывать нужные зависимости.')],
 'Перечисли хуки учебного набора по группам и объясни назначение каждого.', 'hooks',drill=True,notion=False)
t('react-effects','effects-purpose','useEffect: внешние системы и cleanup','Эффект нужен для синхронизации после commit: подписки, соединения, таймеры, browser API и интеграции с внешними виджетами.',[
 ('Setup','Подписать listener, подключить канал, запустить таймер или синхронизировать imperative widget.'),
 ('Cleanup','Снять подписку, остановить таймер, закрыть соединение. Перед новым setup со сменившимися зависимостями React выполняет прежний cleanup; также при unmount.'),
 ('Что не требует эффекта','Вычисляемые данные можно получить в render, действие пользователя — в event handler. Не копировать props в state без необходимости.'),
 ('Разработка','StrictMode может выполнить дополнительный цикл setup → cleanup → setup, чтобы выявить ошибки очистки.')],
 'Для чего использовать useEffect, кроме запросов? Назови несколько внешних систем и cleanup для каждой.', 'effect',kind='explain')
t('react-effects','effect-deps','Массив зависимостей эффектов','Зависимости — все реактивные значения, которые читает setup. React сравнивает каждую позицию с предыдущей через Object.is; правила одинаковы для useEffect и useLayoutEffect.',[
 ('Без массива','Setup после каждого commit компонента, а перед следующим setup — cleanup предыдущего.'),
 ('Пустой массив []','Нет реактивных зависимостей. Mount setup и unmount cleanup; дополнительный dev-цикл StrictMode и повторный mount возможны.'),
 ('[a, b]','Перезапустить синхронизацию, когда хотя бы одно значение отличается по Object.is.'),
 ('Объект с той же ссылкой','Изменение поля не меняет identity зависимости. Сама мутация не запускает render; даже при другом render эффект с [object] не перезапустится из-за этого поля.')],
 'Сравни отсутствие массива, [] и [object]. Объясни поведение при мутации object.name без смены ссылки.', 'effect layout',kind='compare',drill=True,
 note='Уточнение к Notion: [] не означает «ровно один раз навсегда»; useLayoutEffect не делает глубокое сравнение зависимостей.')
t('react-effects','effect-timing','useEffect и useLayoutEffect','Разница — момент и влияние на paint, а не способ сравнения зависимостей.',[
 ('useLayoutEffect','Выполняется до repaint и может блокировать его. Подходит для измерения tooltip и синхронной коррекции позиции.'),
 ('useEffect','Обычно не блокирует paint; для обновлений от взаимодействий может выполняться до paint. Нельзя обещать «всегда после paint».'),
 ('Общее','Оба эффекта работают только на клиенте, требуют корректных зависимостей и cleanup. Избыточный layout effect ухудшает отзывчивость.')],
 'Tooltip сначала прыгает из неверной позиции в правильную. Какой эффект выбрать и какой у этого компромисс?', 'effect layout',kind='scenario')

# 09. State.
t('react-state','context','Context и разделение контекстов','Потребитель читает ближайший provider. Изменение value по Object.is уведомляет потребителей этого context, даже если компонент обёрнут в memo.',[
 ('Разделение','Разные контексты для независимых данных и разной частоты обновления: тема, пользователь, часто меняющийся ввод.'),
 ('Ссылка value','Новый объект {user, logout} при render может уведомить потребителей; memoization value/callback полезна после измерений.'),
 ('Границы','Context передаёт значение и подписку, но не даёт selectors по отдельным полям автоматически. Обычный render родителя тоже может вызывать дочерние render.')],
 'В один context положили theme, user и каждое нажатие клавиши. Кто обновляется и как разделить данные?', 'context',kind='scenario')
t('react-state','state-design','Организация состояния','Храни минимальный источник истины. Производные значения вычисляй; transient UI state располагай ближе к месту использования.',[
 ('Локальность','State поля ввода внутри формы не должен без причины перерисовывать всю страницу.'),
 ('Единый источник','Не дублировать одинаковые данные в нескольких state. Выбранный объект часто лучше хранить как ID.'),
 ('Композиция','Разделить часто меняющуюся и тяжёлую части; передача children иногда сохраняет стабильное поддерево.'),
 ('Server state','Удалённые данные имеют freshness, retries, cache и invalidation; это другой жизненный цикл, чем открытый dropdown.')],
 'Как организация состояния влияет на производительность? Предложи структуру для поиска и тяжёлого списка.', 'state',kind='scenario')
t('react-state','flux-redux','Flux, Redux и middleware','Однонаправленный поток делает изменения состояния явными: действие → обновление состояния → новый UI. Redux нужен при достаточной сложности общего client state.',[
 ('Action','Описание события, например itemAdded. Dispatch передаёт его в поток обработки.'),
 ('Reducer','Чистая функция previous state + action → next state. Redux Toolkit позволяет удобные записи через Immer при сохранении immutable результата.'),
 ('Store и selectors','Store хранит состояние и подписки; selectors выбирают данные для UI.'),
 ('Middleware','Перехватывает dispatch для side effects, логирования или async-логики; не помещать запросы в reducer.')],
 'Восстанови поток Redux и объясни место middleware. Какие проблемы решает общий store?', 'redux',kind='order',drill=True)
t('react-state','query-libs','RTK Query, TanStack Query, SWR и MobX','Разделяй управление server state и моделирование client state: библиотеки могут сосуществовать.',[
 ('RTK Query','Кэш запросов и mutations в экосистеме Redux Toolkit; endpoints, tags и invalidation.'),
 ('TanStack Query','Server state независимо от Redux: query keys, staleTime, retries, invalidation и mutations.'),
 ('SWR','Подход к server state с кэшем и revalidation; useSWR получает key и fetcher.'),
 ('MobX','Observable state, actions и computed; observer подписывает компонент на observables, прочитанные при render. Это не только библиотека сетевых запросов.')],
 'Сравни Redux, RTK Query, TanStack Query, SWR и MobX. Что выберешь для кэша API, а что для сложного клиентского состояния?', 'rtk query swr mobx',kind='compare',drill=True)

# 10. App.
t('react-app','forms','Controlled и uncontrolled компоненты','В controlled форме значение задаёт React state. В uncontrolled текущее значение хранится в DOM и читается через ref или FormData.',[
 ('Controlled','value/checked + onChange; удобно для взаимозависимых полей и отображения состояния.'),
 ('Uncontrolled','defaultValue/defaultChecked задают начальное значение. Подходит для простых форм и интеграций.'),
 ('Границы','Не переключать один input между controlled и uncontrolled в течение жизни. Файловый input требует чтения FileList.')],
 'Сравни controlled и uncontrolled формы и объясни разницу value/defaultValue.', 'input',kind='compare')
t('react-app','hoc-router','HOC, custom hooks и React Router','HOC принимает компонент и возвращает компонент; custom hook повторно использует stateful-логику, а Router связывает URL и UI.',[
 ('HOC','withPermissions(Component) может добавить поведение. Учитывать передачу props, refs и вложенность wrappers.'),
 ('Custom hook','usePermissions() возвращает данные/действия и явно используется компонентом. Вызовы custom hook не делят state автоматически.'),
 ('Router','Сопоставляет URL маршрутам и вложенным layouts; клиентская навигация использует History API. Современный React Router не сводится к HOC.'),
 ('SPA','Документ остаётся, приложение меняет UI при навигации; сервер должен поддерживать прямые URL. SPA может использовать SSR при первой загрузке.')],
 'Объясни различия HOC, custom hook и Router. Как работает навигация SPA без полной перезагрузки?', 'router patterns',kind='compare')
t('react-app','suspense-lazy','Suspense и lazy loading','Suspense показывает fallback, когда дочернее дерево при render приостановилось на поддерживаемом источнике.',[
 ('React.lazy','Загружает код компонента через dynamic import и работает с Suspense.'),
 ('Данные','Suspense работает с поддерживаемыми framework/data sources или use(Promise). Обычный fetch внутри useEffect сам по себе не активирует fallback.'),
 ('Ошибки','Suspense отвечает за ожидание, Error Boundary — за ошибки render/lazy. Нужны оба сценария для remote-модуля.')],
 'Почему Suspense не показывает fallback для любого fetch в useEffect? Как разделить ожидание и ошибку?', 'suspense',kind='explain')
t('react-app','react-versions','Версии React и миграции','Не приписывай себе опыт версии, которой не пользовалась. Разделяй «применяла в проекте» и «знаю из документации».',[
 ('React 18','createRoot, automatic batching, transitions и concurrent foundations; оценить StrictMode-проверки.'),
 ('React 19','Actions, useActionState, useOptimistic, use для ресурсов/context; ref как prop для function components. useFormStatus находится в react-dom.'),
 ('Миграция','Зафиксировать исходную/целевую версии, проверить зависимости и removed APIs, провести typecheck и тесты ключевых сценариев, замерить поведение.'),
 ('Рассказ','Контекст проекта → причина → изменения → проблемы → проверка результата. Если миграций не было, честно объяснить план действий.')],
 'С какими версиями React ты работала? Расскажи об опыте миграции или о том, как бы её организовала.', 'react19 upgrade hooks',kind='experience',notion=False)

# 11. TypeScript.
t('typescript','ts-basics','TypeScript, type/interface и union','TypeScript проверяет контракт до исполнения. После компиляции типы обычно удалены; входящие JSON-данные требуют runtime-проверки.',[
 ('interface','Описывает объектный контракт, поддерживает extends и declaration merging.'),
 ('type','Alias для объекта, union, tuple и других типов; использует intersections, не поддерживает declaration merging как interface.'),
 ('Union','A | B допускает значения одного из вариантов; для специфичных полей нужен narrowing. Intersection A & B требует совместить требования.'),
 ('Цена TS','Полезен для рефакторинга и IDE, но требует настройки, времени проверки и поддержки типов. Не гарантирует отсутствие runtime-ошибок.')],
 'Сравни interface и type; объясни union, intersection и границу compile-time проверки.', 'ts',kind='compare')
t('typescript','never','never и полнота обработки','never — тип невозможного значения. Появляется после исключения всех вариантов или у функции, которая не возвращает нормально.',[
 ('Функция','Функция с явным возвратом never должна бросить ошибку или не завершаться; void означает отсутствие используемого результата.'),
 ('Exhaustiveness','В default ветке discriminated union присвоение значения переменной never выявит забытый вариант.'),
 ('Union','T | never эквивалентен T. В conditional types never часто удаляет неподходящие варианты.')],
 'Для чего нужен never? Как он помогает заметить новый необработанный вариант union?', 'narrow',notion=False)
t('typescript','assertions','Аннотация, as и satisfies','Это инструменты compile-time. Ни один из них не преобразует и не валидирует произвольный JSON во время исполнения.',[
 (': Type','Задаёт объявленный тип переменной и проверяет совместимость; может скрыть конкретные свойства выведенного типа за более широким контрактом.'),
 ('as Type','Утверждение разработчика о типе; не runtime-cast. Может скрыть ошибку; двойное as unknown as особенно легко обходит проверку.'),
 ('satisfies Type','Проверяет совместимость выражения с контрактом, сохраняя полезную конкретику результирующего типа. Контекстная типизация при этом может влиять на inference.'),
 ('as const','Уточняет литералы и readonly для literal expression. Можно сочетать с satisfies; это не Object.freeze и не глубокая runtime-заморозка.')],
 'Сравни : Type, as Type, satisfies Type и as const. Почему assertion не защищает от неверного ответа API?', 'satisfies ts',kind='compare',notion=False,
 code='type Palette = Record<"red" | "green", string | [number, number, number]>;\nconst a: Palette = { red: [255, 0, 0], green: "#0f0" };\nconst b = { red: [255, 0, 0], green: "#0f0" } satisfies Palette;\n// Объясни типы a.green и b.green перед вызовом toUpperCase().')
t('typescript','narrowing','Narrowing и Type Guards','Control flow analysis уточняет возможный тип по проверкам, ветвлениям, присваиваниям и достижимости кода.',[
 ('typeof','Проверяет примитивные категории; typeof null === "object", поэтому null проверять отдельно.'),
 ('in / instanceof','in проверяет наличие свойства; instanceof — связь с prototype конструктора. Для Array использовать Array.isArray.'),
 ('Equality и truthiness','=== и !==, проверка null/undefined, ранний return. Truthiness исключает также 0, "" и false, что может быть нежелательно.'),
 ('Discriminated union','Общее literal-поле kind позволяет выбрать вариант и проверить исчерпывающий switch.'),
 ('Predicate / assertion function','isUser(x): x is User или asserts x is User. Реализация должна реально проверять контракт; ошибочный predicate может обмануть компилятор.')],
 'Перечисли встроенные способы narrowing и пользовательские Type Guards. Где truthiness теряет допустимые значения?', 'narrow',drill=True,notion=False)
t('typescript','utilities','Utility Types: явный учебный набор','Utility Types преобразуют типы во время проверки; не удаляют поля реального объекта и не меняют runtime-значения.',[
 ('Partial<T>','Делает собственные свойства T optional на один уровень.'),('Required<T>','Делает свойства обязательными на один уровень.'),('Readonly<T>','Запрещает присвоение свойств через этот тип на один уровень; не freeze.'),('Pick<T, K>','Оставляет выбранные ключи объекта.'),('Omit<T, K>','Исключает выбранные ключи объекта.'),('Record<K, V>','Объект с ключами K и значениями V.'),('Exclude<T, U>','Удаляет из union T варианты, присваиваемые U.'),('Extract<T, U>','Оставляет из union T варианты, присваиваемые U.'),('NonNullable<T>','Убирает null и undefined.'),('Parameters<F>','Tuple параметров функции.'),('ReturnType<F>','Тип результата функции.'),('Awaited<T>','Рекурсивно раскрывает promise-like результат как await.')],
 'Перечисли Utility Types учебного набора и объясни каждый на небольшом типе.', 'utility',drill=True,notion=False)
t('typescript','omit-exclude','Omit и Exclude','Omit работает с ключами объектного типа; Exclude фильтрует варианты union через distributive conditional type.',[
 ('Omit','Omit<{id:number; name:string}, "id"> даёт {name:string}. Реальный объект при этом не изменяется.'),
 ('Exclude','Exclude<"draft" | "sent" | "failed", "draft" | "failed"> даёт "sent".'),
 ('Распределение','Для Exclude<T,U> каждый вариант T проверяется отдельно: T extends U ? never : T. Обычный Omit над union не обязан сохранить все variant-specific поля.')],
 'Чем Omit отличается от Exclude? Выведи результаты примеров и объясни распределение Exclude по union.', 'utility',kind='compare',notion=False)
t('typescript','generics-variance','Generics и variance','Generic сохраняет связь между входными и выходными типами. Variance описывает, как совместимость контейнеров/функций связана с совместимостью типов внутри.',[
 ('Generic constraint','T extends {id:string} ограничивает допустимый T, но сохраняет его конкретику. Это не то же самое, что заменить T широким базовым типом.'),
 ('Covariance','Производитель результата Dog может использоваться там, где нужен результат Animal.'),
 ('Contravariance','Обработчик любого Animal можно использовать там, где передают Dog; обратное опасно. Проверка зависит от strictFunctionTypes и формы объявления.'),
 ('Invariance / bivariance','Чтение и запись T могут требовать invariance. Некоторые method parameters допускают bivariance для совместимости; это компромисс soundness.')],
 'Объясни generics и сравни covariance, contravariance, invariance и bivariance на Animal/Dog.', 'generics',kind='compare',drill=True,notion=False)

# 12. Performance.
t('performance','react-performance','Оптимизация React по измерениям','Сначала воспроизвести проблему и измерить, затем менять конкретную причину. Количество render само по себе не равно стоимости.',[
 ('Диагностика','React DevTools Profiler показывает commits и стоимость компонентов; browser Performance — long tasks, layout, paint и взаимодействия.'),
 ('Меньше работы','Локализовать state, разделить context, убрать лишние effects, виртуализировать большие списки.'),
 ('Memoization','memo пропускает некоторые parent-driven render при стабильных props; useMemo/useCallback помогают сохранять результаты/ссылки. Собственные state/context updates всё равно работают.'),
 ('Приоритеты','Transitions/deferred values помогают отложить несрочный UI, но не уменьшают вычислительную сложность сами по себе.')],
 'Ввод тормозит при фильтрации большого списка. Как выявить причину, выбрать улучшение и проверить результат?', 'profiler memo state',kind='scenario')
t('performance','vitals','Core Web Vitals','Оценивают загрузку, отзывчивость и стабильность. Полевые данные описывают реальных пользователей; лабораторный прогон помогает диагностировать.',[
 ('LCP','Largest Contentful Paint: хороший ориентир ≤ 2.5 секунды. Проверить TTFB, discovery и загрузку главного изображения/текста.'),
 ('INP','Interaction to Next Paint: ≤ 200 мс. Проверить длинные задачи, обработчики и стоимость следующего render.'),
 ('CLS','Cumulative Layout Shift: ≤ 0.1. Резервировать место под изображения, рекламу и динамические блоки.'),
 ('Оценка','Порог оценивают на 75-м перцентиле, отдельно по mobile/desktop; не выдавать единичный Lighthouse-прогон за полевой результат.')],
 'Назови все три Core Web Vitals, что они измеряют и что улучшать при плохом значении каждого.', 'vitals',drill=True,notion=False)
t('performance','bundle','Bundle и загрузка ресурсов','Bundle — результат упаковки зависимостей приложения. Важны не только байты, но и parse/execute, кеширование и порядок обнаружения ресурсов.',[
 ('Code splitting','Разделить по маршрутам или тяжёлым функциям через import(); не дробить вслепую на множество маленьких запросов.'),
 ('Tree shaking','Удаление неиспользуемых exports при подходящей структуре modules и sideEffects; minification — отдельное преобразование.'),
 ('Compression и caching','Brotli/gzip уменьшают передачу; content-hash filenames помогают долгому кэшированию.'),
 ('Preload / prefetch / lazy','Preload для критичного текущего ресурса, prefetch для вероятного будущего; lazy для некритичного. Не делать LCP-изображение ленивым.')],
 'Bundle вырос вдвое. Какие измерения и меры выберешь до добавления memo во все компоненты?', 'splitting images',kind='scenario',drill=True)
t('performance','build-tools','Compiler, transpiler и bundler','Названия описывают функции, а конкретный инструмент может совмещать несколько.',[
 ('Compiler / transpiler','Преобразовать исходный код: TS/JSX, синтаксис, оптимизации. Удаление TS-аннотаций не обязательно означает typecheck.'),
 ('Bundler','Построить dependency graph, собрать chunks, обработать assets, code splitting и plugins.'),
 ('Семейства','Webpack/Rspack, Rollup/Rolldown, esbuild и Turbopack — инструменты со своими возможностями и совместимостью; выбирать по проекту, не только по языку реализации.'),
 ('Monorepo tools','Nx управляет графом проектов, задачами и кэшем; не является прямой заменой bundler. .mjs — явный ESM в Node, .js зависит от окружения/package type, .ts требует TS-tooling.')],
 'Сравни compiler/transpiler и bundler. Где в сборке TS происходит проверка типов?', 'splitting ts',kind='compare')
t('performance','observability','Ошибки, traces, metrics и dashboards','Разные сигналы отвечают на разные вопросы; не отправлять секреты и лишние персональные данные в telemetry.',[
 ('OpenTelemetry','Инструментация и передача traces/metrics/logs; span описывает операцию, trace связывает их через context propagation.'),
 ('Sentry','Ошибки, stack traces, breadcrumbs, releases и инструменты performance; source maps помогают связать production stack с исходниками.'),
 ('Prometheus','Сбор и хранение временных рядов метрик; важно контролировать cardinality labels.'),
 ('Grafana','Визуализация и alerting по подключённым источникам данных; не заменяет instrumentation.')],
 'Сопоставь OpenTelemetry, Sentry, Prometheus и Grafana с задачами расследования ошибки и медленного запроса.', 'otel sentry prometheus grafana',kind='match',drill=True)

# 13. Rendering and SEO.
t('rendering','render-strategies','CSR, SSR, SSG, ISR и hybrid','Разделяй момент получения HTML и момент интерактивности. Серверный HTML не отменяет клиентский JavaScript автоматически.',[
 ('CSR','Основной UI строится в браузере после JS. Подходит для интерактивных закрытых приложений; учитывать стартовую загрузку.'),
 ('SSR','HTML формируется для запроса на сервере; помогает первому контенту, но добавляет серверную стоимость и требует продуманного кеширования.'),
 ('SSG','HTML формируется заранее при сборке; хорошо кэшируется, но обновление данных требует обновления результата.'),
 ('ISR','Предварительный результат обновляется позже по времени или invalidation, поведение зависит от framework.'),
 ('Hybrid / dynamic','Разные маршруты/части используют разные стратегии. Dynamic rendering в framework-контексте — генерация на запрос; независимые fetch можно запускать параллельно, а не создавать waterfall.')],
 'Сравни CSR, SSR, SSG и ISR для личного кабинета, статьи и каталога. Что значит hybrid?', 'render isr',kind='compare',drill=True)
t('rendering','hydration','Hydration, streaming и universal app','Hydration подключает React к уже отданному серверному HTML, сохраняя его как начальный UI.',[
 ('Совпадение','Первый client render должен соответствовать серверному: Date.now, случайные числа, locale и browser-only данные могут создать mismatch.'),
 ('Streaming','Сервер может отдавать HTML частями, а Suspense обозначает границы ожидания. Это не то же самое, что fetch-stream в браузере.'),
 ('Universal / isomorphic','Часть кода может работать и на сервере, и в браузере; window/document на сервере недоступны.'),
 ('Server Components','Компоненты выполняются в серверной среде и не отправляют свой исполняемый код клиенту. Это отдельная модель, сочетаемая с SSR и client components.')],
 'Объясни hydration и причины mismatch. Чем universal app отличается от доступа к window в любом компоненте?', 'hydrate render',kind='explain')
t('rendering','seo','SEO: доступность содержания поисковику','Поисковик должен обнаружить URL, получить содержимое, понять его и выбрать каноническую версию. SSR не гарантирует высокий ranking.',[
 ('Процесс','Crawling → обработка/rendering при необходимости → indexing → ranking; отдельные стадии могут повторяться.'),
 ('Структура','Semantic HTML, понятные headings, title, description, доступные ссылки и alt. viewport относится к отображению на устройствах.'),
 ('Управление URL','robots.txt управляет crawling, не надёжным удалением из индекса; noindex управляет indexing; canonical — сигнал предпочтительного URL, sitemap помогает discovery.'),
 ('Дополнения','Structured data описывает сущности; Open Graph задаёт social preview; скорость и доступность полезны пользователям и поиску.')],
 'Публичный каталог плохо индексируется. Какие проверки проведёшь до смены rendering strategy?', 'seo',kind='scenario')

# 14. HTML/CSS.
t('html-css','specificity','Каскад и специфичность CSS','Специфичность сравнивается внутри соответствующих ступеней каскада: origin, importance, layers и другие правила учитываются раньше.',[
 ('ID / class / type','Три столбца специфичности: ID; classes/attributes/pseudo-classes; elements/pseudo-elements. Сравнение лексикографическое, не сумма десятичных очков.'),
 (':where / :is / :not / :has',':where имеет нулевую специфичность; у остальных учитывается наиболее специфичный аргумент, а не дополнительная «цена» самой функции.'),
 ('Равенство','При прочих равных побеждает более позднее правило; !important — ступень каскада, а не «самая большая специфичность».')],
 'Сравни #app .item, .panel .item:hover и :where(#app) .item. Почему важен не только подсчёт селекторов?', 'css',kind='compare')
t('html-css','styling','Подходы к стилям и дизайн-система','Выбор зависит от изоляции, динамики, SSR, веса и правил команды.',[
 ('Обычный CSS / BEM','Небольшой runtime overhead; дисциплина имён и границы модулей поддерживаются договорённостями.'),
 ('CSS Modules','Локальные имена classes на этапе сборки; значения по-прежнему подчиняются каскаду.'),
 ('CSS-in-JS','Стили рядом с компонентом; runtime и compile-time реализации имеют разные затраты и SSR-требования.'),
 ('Sass / Less / Stylus','Препроцессоры преобразуют расширенный синтаксис в CSS; Sass не SaaS.'),
 ('Дизайн-система','Компоненты, tokens, accessibility и правила использования. UI-библиотека вроде Carbon реализует часть системы, но не заменяет продуктовые решения.')],
 'Сравни CSS Modules, CSS-in-JS и обычный CSS для большого SSR-приложения.', 'css',kind='compare')
t('html-css','scripts','Загрузка скриптов: classic, async, defer, module','Загрузка и исполнение — разные стадии. Модель ниже относится к parser-inserted scripts.',[
 ('Classic без атрибутов','Внешний script блокирует HTML parsing на загрузку и выполнение.'),
 ('async','Загрузка параллельна parsing; исполнение — как только готов, порядок между скриптами не гарантирован.'),
 ('defer','Для внешнего classic script: загрузка параллельно, исполнение после parsing в порядке документа, до DOMContentLoaded.'),
 ('type=module','По умолчанию имеет defer-подобное поведение, использует module graph; async меняет момент исполнения. defer для module не нужен.')],
 'Выбери атрибуты для независимой аналитики и двух зависимых скриптов; объясни порядок исполнения.', 'script',kind='scenario',drill=True)
t('html-css','images','Оптимизация изображений','Изображение должно соответствовать размеру отображения, плотности экрана, содержанию и приоритету загрузки.',[
 ('Формат и сжатие','AVIF/WebP часто полезны для raster; JPEG для фото и PNG для некоторых lossless-задач остаются вариантами. SVG — для подходящей векторной графики.'),
 ('Responsive','srcset + sizes выбирают размер; picture выбирает формат или art direction. Не отправлять огромный desktop asset на маленький экран.'),
 ('Стабильность','width/height или aspect-ratio резервируют место и уменьшают CLS.'),
 ('Приоритет','loading=lazy для внеэкранных изображений; LCP обычно eager и при необходимости fetchpriority=high. alt описывает смысл, декоративным изображениям — пустой alt.')],
 'Главное фото долго появляется, а карточки прыгают. Предложи изменения для LCP и CLS.', 'images vitals',kind='scenario')
t('html-css','svg','SVG: сильные стороны и ограничения','SVG описывает векторную графику. Подходит для иконок и схем, но не заменяет автоматически фотографии.',[
 ('Преимущества','Масштабирование без потери чёткости, редактируемый текстовый формат, CSS/анимации при подходящем способе встраивания.'),
 ('Стоимость','Сложный path/большое DOM-дерево могут быть тяжелее raster. SVG не гарантированно меньше PNG.'),
 ('Безопасность и доступность','Недоверенный inline SVG требует sanitization. Для img важен alt, для inline — подходящее accessible name; внешнее img не даёт CSS-доступ ко внутренним paths.')],
 'Выбери SVG или raster для логотипа, фото и сложной карты. Объясни ограничения.', 'svg',kind='scenario')
t('html-css','internationalization','i18n и l10n','i18n подготавливает приложение к разным языкам/регионам, l10n адаптирует его под конкретный locale.',[
 ('i18n','Вынести сообщения, поддержать plurals/interpolation, форматирование чисел/дат и направление письма.'),
 ('l10n','Перевод, выбор формулировок, региональных форматов и культурных особенностей.'),
 ('Практические границы','Intl форматирует даты и числа; locale не равен timezone. Избегать склеивания фраз и предположения об одинаковой длине текста.')],
 'Сравни i18n и l10n на примере даты, цены и сообщения о количестве товаров.', 'i18n',kind='compare')

# 15. Principles and architecture.
t('architecture','solid','SOLID: все пять принципов','SOLID помогает обсуждать ответственность и зависимости. Во frontend принципы применяются с учётом компонентов и функций, без обязательного создания классов.',[
 ('S — Single Responsibility','Одна связная ответственность / причина изменения. Отделить отображение от сложной работы с транспортом.'),
 ('O — Open/Closed','Расширять поведение через устойчивую точку расширения; например composable children вместо растущего switch по всем типам кнопок.'),
 ('L — Liskov Substitution','Реализация должна сохранять обещанный контракт. Замена не должна неожиданно усиливать требования или нарушать ожидаемое поведение.'),
 ('I — Interface Segregation','Небольшие интерфейсы под потребителей. Компоненту не нужен весь огромный user store ради имени.'),
 ('D — Dependency Inversion','Высокоуровневая логика зависит от абстракции, а не конкретного HTTP-клиента. Передать функцию загрузки через интерфейс/параметр.')],
 'Назови все пять букв SOLID, расшифруй и объясни каждую с примером frontend.', 'solid patterns',drill=True,notion=False)
t('architecture','kiss-dry-yagni','KISS, DRY и YAGNI','Принципы помогают выбирать минимально достаточное решение, а не заменяют анализ задачи.',[
 ('KISS — Keep It Simple','Выбирать понятную структуру без лишних уровней; простота оценивается по пониманию и сопровождению, не только числу строк.'),
 ('DRY — Don’t Repeat Yourself','Не дублировать знание и правила. Внешне похожие строки с разными причинами изменения не всегда стоит объединять.'),
 ('YAGNI — You Aren’t Gonna Need It','Не строить предполагаемые возможности без текущей потребности. Нужные тестируемость и качество не считаются лишней функциональностью.')],
 'Сравни KISS, DRY и YAGNI. Когда обобщение двух похожих компонентов создаёт лишнюю сложность?', 'yagni patterns',kind='compare',drill=True,notion=False,
 note='YAGNI добавлен как дополнительная тема автора обратной связи, а не как исходный вопрос интервьюера.')
t('architecture','design-patterns','Паттерны: учебный набор','Паттерн — повторяемый способ организации решения со своими условиями и ценой. На собесе полезно назвать задачу, применение и компромисс.',[
 ('Observer','Подписчики реагируют на события/изменения. Browser listeners и store subscriptions; нужны unsubscribe и контроль жизненного цикла.'),
 ('Strategy','Взаимозаменяемый алгоритм за одним контрактом, например разные правила сортировки/валидации.'),
 ('Adapter','Привести внешнее API к контракту приложения, изолировать различия.'),
 ('Factory','Сосредоточить создание объекта/клиента, когда варианты зависят от конфигурации.'),
 ('Command','Описать действие как значение/объект для очереди, истории или undo; обратимость нужно проектировать.'),
 ('Composition / compound components','Собирать UI из частей; совместное состояние может передаваться через Context. HOC и custom hooks — варианты повторного использования поведения.')],
 'Назови паттерны учебного набора, задачу каждого и пример из frontend.', 'patterns',drill=True,notion=False)
t('architecture','architecture-boundaries','Границы приложения и системное проектирование','Начинать с требований и данных, затем выбирать границы модулей, API и поведение при сбоях.',[
 ('Модули / MVC','Модуль скрывает детали за понятным интерфейсом. MVC разделяет model, view и controller; React сам по себе не задаёт полную архитектуру приложения.'),
 ('Monorepo / multirepo','Способ хранения исходников, не способ исполнения. Monorepo упрощает согласованные изменения; нужны граф задач и ownership.'),
 ('Микрофронтенды','Независимые части UI могут иметь собственные команды и deployment. Цена: интеграция, общий UX, зависимости, маршрутизация и observability.'),
 ('RADIO','Requirements → Architecture → Data model → Interface definition → Optimizations. Обсудить accessibility, security, performance, cache и failure states.')],
 'Спроектируй frontend поиска: уточни требования, назови модули и API, затем объясни компромиссы.', 'radio mf',kind='interview')
t('architecture','module-federation','Module Federation','Механизм обмена модулями между сборками во время выполнения. Микрофронтенды возможны и без него.',[
 ('Host / remote','Host потребляет exposed modules remote; remote entry/runtime описывает загрузку.'),
 ('Shared','Разделять совместимые зависимости, часто React как singleton. Выбор версий зависит от конфигурации и порядка инициализации; singleton не гарантирует совместимость.'),
 ('Надёжность','Загрузка remote может упасть. Нужны fallback, Error Boundary, timeout/повтор и совместимый контракт.'),
 ('Build-time / runtime','npm-пакет обычно попадает в сборку host; remote может обновляться независимо, что требует контроля совместимости.')],
 'Объясни Module Federation и поведение приложения, если remote недоступен или принёс другую копию React.', 'mf',kind='interview')

# Extra detail found in the source and verified against primary documentation.
S['react192']=('React 19.2','https://react.dev/blog/2025/10/01/react-19-2')
S['react193']=('React 19.3','https://react.dev/blog/2026/09/09/react-19-3')
S['fsd']=('Feature-Sliced Design','https://feature-sliced.design/docs/get-started/overview')
S['atomic']=('Brad Frost: Atomic Design','https://atomicdesign.bradfrost.com/chapter-2/')
S['httpversions']=('MDN: evolution of HTTP','https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Evolution_of_HTTP')
S['pagination']=('Slack Engineering: API pagination','https://slack.engineering/evolving-api-pagination-at-slack/')
S['vite']=('Vite: features','https://vite.dev/guide/features')
byid={x['id']:x for x in topics}
byid['pagination']['sources']=['pagination']
byid['build-tools']['sources']+=['vite']
byid['react-versions']['items'][2:2]=[
 dict(name='React 19.2',detail='Activity сохраняет state скрытого дерева с остановкой effects; useEffectEvent отделяет нереактивную логику эффекта; Performance Tracks помогают профилированию.'),
 dict(name='React 19.3',detail='Стабильные ViewTransition и Fragment Refs; browser() и интеграция Trusted Types. Обзор сверён 10 ноября 2026; доступность проверять для проекта.')]
byid['react-versions']['sources']+=['react192','react193']
byid['react-versions']['drill']=True
byid['react-versions']['items'][-2]['detail']+=' Для 18 → 19 официальный guide рекомендует сначала 18.3 с предупреждениями о несовместимостях.'
byid['arrays']['items']=[dict(name=n,detail=d) for n,d in [
 ('map','Новый массив результатов callback; не изменяет исходный массив сам по себе.'),('filter','Новый массив элементов, прошедших predicate.'),('reduce','Один аккумулятор, обход слева направо; initialValue особенно важен для пустого массива.'),('reduceRight','Свёртка справа налево.'),('flatMap','Преобразование с объединением на один уровень.'),('find','Первый подходящий элемент или undefined.'),('findIndex','Индекс первого подходящего элемента или -1.'),('includes','Наличие значения по SameValueZero; возвращает boolean.'),('indexOf / lastIndexOf','Первый / последний индекс значения по строгому равенству или -1; NaN таким способом не находится.'),('some / every','Хотя бы один / все удовлетворяют условию; для пустого массива false / true.'),('push / pop','Добавить в конец / убрать с конца; мутируют; возвращают новую длину / удалённый элемент.'),('shift / unshift','Убрать в начале / добавить в начало; мутируют; возвращают элемент / новую длину.'),('splice','Изменяет массив: удалить/вставить; возвращает удалённые элементы.'),('sort / reverse','Сортирует / переворачивает на месте. sort без comparator сравнивает строковые представления.'),('fill','Заполняет диапазон одним значением и мутирует массив; объект будет одной общей ссылкой.'),('slice / concat','Копия диапазона / объединение без мутации; копирование поверхностное.'),('join','Строка из элементов с разделителем.'),('toSorted / toReversed / toSpliced / with','Новые массивы без соответствующей мутации исходника; with заменяет значение по индексу.')]]
t('http','http-versions','HTTP/1.1, HTTP/2 и HTTP/3','Семантика методов и статусов сохраняется; меняются передача, соединения и работа с потоками.',[
 ('HTTP/1.1','Текстовые сообщения и persistent connections; браузеры часто открывают несколько TCP-соединений. Pipelining имеет ограничения и head-of-line blocking.'),
 ('HTTP/2','Бинарные frames, multiplexing потоков в одном соединении, HPACK для headers. Потеря TCP-пакета может задержать все потоки соединения.'),
 ('HTTP/3','QUIC поверх UDP, встроенный TLS и независимые потоки транспорта, QPACK. Не использует TCP; потери всё равно могут влиять на congestion control.')],
 'Сравни все три версии HTTP: transport, multiplexing, headers и head-of-line blocking.', 'httpversions',kind='compare',drill=True,
 note='Уточнение к Notion: HTTP/1.1 умеет persistent connections; формулировка «одно соединение на запрос» неверна.')
t('architecture','architecture-methods','Модульность, Atomic Design и FSD','Организация папок должна отражать границы ответственности и правила зависимостей. Нет единственной обязательной структуры для всех React-проектов.',[
 ('Модульность','Модуль скрывает внутреннее устройство. Группировка по типам файлов — только один вариант; feature-модули тоже модульны.'),
 ('Atomic Design','Atoms → molecules → organisms → templates → pages. Полезная модель композиции дизайн-системы, но не обязательные папки.'),
 ('Feature-Sliced Design','Слои и slices по доменам/сценариям: shared, entities, features, widgets, pages, app. Контролировать public API и направление зависимостей.')],
 'Сравни Atomic Design, FSD и группировку по типам файлов. Для чего подходит каждый подход?', 'fsd atomic',kind='compare',drill=True)
t('react-app','experience-story','История из опыта','Выбери настоящий эпизод. Не нужно придумывать миграцию или паттерн: можно рассказать о диагностике, форме или архитектурном решении.',[
 ('Контекст и задача','Какой продукт, твоя роль, ограничения и наблюдаемая проблема.'),
 ('Выбор решения','Какие альтернативы рассматривала и почему выбрала конкретную.'),
 ('Действия и проверка','Что сделала лично, как проверила корректность и результат.'),
 ('Итог и вывод','Назови известный результат без придуманных процентов; что бы изменила сейчас.')],
 'Расскажи о реальном решении технической проблемы: контекст, альтернативы, твои действия, проверка и вывод.', 'upgrade profiler',kind='experience',notion=False)

byid={x['id']:x for x in topics}
byid['pipeline']['order']=['DOM и CSSOM','Вычисление стилей / render tree','Layout','Paint','Compositing']
byid['render-commit']['order']=['Trigger','Render','Commit']
byid['flux-redux']['order']=['Dispatch action','Middleware','Reducer вычисляет next state','Store сохраняет state и уведомляет подписчиков','Selectors и UI читают новое состояние']
byid['assertions']['answerExtra']='В примере a.green имеет string | [number, number, number], поэтому перед toUpperCase нужен narrowing. b.green остаётся string и позволяет вызвать toUpperCase сразу.'

# Questions from the chat are recorded verbatim for coverage; UI wording avoids yes/no.
CHAT = {
 'JavaScript и браузерные API': [
 ('promise-combinators','Какие есть методы Promise: all, any, allSettled, race? Чем они отличаются?'),
 ('workers','Что такое Web Workers и Service Workers? Для чего они нужны?'),
 ('broadcast','Что такое BroadcastChannel и как его использовать?'),
 ('cross-context','Как синхронизировать данные между несколькими вкладками или iframe?'),
 ('dedup','Как дедуплицировать события между вкладками, например при получении уведомления?'),
 ('map-set','Чем отличаются Map и Set? Есть ли у Set индексы?'),
 ('weak','Для чего нужны WeakMap и WeakSet? Как они связаны со сборкой мусора?'),
 ('gc','Как работает сборщик мусора в JavaScript?'),
 ('proxy','Что такое Proxy? Как работает проксирование объектов?')],
 'React':[
 ('react-versions','С какими версиями React ты работала?'),('react-versions','Был ли опыт перехода между версиями?'),
 ('react-versions','Какие новые возможности React знаешь?'),('hooks-list','Какие хуки знаешь и для чего они нужны?'),
 ('context','Как работают контексты? Когда стоит разделять данные на несколько контекстов?'),
 ('effects-purpose','Для чего использовать useEffect, кроме выполнения запросов?'),
 ('effect-deps','Как работает массив зависимостей у useEffect и useLayoutEffect?'),
 ('effect-deps','Что произойдёт, если не указать массив зависимостей?'),
 ('effect-deps','Что означает пустой массив зависимостей?'),
 ('effect-deps','Как React сравнивает зависимости?'),
 ('effect-deps','Сработает ли useLayoutEffect, если изменить свойство объекта в зависимостях, сохранив ссылку на объект?'),
 ('react-performance','Какие способы оптимизации React-приложений знаешь?'),
 ('react-performance','Как выявлять проблемы производительности?'),('state-design','Как организация состояния влияет на производительность?')],
 'TypeScript':[
 ('never','Для чего нужен тип never?'),('assertions','Какие подводные камни есть у приведения типов — cast / type assertion?'),
 ('utilities','Какие Utility Types знаешь и для чего они нужны?'),('omit-exclude','Чем отличаются Omit и Exclude?'),
 ('omit-exclude','Как Exclude работает с union-типами?'),('narrowing','Что такое Type Guard?'),
 ('narrowing','Какие бывают способы сужения типов?'),('narrowing','Какие встроенные проверки TypeScript использует для сужения типов?'),
 ('assertions','Для чего нужен satisfies и чем он отличается от : Type и as Type?')],
 'Принципы и паттерны':[
 ('kiss-dry-yagni','Какие принципы разработки знаешь?'),('solid','Что означает каждая буква в SOLID?'),
 ('kiss-dry-yagni','Что означают KISS и DRY?'),('design-patterns','Какие паттерны проектирования знаешь? Где их применяла?')]
}

def answer_for(topic):
    if topic['kind']=='experience':
        return 'Здесь нет универсального биографического ответа. Назови только свой реальный опыт. Если такого опыта не было — скажи об этом и объясни подход. '+ ' '.join(i['name']+': '+i['detail'] for i in topic['items'])
    return topic.get('orderAnswer') or (topic['summary']+'\n\n'+'\n\n'.join(i['name']+': '+i['detail'] for i in topic['items'])+ ('\n\n'+topic['answerExtra'] if topic.get('answerExtra') else ''))

questions=[]
for topic in topics:
    q=dict(id=topic['id']+'-main',topic=topic['id'],lesson=topic['lesson'],kind=topic['kind'],prompt=topic['question'],answer=answer_for(topic),check=[i['name'] for i in topic['items']],followups=[f'Приведи пример: {topic["items"][0]["name"]}.',f'Какие ограничения важно помнить: {topic["title"]}?'])
    if topic.get('order'): q['order']=topic['order']
    if topic['kind']=='match': q['pairs']=topic['items']
    if topic.get('code'): q['code']=topic['code']
    questions.append(q)
    if topic['drill']:
        for n,item in enumerate(topic['items']):
            questions.append(dict(id=f'{topic["id"]}-item-{n+1}',topic=topic['id'],lesson=topic['lesson'],kind='recall',prompt=f'Объясни «{item["name"]}» в теме «{topic["title"]}». Приведи пример и назови важное ограничение.',answer=item['detail'],check=[item['name'],item['detail']],followups=[f'Чем этот пункт отличается от других в теме «{topic["title"]}»?']))

registry=[]
for group,entries in CHAT.items():
    for n,(tid,prompt) in enumerate(entries,1):
        topic=byid[tid]; qid=f'chat-{list(CHAT).index(group)+1}-{n}'
        ui=prompt
        if 'Есть ли у Set' in ui: ui='Чем отличаются Map и Set? Объясни, как получить элемент Set по позиции и какие ограничения у этого подхода.'
        if ui.startswith('Был ли опыт'): ui='Расскажи об опыте перехода между версиями React; если его не было, объясни план такой миграции.'
        if ui.startswith('Сработает ли'): ui='Объясни поведение useLayoutEffect с [obj], если изменить obj.name, сохранив ссылку. Что меняется при отсутствии нового render?'
        kind='experience' if ('работала' in ui or 'опыте перехода' in ui or 'Где их применяла' in ui) else 'recall'
        questions.append(dict(id=qid,topic=tid,lesson=topic['lesson'],kind=kind,prompt=ui,answer=answer_for(topic),check=[i['name'] for i in topic['items']],followups=[f'Объясни конкретный пример из темы «{topic["title"]}».', 'Какое ограничение или компромисс здесь важно учитывать?']))
        registry.append(dict(origin='Чат · '+group,title=prompt,topic=tid,lesson=topic['lesson'],question=qid,status='included'))

# Each main source heading maps to a concrete topic; subheadings inherit its section.
M = {
 'Why Redux?':'flux-redux','FLUX':'flux-redux','SEO quick recap':'seo','SSL сертификат':'tls',
 'Что происходит перед рендерингом?':'navigation','Фазы рендеринга страницы':'pipeline',
 'Что входит в запрос к серверу? REST':'rest','REST (Representational State Transfer)':'rest','Head requests':'caching',
 'Что может быть в заголовках HEAD-ответа':'caching','304':'caching','Options request':'cors','CORS':'cors',
 'HTTP Requests Answers':'statuses','OpenTelemetry, Sentry, Prometheus, and Grafana':'observability','Vulnerabilities':'vulnerabilities',
 'Typescript':'ts-basics','React':'render-commit','Архитектура':'architecture-methods','What is gRPC?':'api-styles',
 'Что такое HTTP запрос? Чем от отличается от HTTPS?':'message','Как создается HTTP-запрос?':'navigation',
 'CDN and why we need it':'cdn','Cookie. Какие аттрибуты?':'cookies','Array Methods':'arrays','Set, Map, WeakSet, WeakMap':'map-set',
 'React Fiber':'fiber','Service Worker vs Web worker':'workers','Concurrent rendering':'fiber','Cookies':'cookies',
 'useEffect vs useLayoutEffect':'effect-timing','React Suspense':'suspense-lazy','Lazy Loading':'suspense-lazy',
 'React hydration':'hydration','Redux / RTK Query / Tanstack Query / SWR':'query-libs','CSS Specificity':'specificity',
 'HOC in React':'hoc-router','Object cloning/copying in JS':'cloning','Bundle Optimizations':'bundle',
 'Rollup/ Rolldown / ESbuild /  Webpack / Rspack':'build-tools','Compiler/Transpiler ≠ Bundler:':'build-tools',
 'i18n VS l10n':'internationalization','IndexedDB':'web-storage','Controlled/Uncontrolled components':'forms',
 'React Keys':'keys-vdom','Virtual DOM':'keys-vdom','Fiber 2.0':'fiber','The Problem It Solved: The Old "Stack" Reconciler':'fiber',
 'Core Features of React Fiber':'fiber','How Fiber Works Under the Hood':'fiber','Why should you care?':'fiber',
 'SSE':'realtime','WebSocket':'realtime','Long Polling':'realtime',
 'Как использовать Fetch API и Streams для обработки больших объемов данных?':'fetch-streams','Что такое React Router?':'hoc-router',
 'Что такое Cookie и для чего они используются?':'cookies','Что такое SPA?':'hoc-router',
 'В чем разница передачи данных через query-параметры и body запроса?':'message',
 'Что такое setTimeout и setInterval?':'timers','В чем разница между интерфейсом (interface) и типом (type) в TypeScript?':'ts-basics',
 'В чем отличие между microtask queue и task queue?':'event-loop','Что такое замыкания в JavaScript и для чего они нужны':'closures',
 'Что такое промисы в JavaScript и как они работают':'promise-basics','Ассоциации из жизни':'promise-combinators',
 'Как различить похожие пары':'promise-combinators','Где это встречается на практике':'promise-combinators',
 'Жизненный цикл реакт компонентов':'render-commit','useEffect / useLayoutEffect':'effect-timing',
 'Опиши процесс от ввода адреса сайта в браузере до отображения страницы':'navigation',
 'Способы хранения данных в браузере:':'web-storage','Load JS scripts: async / defer':'scripts','REST:rest':'rest',
 'Различия между HTTP/1.1 и HTTP/2:':'http-versions','🍪 Cookies':'cookies','Images optimization':'images',
 'SVG. Best (and worst) parts':'svg','GraphQL':'api-styles','gRPC':'api-styles','Cross-context communication in the browser':'cross-context',
 'One question sorts them: who is talking to whom?':'cross-context','What they have in common':'cross-context',
 'Each one in a line or two':'cross-context','Picking one':'cross-context',
 'Dashboard':'suspense-lazy','The biggest wins are usually:':'bundle','{translate("welcome_back", { name })}':'internationalization',
}
excluded={'Реляционные базы данных','Database joins ???','Elasticsearch','Inverted vs Forward index'}
parent=None
source=json.loads((ROOT/'source-headings.json').read_text(encoding='utf-8'))
for i,h in enumerate(source['headings']):
    title=h['title']
    if title in excluded:
        parent=None; registry.append(dict(origin='Notion',title=title,status='excluded',reason='Исключено пользователем: базы данных и инструменты'));continue
    tid=M.get(title)
    if not tid and h['level']>=3 and parent is None:
        registry.append(dict(origin='Notion',title=title,status='excluded',reason='Подраздел исключённой темы'));continue
    if not tid and h['level']>=3: tid=parent
    if not tid:
        raise ValueError('Unmapped Notion heading: '+title)
    parent=tid
    registry.append(dict(origin='Notion',title=title,status='included',topic=tid,lesson=byid[tid]['lesson'],question=tid+'-main'))

# Relevant study labels before the first heading, including empty TODO study topics.
early={
 'Idempotency':'methods','offset based or cursor based pagination':'pagination','mobx':'query-libs','Isomorphic web apps':'hydration',
 'useEffect cleanup function':'effects-purpose','call, apply, bind':'closures','async/await, promises in React code':'promise-basics',
 'Context, who rerenders and when?':'context','Core web vitals':'vitals','SOLID principles and examples from FE':'solid',
 'patterns and examples from React':'design-patterns','GENERICS':'generics-variance','React 19 hooks':'hooks-list',
 'Cache API':'web-storage','Reflow, repaint, composite':'pipeline','Как реализована авторизация?':'auth',
 'What is NX + Turbopack':'build-tools','extensions: ts, js, mjs':'build-tools','saas, less, stylus':'styling','Carbon UI lib':'styling',
 'Module Federation':'module-federation','Understanding variance in TS':'generics-variance','MVC':'architecture-boundaries','RADIO Framework':'architecture-boundaries',
 'CSS in JS and compare other css approaches':'styling','Handlebars templates VS component-based templating systems':'hoc-router',
 'Ad hoc тестирование':'react-performance','i18n':'internationalization','Compiler / Transpiler':'build-tools'}
for label,tid in early.items():
    registry.append(dict(origin='Notion · учебный список',title=label,status='included',topic=tid,lesson=byid[tid]['lesson'],question=tid+'-main'))
for label in ['Личные TODO и вакансии','Реляционные БД, нормализация, joins и индексы БД','Redis, Kafka, Elasticsearch, ClickHouse','Backend-фреймворки, ORM и прочие инструменты исключённого раздела','Codegen / Orval, CASL как отдельная библиотека, nuqs / qs, Nivo / amCharts, CodeGraph, npm-пакеты, ERD / UML / Excalidraw']:
    registry.append(dict(origin='Notion · исключения',title=label,status='excluded',reason='Исключённый раздел / вне согласованного набора уроков'))

# Fill two small source labels rather than merely claiming coverage.
byid['hoc-router']['items'].append(dict(name='Шаблоны и компоненты',detail='Handlebars подставляет данные в текстовый HTML-шаблон. React-компонент объединяет описание UI с композиционной моделью, state и обновлениями; оба подхода могут генерировать HTML на сервере.'))
byid['react-performance']['items'].append(dict(name='Ad hoc проверка',detail='Свободное исследование поведения без фиксированного тест-кейса полезно для поиска неожиданностей, но не заменяет воспроизводимый benchmark или regression test.'))
# Regenerate the main answers affected by these additions.
for topic in [byid['hoc-router'],byid['react-performance']]:
    for q in questions:
        if q['topic']==topic['id'] and '-item-' not in q['id']:
            q['answer']=answer_for(topic);q['check']=[i['name'] for i in topic['items']]

for q in questions:
    q['sources']=byid[q['topic']]['sources']
    q['notion']=byid[q['topic']]['notion'] or any(r.get('topic')==q['topic'] and r['origin']=='Notion' for r in registry)

FOLLOWUPS={
 'navigation':['Какие этапы исчезнут при переиспользовании соединения и свежем кэше?','Что меняется при HTTP/3?'],
 'pipeline':['Чем reflow отличается от repaint?','Почему transform иногда дешевле изменения left?'],
 'cdn':['Как защитить приватный ответ от общего кэша?','Что произойдёт при cache miss?'],
 'message':['Где могут остаться query-параметры после HTTPS-запроса?','Как меняется представление сообщения в HTTP/2?'],
 'methods':['Почему второй DELETE может вернуть 404, сохранив идемпотентность?','Как сделать повторный POST безопасным для бизнес-операции?'],
 'caching':['Чем no-cache отличается от no-store?','Как браузер использует ETag для получения 304?'],
 'rest':['Почему JSON по HTTP ещё не доказывает соблюдение REST?','Что означает stateless для запроса с токеном?'],
 'api-styles':['Какие ограничения native gRPC есть в браузере?','Как контролировать сложность GraphQL-запросов?'],
 'pagination':['Что произойдёт при вставке записи перед текущим offset?','Зачем cursor стабильный порядок с уникальным tie-breaker?'],
 'tls':['Что именно проверяет браузер в сертификате?','От каких ошибок приложения TLS не защищает?'],
 'cors':['Как preflight влияет на отправку основного запроса?','Почему CORS не заменяет защиту от CSRF?'],
 'cookies':['Чем HttpOnly отличается от Secure?','Почему SameSite=None требует Secure?'],
 'web-storage':['Чем Cache API отличается от HTTP-кэша?','Как отличается scope sessionStorage и localStorage?'],
 'auth':['Где нужно проверять права на конкретный ресурс?','Почему JWT не означает автоматическую безопасность хранения?'],
 'workers':['Почему Service Worker нельзя использовать как вечный in-memory store?','Как worker сообщает результат странице без DOM?'],
 'broadcast':['Как новая вкладка получает состояние, если история сообщений не хранится?','Что меняет storage partition для iframe?'],
 'cross-context':['Что проверять при получении postMessage от iframe?','Какой контекст получает storage event, а какой нет?'],
 'dedup':['Почему getItem → setItem не является блокировкой?','Что произойдёт при падении между показом уведомления и записью eventId?'],
 'realtime':['Как клиент восстанавливает события после reconnect?','Когда однонаправленный SSE проще WebSocket?'],
 'map-set':['Как Set сравнит два отдельно созданных объекта?','Почему порядок итерации не означает наличие индексов?'],
 'weak':['Почему у WeakMap нет size и keys()?','Когда обычный Map удержит объект в памяти?'],
 'gc':['Что делает недостижимый цикл объектов?','Как искать объект, удерживаемый забытым listener?'],
 'proxy':['Что произойдёт при доступе напрямую к target?','Почему Proxy не становится глубоким автоматически?'],
 'cloning':['Что произойдёт с Date и функцией при JSON round trip?','Какие ограничения у structuredClone?'],
 'closures':['Замыкание хранит снимок значения или доступ к переменной?','Как bind отличается от немедленного вызова call?'],
 'promise-basics':['Когда запускается executor нового Promise?','Как исключение в then влияет на следующий Promise?'],
 'promise-combinators':['Как поведёт себя каждый комбинатор на пустом iterable?','Почему завершение race не отменяет проигравший fetch?'],
 'event-loop':['Где окажется microtask, добавленная из другой microtask?','Как длинная очередь microtasks влияет на paint?'],
 'timers':['Почему delay=0 не означает немедленный вызов?','Как cleanup и functional updater помогают React-таймеру?'],
 'fetch-streams':['Почему chunk нельзя считать целым JSON-сообщением?','Как отменить загрузку и не сломать декодирование UTF-8?'],
 'render-commit':['Почему повторный render может не изменить DOM?','Почему побочный эффект внутри render опасен?'],
 'keys-vdom':['Как key влияет на сохранение state строки?','Что меняется при случайном key на каждом render?'],
 'fiber':['Как urgent update может обойти transition?','Чем concurrent rendering отличается от многопоточности?'],
 'effect-deps':['Что произойдёт с [obj] при той же ссылке, но новом поле?','Почему [] не означает один запуск навсегда?'],
 'effects-purpose':['Как проверить симметрию setup и cleanup?','Какие вычисления стоит оставить в render вместо эффекта?'],
 'effect-timing':['Почему useLayoutEffect может ухудшать отзывчивость?','Почему нельзя обещать, что useEffect всегда выполнится после paint?'],
 'context':['Как memo взаимодействует с обновлением context?','Как разделить часто и редко меняющиеся данные?'],
 'state-design':['Какой state можно заменить вычисляемым значением?','Почему перенос ввода ближе к форме уменьшает область обновления?'],
 'flux-redux':['Почему запрос нельзя выполнять в reducer?','Где middleware находится относительно dispatch и reducer?'],
 'forms':['Чем defaultValue отличается от value?','Как прочитать uncontrolled input при отправке формы?'],
 'suspense-lazy':['Почему обычный fetch в effect не активирует Suspense?','Какая граница обрабатывает ошибку lazy-загрузки?'],
 'react-versions':['Какая часть ответа — твой опыт, а какая — знание документации?','Как проверишь совместимость зависимостей и изменение поведения после обновления?'],
 'never':['Как never помогает проверить исчерпывающий switch?','Чем never отличается от void?'],
 'assertions':['Какой тип у a.green и b.green в примере?','Почему as const не замораживает объект во время исполнения?'],
 'narrowing':['Что не так с typeof null?','Какие допустимые значения отсекает truthiness?'],
 'omit-exclude':['Почему Exclude не удаляет поле внутри объекта?','Как T extends U ? never : T фильтрует члены union?'],
 'generics-variance':['В каком направлении совместимы Consumer<Animal> и Consumer<Dog>?','Почему method declaration может отличаться от function property при strictFunctionTypes?'],
 'react-performance':['Как измеришь результат до и после изменения?','Какие обновления memo не блокирует?'],
 'vitals':['Какая метрика отражает прыжки layout?','Почему одного лабораторного прогона мало для оценки реальных пользователей?'],
 'bundle':['Как отличить вес передачи от затрат выполнения JS?','Какие ресурсы не стоит загружать лениво?'],
 'render-strategies':['Когда статическая генерация не подходит изменению данных?','Как SSR сочетается с клиентской интерактивностью?'],
 'hydration':['Как случайные числа создают mismatch?','Почему server component и SSR — разные понятия?'],
 'solid':['Покажи нарушение одного из пяти принципов во frontend.','Какое расширение оправдано сейчас, а какое нарушает YAGNI?'],
 'design-patterns':['Какой паттерн ты действительно применяла и для какой задачи?','Какова цена этого решения и что было бы проще без него?'],
 'module-federation':['Что делать с несовместимой общей зависимостью?','Как сохранить остальное приложение при отказе remote?']
}
for q in questions:
    if q['topic'] in FOLLOWUPS:q['followups']=FOLLOWUPS[q['topic']]
    if q['kind']=='experience' and byid[q['topic']]['kind']!='experience':
        q['answer']='Опирайся только на свой опыт: контекст → задача → альтернативы → твои действия → проверка → результат. Если такого опыта не было, скажи об этом и объясни подход.\n\nТеоретические ориентиры:\n'+q['answer']

assert set(EXPLANATIONS)==set(byid), 'Every topic needs its own complete explanation'
for topic in topics:
    topic['explanation']=EXPLANATIONS[topic['id']]
data=dict(version=1,title='Практика собеседований',date='2026-11-11',notion=NOTION,sources={k:dict(title=v[0],url=v[1]) for k,v in S.items()},lessons=[dict(id=id,number=n,title=title,subtitle=sub,topics=[x['id'] for x in topics if x['lesson']==id]) for n,(id,title,sub) in enumerate(LESSONS,1)],topics=topics,questions=questions,coverage=registry)

def esc(v): return html.escape(str(v),quote=True)
def static_topic(x):
    src=' · '.join(f'<a href="{esc(S[k][1])}">{esc(S[k][0])}</a>' for k in x['sources'])
    z=x['explanation']
    code=z['code'] or x['code']
    walkthrough='<ol>'+''.join(f'<li>{esc(line)}</li>' for line in z['walkthrough'])+'</ol>' if z['walkthrough'] else ''
    sample=f'<div class="worked-example"><h3>Разберём на примере</h3><p>{esc(z["example"])}</p>'+(f'<pre><code>{esc(code)}</code></pre>' if code else '')+walkthrough+'</div>'
    terms='<details class="topic-reference"'+(' open' if x['drill'] else '')+'><summary>Термины и элементы темы</summary><dl>'+''.join(f'<dt>{esc(i["name"])}</dt><dd>{esc(i["detail"])}</dd>' for i in x['items'])+'</dl></details>'
    return f'<section class="theory" id="{x["id"]}"><h2>{esc(x["title"])}</h2><p class="explanation-context">{esc(z["context"])}</p><h3>Как это работает — по шагам</h3><ol class="explanation-steps">'+''.join(f'<li>{esc(step)}</li>' for step in z['steps'])+f'</ol>{sample}{terms}<div class="interview-takeaway"><h3>Коротко для собеседования</h3><p>{esc(z["takeaway"])}</p></div><p>{esc(x["note"])}</p><p class="sources">{src}</p></section>'

def write_page(name,title,view,content,lesson=''):
    page=f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>{esc(title)} · Собеседование</title><link rel="stylesheet" href="style.css"></head>
<body data-view="{view}" data-lesson="{lesson}"><a class="skip" href="#main">К содержимому</a><div id="storage-warning" role="status" hidden></div><div id="app"><header class="static-header"><a href="index.html">← Все уроки</a><h1>{esc(title)}</h1></header><main id="main">{content}</main></div><div id="toast" role="status" aria-live="polite"></div><script src="data.js"></script><script src="app.js"></script></body></html>'''
    (ROOT/name).write_text(page,encoding='utf-8')

if __name__=='__main__':
    (ROOT/'data.js').write_text('window.STUDY_DATA = '+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    (ROOT/'coverage.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')
    listing='<p>Объяснения по шагам, разобранные примеры, вопросы без подсказок и смешанное повторение. Включите JavaScript для упражнений и сохранения прогресса.</p><ol>'+''.join(f'<li><a href="lesson-{l["number"]:02d}.html">{esc(l["title"])}</a></li>' for l in data['lessons'])+'</ol><p><a href="review.html">Повторение</a> · <a href="interview.html">Мини-собеседование</a> · <a href="coverage.html">Реестр тем</a></p>'
    write_page('index.html','Твоя подготовка','home',listing)
    for l in data['lessons']:
        write_page(f'lesson-{l["number"]:02d}.html',l['title'],'lesson',''.join(static_topic(byid[id]) for id in l['topics']),l['id'])
    write_page('review.html','Повторение','review','<p>Повторение вопросов по теме и самооценке доступно с JavaScript.</p>')
    write_page('interview.html','Мини-собеседование','interview','<p>Десять смешанных вопросов с уточнениями. Включите JavaScript.</p>')
    write_page('coverage.html','Реестр тем','coverage','<p>Машиночитаемый реестр: <a href="coverage.json">coverage.json</a>.</p>')
    write_page('progress.html','Твой прогресс','progress','<p>Экспорт и импорт прогресса доступны с JavaScript.</p>')
    print(json.dumps(dict(lessons=len(LESSONS),topics=len(topics),questions=len(questions),coverage=len(registry)),ensure_ascii=False))

