# 👹 Samurai Telegram Bot

Профессиональный бот-автомодератор для Telegram групп с использованием машинного обучения. Бот автоматически обнаруживает и обрабатывает спам, мат, NSFW контент и другие нарушения, поддерживая чистоту и порядок в чатах.

## ✨ Основные возможности

- **🛡️ Анти-мат фильтр**: Автоматическое обнаружение и удаление сообщений с нецензурной лексикой (русский и английский языки)
- **🤖 Анти-спам на основе ML**: Интеллектуальное обнаружение спама с использованием модели RUSpam/spam_deberta_v4
- **🔞 NSFW детекция**: Анализ фотографий профилей на наличие неприемлемого контента
- **⭐ Система репутации**: Пользователи получают репутацию за активное участие, влияющую на права в группе
- **📢 Система репортов**: Пользователи могут жаловаться на сообщения, админы получают уведомления с кнопками действий
- **📅 Планируемые объявления**: Автоматические периодические сообщения с настраиваемым расписанием
- **🌍 Мультиязычность**: Поддержка русского и английского языков через Project Fluent
- **📊 Логирование**: Полное логирование действий в отдельный канал
- **👤 Определение пола**: Автоматическое определение пола пользователя по имени
- **💾 Умное кэширование**: LRU-кэш для оптимизации производительности
- **🔋 Управление памятью**: Автоматическая выгрузка ML-моделей из памяти при неиспользовании

## 🚀 Быстрый старт

### Требования

- Python 3.11 или выше
- Токен бота от [@BotFather](https://t.me/BotFather)
- Минимум 1 ГБ оперативной памяти (рекомендуется 2 ГБ для комфортной работы)

### Установка

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/QuestGuideRF/samurai.git
   cd samurai
   ```

2. **Установите зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте конфигурацию**:

   Отредактируйте файл `config.toml` и укажите:
   - ID вашего аккаунта в `[bot]` → `owner`
   - Токен бота в `[bot]` → `token` (или через переменную окружения)
   - ID групп, где бот будет работать в `[groups]` → `main`
   - ID канала для репортов в `[groups]` → `reports`
   - ID канала для логов в `[groups]` → `logs`

   Также можно настроить через переменные окружения:
   ```bash
   export BOT_TOKEN="your_bot_token"
   export BOT_OWNER="your_user_id"
   export GROUPS_MAIN="-1001234567890,-1009876543210"
   export GROUPS_REPORTS="-1001111111111"
   export GROUPS_LOGS="-1002222222222"
   ```

4. **Инициализируйте базу данных** (только при первом запуске):

   Откройте `db_init.py`, закомментируйте строку `exit(...)` и выполните:
   ```bash
   python db_init.py
   ```

   ⚠️ **ВНИМАНИЕ**: Этот скрипт удаляет все данные из таблиц! Используйте только при первой настройке.

5. **Запустите бота**:
   ```bash
   python bot.py
   ```

### Запуск в Docker

```bash
# Сборка образа
docker build -t samurai-bot .

# Запуск контейнера
docker run -d \
  --name samurai-bot \
  -v $(pwd)/config.toml:/app/config.toml \
  -e BOT_TOKEN="your_token" \
  -e BOT_OWNER="your_user_id" \
  -e GROUPS_MAIN="-1001234567890" \
  samurai-bot
```

Или используйте файл с переменными окружения:
```bash
docker run -d --name samurai-bot --env-file .env samurai-bot
```

### Запуск как systemd сервис

Создайте файл `/etc/systemd/system/samurai-bot.service`:

```ini
[Unit]
Description=Samurai Telegram Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/samurai
Environment="BOT_TOKEN=your_token"
Environment="BOT_OWNER=your_user_id"
Environment="GROUPS_MAIN=-1001234567890"
ExecStart=/usr/bin/python3 /path/to/samurai/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Затем:
```bash
sudo systemctl daemon-reload
sudo systemctl enable samurai-bot
sudo systemctl start samurai-bot
```

## 📁 Структура проекта

```
samurai/
├── bot.py                      # Точка входа, инициализация и запуск бота
├── config.toml                 # Файл конфигурации (TOML формат)
├── db_init.py                  # Скрипт инициализации базы данных
├── requirements.txt            # Зависимости Python
├── Dockerfile                  # Конфигурация Docker-образа
├── config/                     # Модуль конфигурации
│   ├── settings.py            # Pydantic модели для валидации конфигурации
│   └── __init__.py
├── core/                       # Основные компоненты
│   └── i18n.py                # Интернационализация (Project Fluent)
├── db/                         # Работа с базой данных
│   ├── database.py            # Настройка подключения (SQLite/PostgreSQL)
│   └── models/                # ORM модели
│       ├── member.py          # Модель участника (репутация, нарушения)
│       └── spam.py            # Модель записей о спаме
├── handlers/                   # Обработчики событий
│   ├── group_events.py        # Обработка сообщений в группах (основная логика)
│   ├── admin_actions.py       # Команды администраторов (ban/unban)
│   ├── user_actions.py        # Команды пользователей (report, @admin)
│   ├── personal_actions.py    # Личные команды (ping, profanity check)
│   ├── callbacks.py           # Обработка inline-кнопок
│   └── exceptions.py          # Обработка ошибок
├── filters/                    # Фильтры для обработчиков
│   ├── is_owner.py           # Проверка прав владельца
│   ├── is_admin.py           # Проверка прав администратора
│   ├── in_main_groups.py     # Проверка, что сообщение в основной группе
│   ├── throttle.py           # Ограничение частоты запросов
│   └── member_can_restrict.py # Проверка прав на ограничения
├── middlewares/                # Промежуточное ПО
│   ├── i18n.py               # Мидлвар для интернационализации
│   └── throttling.py         # Мидлвар для rate limiting
├── services/                   # Бизнес-логика и сервисы
│   ├── spam.py               # ML-модель обнаружения спама
│   ├── profanity.py          # Обнаружение мата
│   ├── nsfw.py               # Детекция NSFW контента
│   ├── announcements.py      # Планируемые объявления
│   ├── gender.py             # Определение пола по имени
│   ├── cache.py              # Система кэширования
│   ├── reports.py            # Обработка репортов
│   ├── ml_manager.py         # Управление ML-моделями в памяти
│   └── healthcheck.py        # HTTP endpoint для health checks
├── locales/                    # Переводы (Fluent формат)
│   ├── ru/                    # Русский язык
│   │   ├── strings.ftl       # Основные строки
│   │   └── announcements.ftl # Тексты объявлений
│   └── en/                    # Английский язык
│       ├── strings.ftl
│       └── announcements.ftl
├── utils/                      # Вспомогательные функции
│   ├── helpers.py            # Утилиты
│   ├── enums.py              # Перечисления
│   └── localization.py       # Экспорты локализации
├── libs/                       # Внешние библиотеки
│   ├── censure/              # Фильтр нецензурной лексики
│   └── gender_extractor/     # Определение пола
└── ruspam_model/              # ML-модель для обнаружения спама
    └── torch/                 # Веса модели (PyTorch)
```

## 🛠 Использование

### Команды для пользователей

| Команда | Описание |
|---------|----------|
| `/rules` или `!rules` | Показать правила чата |
| `/report` или `!report` | Пожаловаться на сообщение (ответьте на сообщение) |
| `/me`, `/info`, `/lvl` или `!me` | Показать информацию о пользователе и репутацию |
| `!бу` | Развлекательная команда (бот "пугается") |
| `@admin` | Вызвать внимание администраторов |

### Команды для администраторов

| Команда | Описание |
|---------|----------|
| `!ban` | Забанить пользователя (ответьте на сообщение) |
| `!unban` | Разбанить пользователя (ответьте на сообщение) |
| `!ping` | Проверить статус бота и системные ресурсы |
| `!prof <текст>` или `!мат <текст>` | Проверить текст на наличие мата |

### Команды для владельца

| Команда | Описание |
|---------|----------|
| `!msg <текст>` | Отправить сообщение от имени бота (с выбором чата) |
| `!chatid` | Получить ID текущего чата |
| `!reload` | Перезагрузить объявления из файлов локализации |
| `!log <текст>` | Написать тестовое сообщение в лог |
| `!top_violators_profanity [количество]` | Топ нарушителей по мату (по умолчанию 10, макс 50) |
| `!top_violators_spam [количество]` | Топ нарушителей по спаму (по умолчанию 10, макс 50) |

### Система репортов

Когда пользователь отправляет `/report` в ответ на сообщение:
1. Бот отправляет подтверждение в чат
2. Сообщение пересылается в канал репортов
3. Администраторы получают кнопки для действий:
   - 👀 Перейти к сообщению
   - 🗑 Удалить сообщение
   - 🗑 Удалить + ❌ Бан
   - 🗑 Удалить + 🙊 Мут на день/неделю
   - ❎ Нарушений нет (с опциями наказания репортера)

### Система репутации

- Пользователи получают репутацию за активное участие
- Репутация влияет на права:
  - До определенной репутации действуют ограничения на отправку медиа
  - Низкая репутация → проверка на спам
  - Высокая репутация → пропуск некоторых проверок
- Владелец может вручную изменять репутацию через команды

### Планируемые объявления

Объявления загружаются из файлов `locales/{lang}/announcements.ftl` и отправляются автоматически с настраиваемыми интервалами.

Настройка в `config.toml`:
```toml
[announcements]
enabled = true
sleep_from = "22:00"  # Не отправлять с 22:00
sleep_to = "9:00"     # До 9:00
utc_offset = 5        # Смещение времени
```

## ⚙️ Конфигурация

Основная конфигурация находится в файле `config.toml`. Все параметры можно переопределить через переменные окружения.

### Основные параметры

**Переменные окружения:**

| Переменная | Описание |
|-----------|----------|
| `BOT_TOKEN` | Токен бота (обязательно) |
| `BOT_OWNER` | ID владельца (обязательно) |
| `BOT_LOCALE` | Язык по умолчанию (`ru` или `en`) |
| `GROUPS_MAIN` | ID основных групп (через запятую) |
| `GROUPS_REPORTS` | ID канала для репортов |
| `GROUPS_LOGS` | ID канала для логов |
| `LINKED_CHANNELS` | ID связанных каналов (через запятую) |
| `DB_URL` | URL базы данных (по умолчанию SQLite) |
| `HEALTHCHECK_PORT` | Порт для health check endpoint |

**Пример конфигурации `config.toml`:**

```toml
[bot]
token = ""  # Заполняется через BOT_TOKEN или здесь
owner = 0   # Заполняется через BOT_OWNER или здесь
version = "1.0"
version_codename = "Night City Samurai"

[groups]
main = [-1001234567890]  # Основные группы
reports = -1001111111111  # Канал репортов
logs = -1002222222222     # Канал логов
linked_channels = []      # Связанные каналы
new_users_nomedia = 7776000  # Время ограничения медиа для новых пользователей (секунды)

[spam]
member_messages_threshold = 10      # После скольких сообщений прекратить проверку
member_reputation_threshold = 10    # Минимальная репутация для пропуска проверок
allow_media_threshold = 20          # Репутация для отправки медиа
allow_forwards_threshold = 50       # Репутация для пересылки сообщений
autoban_enabled = true              # Автобан за спам
autoban_threshold = 100             # Количество нарушений для автобана

[nsfw]
enabled = true
# Пороги обнаружения (настраиваются опытным путем)

[db]
url = "sqlite+aiosqlite:///db.sqlite"  # SQLite по умолчанию
# Для PostgreSQL: "postgresql+asyncpg://user:pass@host/dbname"

[healthcheck]
enabled = false  # Включить HTTP endpoint для проверки здоровья
host = "0.0.0.0"
port = 8080
```

## 🧪 Технологический стек

- **Python 3.11+** — язык программирования
- **aiogram 3.x** — асинхронный фреймворк для Telegram Bot API
- **PyTorch** — ML-фреймворк для моделей обнаружения спама и NSFW
- **Transformers (HuggingFace)** — библиотека для работы с ML-моделями
- **ormar** — асинхронный ORM для работы с БД
- **SQLite/PostgreSQL** — базы данных (SQLite по умолчанию)
- **Pydantic** — валидация конфигурации
- **Project Fluent** — система интернационализации
- **aiohttp** — асинхронный HTTP-клиент
- **Pillow** — обработка изображений для NSFW детекции

## 💾 Использование памяти

Бот использует примерно **800 МБ ОЗУ** для ML-моделей и кэширования данных. Модели автоматически выгружаются из памяти при неиспользовании для оптимизации потребления ресурсов.

Если процесс завершается из-за нехватки памяти, добавьте swap-файл:

```bash
# Создать swap-файл 2 ГБ
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Сделать постоянным
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

## 🌍 Интернационализация

Бот использует [Project Fluent](https://projectfluent.org/) для переводов. Файлы переводов находятся в `locales/{lang}/strings.ftl`.

### Добавление новых переводов

1. Откройте файл `locales/{lang}/strings.ftl`
2. Добавьте ключ с дефисами: `my-new-key = Текст перевода`
3. Используйте переменные: `greeting = Привет, { $name }!`

Пример использования в коде:

```python
from core.i18n import _

# Простой перевод
text = _("error-no-reply")

# С переменными
text = _("report-message", date="01.01.2024", chat_id="123", msg_id="456")
```

## 📊 База данных

По умолчанию используется SQLite. Для продакшена рекомендуется PostgreSQL.

**Инициализация базы данных:**

1. Откройте `db_init.py`
2. Закомментируйте строку `exit("...")`
3. Запустите: `python db_init.py`
4. Верните строку `exit()` обратно

⚠️ **ВНИМАНИЕ**: Скрипт удаляет все данные! Используйте только при первой настройке.

**Переход на PostgreSQL:**

Измените `DB_URL` в `config.toml` или переменную окружения:
```bash
export DB_URL="postgresql+asyncpg://user:password@localhost/samurai"
```

Установите зависимости:
```bash
pip install aiomysql pymysql  # для MySQL
# или для PostgreSQL уже включено в requirements.txt
```

## 📝 Логирование

Все действия логируются в канал, указанный в `config.toml` → `[groups]` → `logs`. Логи включают:
- Нарушения (мат, спам, NSFW)
- Действия администраторов
- Ошибки и предупреждения
- Системные события

## 🔒 Безопасность

- Все чувствительные данные (токены) хранятся в переменных окружения или `config.toml`
- Используйте переменные окружения в продакшене вместо записи токенов в файлы
- Регулярно обновляйте зависимости для получения исправлений безопасности
- Не делитесь файлами конфигурации с токенами

## Источники словарей имён

Модуль извлечения имени использует данные из `libs/gender_extractor/nameLists/`.

<details>
<summary>Список источников по странам</summary>

- **Уменьшительные формы английских имён**
  - http://en.wiktionary.org/wiki/Appendix:English_given_names
- **Афганистан**
  - Справочник Великобритании по употреблению имён https://www.fbiic.gov/public/2008/nov/Naming_practice_guide_UK_2006.pdf
- **Албания**
  - Справочник Великобритании по употреблению имён https://www.fbiic.gov/public/2008/nov/Naming_practice_guide_UK_2006.pdf
- **Австралия**
  - Department of Attorney General and Justice NSW http://www.bdm.nsw.gov.au/births/popularBabyNames.htm
- **Бельгия**
  - Voornamen van de bevolking op 1.1.2009 (XLS, 17.33 MB) http://statbel.fgov.be/nl/modules/publications/statistiques/bevolking/prenoms_de_la_population_totale.jsp
- **Бразилия**
  - http://www.dicionariodenomesproprios.com.br/nomes-masculinos/
  - http://www.dicionariodenomesproprios.com.br/nomes-femininos/
- **Канада**
  - http://www.servicealberta.ca/1166.cfm (1990 lists)
- **Чехия**
  - Czech name days http://www.myczechrepublic.com/czech_culture/czech_name_days/alphabetical.html
  - Diminutives http://www.myczechrepublic.com/czech_culture/czech_name_days/dimf.html and http://www.myczechrepublic.com/czech_culture/czech_name_days/dimm.html
- **Финляндия**
  - http://www.sci.fi/~kajun/finns/
- **Фрисландия**
  - http://allenamen.nl/friese_namen/jongens_namen.html and http://allenamen.nl/friese_namen/meisjes_namen.html
- **Греция**
  - http://www.fredonia.edu/faculty/emeritus/edwinlawson/greeknames/
- **Индия**
  - www.eyeofindia.com/services/indian-names
  - www.iloveindia.com/babynames
  - http://en.wikipedia.org/wiki/Category:Indian_given_names
  - http://www.infernaldreams.com/names/Asia/India/Hin_Names.htm
- **Иран**
  - http://persia.org/Information/boys.html
  - http://persia.org/Information/girls.html
- **Ирландия**
  - see Northern Ireland
- **Израиль**
  - http://www.learn-hebrew-names.com/Hebrew-names.aspx
- **Италия**
  - page 12 from http://www3.istat.it/salastampa/comunicati/non_calendario/20100318_00/testointegrale20100318.pdf
- **Япония**
  - https://en.wikipedia.org/wiki/Category:Japanese_feminine_given_names
  - https://en.wikipedia.org/wiki/Category:Japanese_masculine_given_names
- **Латвия**
  - http://en.wiktionary.org/wiki/Appendix:Latvian_given_names
  - http://en.wiktionary.org/wiki/Category:Latvian_male_given_names and http://en.wiktionary.org/wiki/Category:Latvian_female_given_names
- **Норвегия**
  - Namnestatistikk, 2011, http://www.ssb.no/emner/00/navn/
- **Польша**
  - http://chomikuj.pl/justynadow/s*c5*82owniki+imion/S*c5*81OWNIK+IMION+POLSKICH,263985157.pdf
  - augmented with diminutives from http://en.wiktionary.org/wiki/Appendix:Polish_given_names
- **Румыния**
  - http://childnamesworld.com/romanian-boy-baby-names.php?religion=Romanian&gender=boy
  - http://ro.wikipedia.org/wiki/List%C4%83_de_prenume_rom%C3%A2ne%C8%99ti
- **Россия**
  - http://en.wikipedia.org/wiki/Category:Russian_masculine_given_names and http://en.wikipedia.org/wiki/Category:Russian_feminine_given_names
  - http://habrahabr.ru/post/123856/
  - Male diminutives from http://irusik-05.narod.ru/index37.html
- **Словения**
  - http://www.stat.si/eng/imena.asp
- **Сомали**
  - Справочник Великобритании по употреблению имён https://www.fbiic.gov/public/2008/nov/Naming_practice_guide_UK_2006.pdf
- **Испания**
  - Nombres mas frecuentes simples y exactos para total nacional y exactos por provincia de residencia
 http://www.ine.es/daco/daco42/nombyapel/nombyapel.htm
- **Швеция**
  - http://www.scb.se/Pages/ProductTables____30919.aspx
- **Турция**
  - http://www.annecocuk.com/isim/isimler-xkiz.htm
  - http://www.annecocuk.com/isim/isim-erkek.htm
- **Великобритания**
  - http://www.ons.gov.uk/ons/publications/re-reference-tables.html?edition=tcm%3A77-243644
- **Украина**
  - http://www.aratta-ukraine.com/sacred_ua.php?id=44
  - http://database.ukrcensus.gov.ua/dw_name/tlum.asp?nom_zag=4
  - http://logistik.mybb.ru/viewtopic.php?id=141
- **США**
  - 1990 census: e.g., http://www.uta.fi/FAST/US7/NAMES/male1st.html and http://www.uta.fi/FAST/US7/NAMES/female-1.html

</details>

Подпись относится к текущей версии проекта.

---

Автор: legenda  
Telegram: [@LEGENDA_SD](https://t.me/LEGENDA_SD)
