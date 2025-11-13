# Документация по интеграции Bpium

## Методы интеграции

Интеграции расширяют возможности решения за счёт объединения нескольких программ.

### Виды интеграций

- **На уровне данных** — другие системы работают с данными в Бипиуме.
- **На уровне интерфейса** — функции других продуктов встраиваются в Бипиум.

### Интеграции на уровне данных

Типовые задачи:

- импорт и синхронизация данных с другими системами;
- приём и сохранение заявок с сайта, почты или мессенджеров;
- генерация документов и отчётов;
- запуск действий в других системах при наступлении событий;
- синхронизация учётных записей.

Инструменты: API, бизнес‑процессы, вебхуки.

Подробнее: https://docs.bpium.ru/integrations/integration/data

### Интеграции на уровне интерфейса

Типовые задачи:

- отображение форм Бипиума в сторонних системах и на сайтах;
- дополнительные кнопки‑действия внутри Бипиума;
- встроенные функциональные модули сторонних продуктов.

Инструменты: веб‑формы, веб‑расширения.

Подробнее: https://docs.bpium.ru/integrations/integration/client

## API Bpium

- REST‑подход, формат JSON.
- Относительный адрес: `/api/v1/{ресурс}/{?ID-объекта}`
- Облачный адрес: `https://{вашдомен}.bpium.ru/api/v1/{ресурс}/{?ID-объекта}`

### Базовые ресурсы данных

- **Каталоги (Catalogs)** — структура каталогов. https://docs.bpium.ru/integrations/api/data/catalogs
- **Записи (Records)** — записи каталога. https://docs.bpium.ru/integrations/api/data/records
- **Связи (Relations)** — ссылки на запись. https://docs.bpium.ru/integrations/api/data/relations-relations
- **История (Histories)** — изменения записи. https://docs.bpium.ru/integrations/api/data/istoriya-history
- **Файлы (Files)** — файловое хранилище. https://docs.bpium.ru/integrations/api/data/files
- **Отделы (Sections)** — группы каталогов. https://docs.bpium.ru/integrations/api/data/sections
- **Виды (Views)** — виды каталога. https://docs.bpium.ru/integrations/api/data/views

### Агрегация и отчётность

- **Values** — разложение по полю с подсчётом значений. https://docs.bpium.ru/integrations/api/agregate/values
- **Totals** — сводные значения. https://docs.bpium.ru/integrations/api/agregate/totals
- **Дашборды (Boards)** — экраны с графиками. https://docs.bpium.ru/integrations/api/reports/boards
- **Виджеты (Widgets)** — значения графика. https://docs.bpium.ru/reports/widgets

### Поиск и справочники

- **AvailableRecords** — записи для выбора в связанных полях. https://docs.bpium.ru/integrations/api/search/availablerecords
- **Users** — сотрудники системы. https://docs.bpium.ru/integrations/api/search/polzovateli-users
- **AvailableFilterRecords** — записи для условий фильтра. https://docs.bpium.ru/integrations/api/search/availablerecords-1
- **Contacts** — поиск по контактам. https://docs.bpium.ru/integrations/api/search/polzovateli-users-1

### Права и события

- **Rights** — правила доступа. https://docs.bpium.ru/integrations/api/prava-rights
- **Changes** — live‑события для запуска сценариев редактирования.

### Системные ресурсы

- **Profile /me** — текущий пользователь.
- **Company / Companies** — информация о компании и списке доступных компаний.
- **License** — данные лицензии.

### CRUD‑методы

- GET — коллекция или ресурс.
- POST — создание.
- PATCH — изменение.
- DELETE — удаление.

### Формат запросов

- JSON/UTF‑8.
- Заголовок: `Content-Type: application/json`.

### Авторизация

1. **Basic auth** — `Authorization: Basic base64(login:password)`. Сервер выдаёт cookie (по умолчанию `connect.sid`) для ускорения последующих запросов.
2. **POST `/auth/login`** — параметры `email`, `password`, далее тоже рекомендуется использовать cookie.
3. **Сессионная cookie** — передача через заголовок `cookie: connect.sid=...`.

### Часовой пояс

Сервер хранит даты в UTC. Для корректных выборок передаётся параметр `timezoneOffset` в минутах (например, `180` для UTC+3): `...?timezoneOffset=180`.

### Коды ошибок

400, 401, 402, 403, 404, 405, 426, 429, 500, 501 — см. официальное описание для интерпретации.

### Лимиты запросов

- Облако: 100 запросов / 30 секунд для пользователя, 500 / 30 секунд для IP.
- Enterprise: настраиваемые параметры `LIMIT_*`.
  
При превышении лимита — ответ `429 Too Many Requests`.

### Пример запроса (PHP)

```php
$domen = 'ВАШДОМЕН.bpium.ru';
$user = 'abc@mail.ru';
$pass = 'mypass';
$catalog_id = 13;

$values = [];
$values['2'] = '';
$values['3'] = ['1'];
$values['4'] = 17;
$values['5'] = date('Y-m-d') . "T" . date('H:i:s') . "+04:00";

$data = ['values' => $values];
$data_json = json_encode($data);

$ch = curl_init("https://$domen/api/v1/catalogs/$catalog_id/records");
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
curl_setopt($ch, CURLOPT_POSTFIELDS, $data_json);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
curl_setopt($ch, CURLOPT_USERPWD, "$user:$pass");
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'Content-Length: ' . strlen($data_json)
]);
$result = curl_exec($ch);
```

## Архитектура

### Структура решений

- **Bpium** — сервер бизнес-логики и API.
- **Bpium S3** — файловое хранилище (встроенное или внешнее S3).
- **Bpium BPM** — движок бизнес‑процессов.
- Внешние зависимости: PostgreSQL (БД), Redis (очередь/состояние процессов), опционально веб‑сервер/балансировщик.
- Клиенты: веб‑приложение администратора/сотрудников и мобильное приложение.

Приложения кроссплатформенные (Windows, Linux, Alpine, macOS) и могут запускаться как обычные сервисы, Docker-контейнеры, процессы под PM2 и т. п.

### Одиносерверный вариант

Все компоненты (Bpium, S3, BPM, PostgreSQL, Redis) могут работать на одном выделенном/виртуальном сервере. Требуется обеспечить публичные адреса для Bpium и Bpium S3.

### Многосервисная и многосерверная схемы

- Сервисы можно разнести по разным узлам для отказоустойчивости и повышения производительности.
- Bpium BPM и Bpium должны иметь взаимный доступ по внешним адресам, аналогично Bpium ↔ Bpium S3.
- Redis используется для хранения состояний процессов; PostgreSQL реплицируется стандартными средствами.
- Bpium S3 экземпляры должны иметь общую папку/шару для файлов.

### Каналы взаимодействия

- Bpium → PostgreSQL (5432), Redis (через BPM), S3 (2020), BPM (2030), вебхуки/внешние API, *.bpium.ru (лицензии/обновления).
- BPM ↔ Bpium, BPM ↔ S3, BPM ↔ Redis, BPM → внешние сервисы (HTTP/SQL компоненты).
- S3, PostgreSQL, Redis — принимают подключения из доверенной внутренней сети. При необходимости узлы ставятся за балансировщиками/маршрутизаторами.

## Требования к инфраструктуре

### Сервер приложения Bpium

- CPU: ≥2 ГГц (рекомендовано i5/i7 3+ ГГц), 2 ядра.
- RAM: ≥2 ГБ (рекомендовано от 4 ГБ).
- Диск: ≥10 ГБ свободно.
- Сеть: 100 Мбит/с, периодический доступ в интернет (лицензии).
- ОС: Windows, macOS, Linux.
- Для телефонии: внешний IP, домен, HTTPS‑сертификат.

### Сервер PostgreSQL

- CPU: ≥2 ГГц (желательно 4 ядра и выше).
- RAM: ≥2 ГБ (рекомендуется 8 ГБ).
- Диск: ≥10 ГБ.
- Версия PostgreSQL ≥9.4 (предпочтительно ≥9.6; 15+ пока не поддерживается).
- На Windows сервер запускается как служба, требуется резервное копирование.

### Bpium S3

- CPU: ≥2 ГГц (желательно 2+ ядра i3/i5).
- RAM: ≥2 ГБ (рекомендуется 4 ГБ).
- Диск: 10 ГБ + место под файлы.
- Сеть: 100 Мбит/с, опциональный интернет‑доступ, HTTPS требует внешний IP/домен/сертификат.

### Bpium BPM

- CPU: ≥3 ГГц (желательно 4+ ядра i5/i7).
- RAM: 8 ГБ.
- Диск: 20 ГБ.
- Сеть: 100 Мбит/с.

### Redis

- CPU: ≥1 ГГц, RAM: ≥2 ГБ, диск: ≥10 ГБ.
- Может работать на той же машине, что и BPM.

### Рабочие места

- Браузер: актуальный Google Chrome.
- CPU: ≥2 ГГц (рекомендуется i3/i5 4 ядра), RAM: ≥4 ГБ (лучше 8 ГБ), 100 Мбит/с сеть, OS Windows/Linux/macOS.

## Установка как службы

### Состав дистрибутива

- Для каждой роли (Bpium, Bpium S3, Bpium BPM) предоставляются бинарники под Windows/Linux, скрипты `*-setup` для инициализации БД, шаблоны `config-example.env`, инсталляторы служб (`*-install-service.*`, `nssm.exe` для Windows).

### Подготовка сервера

- Настроить доменное имя (если нужно обращение по HTTPS).
- Получить сертификаты (Class 1+, для мультидоменной версии — wildcard Class 2+). Рекомендуется Let's Encrypt.
- Открыть порты в firewall в соответствии с ролями (HTTP/HTTPS, 2020 для S3, 2030 для BPM, 5432 для PostgreSQL, 6379 для Redis и т. д.).

### PostgreSQL

1. Установить PostgreSQL ≥9.4 (желательно ≥9.6).
2. Задать пароль суперпользователя `postgres`, порт (обычно 5432), локаль `ru_RU` для поддержки кириллицы.
3. Создать пустую БД через pgAdmin (или использовать выгруженную из облака).

### Redis

1. Установить актуальную версию (для Windows — MSI из MicrosoftArchive).
2. Настроить автозапуск службы.

### Развёртывание Bpium

1. Распаковать архив в каталог без кириллицы и с разрешениями на запись.
2. Сконфигурировать `config.env` (обязательные параметры подключения к PostgreSQL, Redis, S3, BPM и серийный номер).
3. Выполнить `bpium-setup` для создания схемы БД.
4. Зарегистрировать службу:
   - Windows: `bpium-server-install-service.bat` (от имени администратора).
   - Linux: supervisor/systemd с простым стартовым скриптом (`./bpium`).
5. Убедиться, что служба запущена и включен автозапуск.

### Развёртывание Bpium S3

- Аналогичные шаги: распаковка, настройка `config.env`, опционально создание симлинка на отдельное хранилище, регистрация службы (`bpium-s3-install-service.bat`, supervisor/systemd).

### Развёртывание Bpium BPM

- Требуется Redis.
- Распаковка, настройка `config.env` (хост очереди Redis, токены, адрес Bpium), регистрация службы (`bpium-bpm-install-service.bat` или скрипты supervisor/systemd).

### Проверка

1. Открыть указанный в `config.env` хост Bpium в браузере.
2. Войти под `admin` / `admin`, убедиться в загрузке рабочего стола.

## Установка через Docker

- Состав контейнеров: `bpiumdocker/bpium`, `bpiumdocker/bpm`, `bpiumdocker/s3`, `postgres:14-alpine`, `redis:alpine`.
- Контейнеры объединяются в общую сеть, каждому подключаются тома (`storagebpium`, `postgresstorage`, `redisstorage`) для персистентных данных.
- Все сервисы могут жить на одном хосте или быть разнесены по нескольким — потребуются дополнительные настройки сети и переменных окружения.

### Пример docker-compose

```yaml
version: "3.8"
services:
  bpium:
    image: bpiumdocker/bpium
    ports: ["80:80", "443:443"]
    environment:
      SERIAL_NUMBER: ""
      DB_CONNECTION_STRING: "postgres://postgres:password@postgres:5432/bpium_database"
      S3_HOST: "external-host"
      BPM_HOST: "bpm"
    depends_on: [postgres, bpm, bpium-s3]
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: bpium_database
      POSTGRES_INITDB_ARGS: "--locale=ru_RU"
    volumes: ["postgresstorage:/postgresdb"]
  bpm:
    image: bpiumdocker/bpm
    environment:
      BPM_QUEUE_HOST: redis
  bpium-s3:
    image: bpiumdocker/s3
    ports: ["2020:2020"]
    volumes: ["storagebpium:/bpiumpac/storage"]
  redis:
    image: redis:alpine
    command: ["--appendonly", "yes", "--appendfilename", "redisdb.aof"]
    volumes: ["redisstorage:/data"]
volumes:
  storagebpium:
  postgresstorage:
  redisstorage:
```

### Дополнительные сведения

- SSL: положить `cert`/`cert-key` рядом с `docker-compose.yml` либо переопределить пути в секции `secrets`.
- Конфигурация хранится в переменных окружения контейнеров (см. справку по `config.env`).
- Persist storage: использовать Docker volumes, список см. `docker volume ls`.
- Запуск: `docker-compose up -d`; обновление — `docker pull ...` и повторный `docker-compose up -d`.
- Логи: `docker logs <container>`.
- Бэкап PostgreSQL:
  - `docker exec -i postgres pg_dump ... > /path/bpium_dump`
  - Восстановление через `pg_restore`.

## Мультидоменная среда

- Требуется лицензия на мультидомен и wildcard‑сертификат Class 2+.
- В `config.env` Bpium нужно задать `BPIUM_USE_SUB_DOMAINS=true`, указать домен (`BPIUM_HOST`), пути к сертификатам и настройки SMTP.
- После перезапуска главный домен доступен по `admin.<домен>`.
- Для добавления компаний:
  1. Создать группу компаний по умолчанию в каталоге «Компании».
  2. Отправить приглашение через `POST http://admin.<домен>/auth/createInvite` (Basic auth, тело с именем/email/компанией/телефоном).
  3. Получатель создаёт компанию по ссылке из письма; адрес формата `<company>.<домен>`.
- Каждая компания лицензируется отдельно — серийный номер вносится в запись компании.

## Материалы

- TLS/SSL сертификаты: `/deployment/extra/tls-ssl-sertifikat.md`
- Параметры `config.env`: общие + разделы для Bpium, S3, BPM.
- Запуск, обслуживание, активация, обновление, бэкапы, whitelabel, удаление.
- Перенос базы из облака, частые проблемы — см. соответствующие статьи в документации.

---

## Каталоги (Catalogs)

### Список каталогов

- `GET {domain}/api/v1/catalogs?sectionId={sectionId}`
- Параметры: `sectionId` — фильтр по отделу.
- Ответ: массив объектов с `id`, `sectionId`, `icon`, `name`, `fieldPrivilegeCodes`.

### Получить каталог

- `GET {domain}/api/v1/catalogs/{catalogId}{?fields}`
- Параметры: `catalogId`, опционально `fields` (JSON-массив идентификаторов полей, доступно с API 1.9.1).
- Ответ: описание каталога, права (`privilegeCode`, `fieldPrivilegeCodes`), массив `fields` с конфигурацией.

### Создать каталог

- `POST {domain}/api/v1/catalogs/`
- Тело: `name`, `icon`, `sectionId`, массив `fields` с описанием каждого поля.
- Ответ: `id` созданного каталога + `values`.
- Иконки берутся из справочника http://okcss.dev.oktell.ru/#/elements/icons.

### Изменить каталог

- `PATCH {domain}/api/v1/catalogs/{catalogId}`
- Тело: обновляемые свойства и массив полей. Для сохранения существующего поля нужно передать его `id`; отсутствующие поля будут удалены; без `id` создаётся новое поле.
- Ответ: `200 OK`.

### Удалить каталог

- `DELETE {domain}/api/v1/catalogs/{catalogId}`
- Ответ: `200 OK`.

---

## Записи (Records)

### Получить записи

- `GET {domain}/api/v1/catalogs/{catalogId}/records` с параметрами `viewId`, `fields`, `filters`, `searchText`, `sortField`, `sortType`, `limit`, `offset`.
- `filters` может быть:
  - массивом `filters[0][fieldId]=...` с типоспецифичным `value`;
  - JSON-объектом с комбинациями `$and` / `$or` и вложенными условиями, сериализованным в строку.
- Параметр `fields` ограничивает набор возвращаемых полей и может описывать вложенные поля связанных записей (объект `{ fieldId, fields: { catalogId: [subFieldIds] } }`).
- Параметр `id` (несколько значений) фильтрует по конкретным ID записей.
- Ответ: массив записей (`id`, `title`, `values`).

### Получить запись

- `GET {domain}/api/v1/catalogs/{catalogId}/records/{recordId}{?fields}`
- Ответ: объект с `id`, `title`, `privilegeCode`, `values`.
- Для получения расширенных полей связанных каталогов используется `withFieldsAdditional=true` — в ответ добавляется `recordValues`.

### Создать запись

- `POST {domain}/api/v1/catalogs/{catalogId}/records`
- Тело: `values` с наборами по API-ID полей (текст, числа, категории, даты, контакты, сотрудники, связанные объекты, файлы).
- Ответ: `id` созданной записи.

### Изменить запись

- `PATCH {domain}/api/v1/catalogs/{catalogId}/records/{recordId}`
- Тело: `values` с новыми значениями; для файлов можно смешивать существующие `id` и новые `src`.
- Ответ: `200 OK`.

### Удалить запись

- `DELETE {domain}/api/v1/catalogs/{catalogId}/records/{recordId}`
- Ответ: `200 OK`.

---

## Связи (Relations)

- `GET {domain}/api/v1/catalogs/{catalogId}/records/{recordId}/relations`
- Параметры: `catalogId`, `recordId`, опциональные фильтры `catalogId` (по связанному каталогу) и `fieldId`.
- Фильтры идентичны тем, что применяются при «Получить записи».
- Ответ: массив связей с `fieldId`, `fieldName`, списком связанных `records` и `recordsTotal`.

---

## Истории (Histories)

### Получить историю

- `GET {domain}/api/v1/histories?catalogId={catalogId}&recordId={recordId}`
- Параметры: `catalogId` (обязателен), `recordId` (если не указан — возвращается активность каталога), `limit`, `from`, `sortType (asc|desc)`, `userId`.
- Также доступны фильтры как в «Получить записи», если `recordId` не передан.
- Ответ: массив событий (`id`, `catalogId`, `recordId`, `actionType`, `payload`, `date`, `user`).

### Написать комментарий

- `POST {domain}/api/v1/histories`
- Тело: `catalogId`, `recordId`, `type: "COMMENT"`, `payload.message`.
- Ответ: `id` комментария.

---

## Файлы (Files)

### Скачать файл

- `GET {domain}/api/v1/files/{fileId}`
- Возвращает редирект `302` с заголовком `Location` на хранилище.

### Прикрепить внешний файл

- В теле создания/обновления записи указать поле типа «Файл»:

```json
{
  "values": {
    "16": [{
      "title": "bpium_logo.png",
      "src": "https://...",
      "size": "8513",
      "mimeType": "image/png"
    }]
  }
}
```

### Загрузить файл в Bpium S3

1. **Получить ключи загрузки:** `POST {domain}/api/v1/files/` с `catalogId`, `recordId` (опционально), `fieldId`, `name`, `size`, `mimeType`, `typeStorage: "remoteStorage"`. Ответ содержит `fileId`, `uploadUrl`, `fileKey`, `AWSAccessKeyId`, `police`, `signature`.
2. **Загрузить файл:** `POST uploadUrl` (multipart/form-data) с полями `key`, `acl`, `AWSAccessKeyId`, `Policy` (именно `police` из предыдущего шага), `Signature`, `Content-Type`, `file`.
3. **Подтвердить загрузку:** `PATCH {domain}/api/v1/files/{fileId}` с `name`, `size`, `mimeType`, `url`. Ответ содержит `metadata.preview`/`thumbnail`.
4. **Привязать к записи:** сохранить запись каталога, указав `values["fieldId"] = [{ "id": fileId }]`.

---

## Отделы (Sections)

### Получить отделы

- `GET {domain}/api/v1/sections`
- Ответ: список отделов (`id`, `icon`, `name`).

### Получить отдел

- `GET {domain}/api/v1/sections/{sectionId}`
- Ответ: объект с `privilegeCode`.

### Создать отдел

- `POST {domain}/api/v1/sections`
- Тело: `name`, `icon`.
- Ответ: `id`.

### Изменить отдел

- `PATCH {domain}/api/v1/sections/{sectionId}`
- Ответ содержит обновлённые поля и `catalogsPriorities`.

### Удалить отдел

- `DELETE {domain}/api/v1/sections/{sectionId}`
- Ответ: `200 OK`.

---

## Виды (Views)

### Получить виды

- `GET {domain}/api/v1/catalogs/{catalogId}/views`
- Ответ: массив видов (`id`, `name`, `originName`, `forRights`).

### Получить вид

- `GET {domain}/api/v1/catalogs/{catalogId}/views/{viewId}`
- Ответ: объект с `privilegeCode`, `filters` (каждый фильтр — `id`, `attr`, `value`).
- Форматы `value` совпадают с фильтрами в разделе «Записи».

### Создать вид

- `POST {domain}/api/v1/catalogs/{catalogId}/views`
- Тело: `name`, `originName`, `forRights`, массив `filters`.
- Ответ: `id`.

### Изменить вид

- `PATCH {domain}/api/v1/catalogs/{catalogId}/views/{viewId}`
- Тело: обновлённые свойства и фильтры.
- Ответ: `200 OK`.

### Удалить вид

- `DELETE {domain}/api/v1/catalogs/{catalogId}/views/{viewId}`
- Ответ: `200 OK`.

---

## Сообщения (Messages)

### Получить сообщения записи

- `GET {domain}/api/v1/catalogs/{catalogId}/records/{recordId}/messages`
- Ответ: массив сообщений (`id`, `author`, `text`, `attachments`, `createdDate`, `deleted`, `mention`, `reply`).

### Создать сообщение

- `POST {domain}/api/v1/catalogs/{catalogId}/records/{recordId}/messages`
- Тело: `text`, `mentions`, `attachments`, `replyMessageId`.
- Ответ: `id`.

### Изменить сообщение

- `PATCH {domain}/api/v1/catalogs/{catalogId}/records/{recordId}/messages/{messageId}`
- Тело: обновлённый `text` и сопутствующие поля.
- Ответ: `200 OK`.

### Удалить сообщение

- `DELETE {domain}/api/v1/catalogs/{catalogId}/records/{recordId}/messages/{messageId}`
- Ответ: `200 OK`.

### Подписаться на сообщения

- `PATCH {domain}/api/v1/catalogs/{catalogId}/records/{recordId}/chatOptions/{recordId}`
- Тело: `{"subscribe": true}`
- Ответ: `{ "subscribe": true }`.

---

## Каталог «Интеграция» (рабочая схема)

- **sectionId**: `2`
- **catalogId**: `16`
- Назначение: хранение курсов, которые будут выгружаться в Tilda (название, расписание запусков, цены, маркеры акций).

| № поля (API ID) | Название | Тип | Примечание |
| --- | --- | --- | --- |
| 1 | Название курса | Text | Заголовок карточки курса |
| 2 | Количество часов | Number | Планируемое значение в академических часах |
| 3 | Дата запуска | Text | Свободный формат даты/описания старта (можно позже сменить на Date) |
| 4 | Статус курса | Status / Drop-down | Значения: «идет набор», «лист ожидания», «набор завершен», «курс месяца» |
| 5 | Стоимость на данный момент | Number | Текущая цена |
| 6 | Дата первого повышения | Date | Опционально проставляется при изменении стоимости |
| 7 | Стоимость первого повышения | Number | Цена после первого изменения |
| 8 | Дата второго повышения | Date | |
| 9 | Стоимость второго повышения | Number | |
| 10 | Стоимость в рассрочку | Number | |
| 11 | Документ | Text | Пока текстовое поле; при необходимости заменить на File |
| 12 | Тип | Text | Например, «Сертификат», «Интенсив» и т. п. |
| 13 | Виды практик | Text | Свободное описание практик |
| 14 | Курс месяца | Switch | Флаг «выделенный курс», по умолчанию выключен |

Эти идентификаторы используем в серверном приложении для чтения/записи данных через API `catalogs/16/...`.

### Маппинг Bpium → Tilda (черновик)

- `record.title` (поле «Название курса») → заголовок карточки курса в Tilda (плейсхолдер `{{course_title}}`).
- API `catalogs/16/records` возвращает значения по идентификаторам полей:

| API ID | Название поля | Тип | Комментарий |
| --- | --- | --- | --- |
| 2 | Название курса | text | `record.title` дублирует это поле |
| 3 | Количество часов | number |
| 4 | Дата запуска | text |
| 5 | Статус курса | radiobutton (значение массива строк, напр. `["1"]`) |
| 6 | Стоимость на данный момент | number |
| 7 | Дата первого повышения | date (ISO) |
| 8 | Стоимость первого повышения | number |
| 9 | Дата второго повышения | date |
| 10 | Стоимость второго повышения | number |
| 11 | Стоимость в рассрочку | number |
| 12 | Документ | text |
| 13 | Тип | text |
| 14 | Виды практик | text |
| 15 | Курс месяца | switch (true/false) |

- Серверный клиент (`app/bpium.py`) использует эти ID в `FIELD_MAP`, приводит типы (`_safe_number`, `_string_value`, `_bool_value`) и возвращает нормализованную модель `Course`.

### Внешние запросы и CORS

- Чтобы запускать процессы по внешнему HTTP‑адресу, в каталоге «Управление → Внешние запросы» создаётся запись с `URL-идентификатором`. Полный адрес приёма: `{ваш_домен}/api/webrequest/{идентификатор}`.
- Процесс можно запускать синхронно (ответ возвращается в том же соединении, таймаут 60 секунд) или асинхронно (`?async=true` — ответ пустой, процесс продолжает выполняться в фоне).
- В сценарий передаются все параметры запроса: `url`, `method`, `headers`, `query`, `body`, а также служебный объект `event`.
- Чтобы браузерный AJAX запрос не блокировался политикой CORS, в `$headers` сценария нужно вернуть `Access-Control-Allow-Origin` (конкретный домен или `*`), например:
  ```javascript
  $headers = {
      "Access-Control-Allow-Origin": "https://example.com"
  }
  ```
