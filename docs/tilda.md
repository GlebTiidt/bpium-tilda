# Документация по API Tilda

## Общие сведения

- Базовый URL: `https://api.tildacdn.info`.
- Все запросы выполняются методом GET и возвращают JSON.
- Параметры авторизации: `publickey`, `secretkey`.
- Ограничение: 150 запросов в час. API нельзя вызывать на каждый визит пользователя — синхронизируем данные и храним у себя.
- Уведомление о публикации (webhook) отправляется методом GET с параметрами `pageid`, `projectid`, `published`, `publickey`. Ожидаемый ответ сервера — `ok` в течение 5 секунд.
- API доступно только подписчикам Business‑плана Tilda.

## Основные методы

| Метод | Описание |
| --- | --- |
| `/v1/getprojectslist` | Список проектов |
| `/v1/getprojectinfo` | Информация о проекте (можно добавить `webconfig=htaccess` или `nginx`) |
| `/v1/getpageslist` | Список страниц проекта |
| `/v1/getpage` | Информация о странице + body‑HTML |
| `/v1/getpagefull` | Информация о странице + полный HTML |
| `/v1/getpageexport` | Информация для экспорта + body‑HTML, списки файлов |
| `/v1/getpagefullexport` | Информация для экспорта + полный HTML, списки файлов |

Каждый запрос дополняется `projectid` или `pageid`, если это требуется.

---

## Маппинг данных (Bpium → Tilda)

- `{{course_title}}` в карточках курсов (Tilda) ← `record.title` из каталога `Интеграция` (Bpium catalogId `16`, поле «Название курса», API ID `1`).

### Скрипт обновления названия курса

- Путь: `scripts/update_course_title.py`.
- Загружает `.env.local` (переменные `BPIUM_DOMAIN`, `BPIUM_EMAIL`, `BPIUM_PASSWORD`), подтягивает записи каталога 16 и берёт поле `title`.
- Пример команды:

```bash
python3 scripts/update_course_title.py tilda/homepage-section.html --copy
```

- Плейсхолдер `{{course_title}}` в HTML заменяется фактическим названием курса (по умолчанию берётся первая запись; можно указать `--record-id`).

### Серверный API для динамической подстановки

- Backend на FastAPI (`app/main.py`) запускается командой:

```bash
uvicorn app.main:app --reload
```

- Для доступа со стороны Тильды необходимо настроить CORS:
  - В `.env.local` добавляем `CORS_ALLOW_ORIGINS=https://example.tilda.ws,https://example.com` (список доменов через запятую).
  - FastAPI автоматически подхватывает переменную и разрешает запросы только с указанных доменов.
- Доступные маршруты:
  - `GET /api/courses` — список всех курсов с нормализованными полями.
  - `GET /api/courses/latest?record_id=<ID>` — курс по умолчанию или конкретный с указанным `record_id`.
- Endpoint использует кэш TTL (`CACHE_TTL_SECONDS`, по умолчанию 300 секунд), чтобы снизить нагрузку на Bpium.
- На стороне Tilda достаточно выполнить `fetch('https://<наш-домен>/api/courses/latest')` и подставить `data.title` в плейсхолдер `{{course_title}}`.
- JSON структура ответа `/api/courses/latest`:

```json
{
  "id": "1",
  "title": "Самый лучший курс",
  "hours": 76.0,
  "start_date": "13 ноября",
  "status": "1",
  "current_price": 75000.0,
  "first_raise_date": "2025-11-11T11:00:00.000Z",
  "first_raise_price": 80000.0,
  "second_raise_date": "2025-11-25T11:00:00.000Z",
  "second_raise_price": 100000.0,
  "installment_price": null,
  "doc": "Сертификат",
  "course_type": "Вебинар",
  "practice_types": "Практика",
  "is_course_of_month": false
}
```

- Фронтовый скрипт в Tilda (пример):

```html
<script>
fetch('https://<наш-сервер>/api/courses/latest')
  .then(res => res.json())
  .then(data => {
    document.querySelector('[data-course-title]').textContent = data.title;
    // дополнительные поля аналогично
  })
  .catch(err => console.error('Course load failed', err));
</script>
```

## Структуры ответов (главное)

### Список проектов

```json
{
  "status": "FOUND",
  "result": [
    { "id": "0", "title": "First Project", "descr": "Some info" },
    { "id": "1", "title": "Second Project", "descr": "" }
  ]
}
```

### Информация о проекте

```json
{
  "status": "FOUND",
  "result": {
    "id": "0",
    "title": "Project title",
    "customdomain": "project.com",
    "export_csspath": "",
    "export_jspath": "",
    "export_imgpath": "",
    "indexpageid": "0",
    "customcsstext": "y",
    "favicon": "",
    "page404id": "0",
    "images": [{ "from": "", "to": "" }]
  }
}
```

### Список страниц

```json
{
  "status": "FOUND",
  "result": [
    {
      "id": "1001",
      "projectid": "0",
      "title": "Page title first",
      "published": "1419702868",
      "filename": "page1001.html"
    }
  ]
}
```

### getpage / getpagefull

`getpage` возвращает `html` с body‑кодом, плюс массивы `js` и `css`.  
`getpagefull` возвращает полный HTML страницы.

### getpageexport / getpagefullexport

- Содержат массивы `images`, `js`, `css` с полями `from`, `to`, `attrs`, чтобы сохранять файлы локально.
- `html` содержит код с локальными путями, готовый к размещению на сервере.
- Рекомендуется скачивать и обновлять статические файлы при каждом экспорте.
- В экспортированных страницах необходимо сохранять идентификатор «Made on Tilda» с ссылкой на https://tilda.cc.

## Типовой сценарий экспорта проекта

1. В настройках проекта (Site Settings → Export) задать пути `export_imgpath`, `export_jspath`, `export_csspath` (например `/images`, `/js`, `/css`).
2. Получить `projectid` нужного проекта.
3. Создать серверный скрипт, который:
   - отправляет запросы к API,
   - создаёт директории и файлы (изображения, CSS, JS),
   - сохраняет HTML страниц.
4. Вызвать `getprojectinfo`, обработать массив `images` и сохранить общие файлы.
5. При необходимости использовать `webconfig=htaccess|nginx` для получения примера конфигурации сервера.
6. Запросить `getpageslist` и пройтись по списку страниц:
   - вызвать `getpagefullexport` (или `getpageexport`, если нужен только `<body>`),
   - сохранить файлы из массивов `images`, `js`, `css`,
   - записать `html` в файл с именем `filename`.

### Интеграция в шаблон без копирования статических файлов

Если нагрузка невелика, можно использовать `getpage`, который возвращает только body‑HTML. Тогда изображения и другие файлы останутся на серверах Tilda, но необходимо самостоятельно подключить списки `js` и `css`, возвращаемые в ответе.

## Пример простого запроса на PHP

```php
$result = file_get_contents('https://api.tildacdn.info/v1/getprojectinfo/?publickey=00000000000000000000&secretkey=00000000000000000000&projectid=0');
$project = json_decode($result, true);
print_r($project);
```
