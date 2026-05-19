# ym_etl

ETL-пайплайн для ежедневной загрузки данных из API Яндекс.Маркета (партнерский API) в PostgreSQL.

## 1. Назначение проекта

- **Входные данные**: API Яндекс.Маркета (отчёты: продажи, остатки, движение товаров, цены, заказы, справочник товаров)
- **Выходные данные**: Таблицы в схемах `raw`, `orders`, `catalog_mp` в PostgreSQL (база `ymdb`)

---

## 2. Логика пайплайна

### 2.1. Источники и маршрутизация

- Данные получаются из API Яндекс.Маркета с постраничной загрузкой (синхронные отчёты) или через асинхронную генерацию (отчёты, требующие ожидания).
- Поддерживается **rate limiting** (ограничение частоты запросов) согласно документации API.

#### Отчёты и их маршрутизация

| Отчёт | Тип | Схема | Таблица |
|-------|-----|-------|---------|
| Справочник товаров (offer mappings) | синхронный | `catalog_mp` | `dim_offers` |
| Продажи (аналитика) | асинхронный (CSV) | `raw` | `raw_sales_reports` |
| Остатки на складах | асинхронный (CSV) | `raw` | `raw_stocks` |
| Движение товаров | асинхронный (CSV) | `raw` | `raw_goods_movement` |
| Цены товаров | асинхронный (CSV) | `raw` | `raw_prices` |
| Детальная информация о заказах | синхронный (JSON) | `orders` | `orders`, `orders_statuses`, `orders_commissions`, `orders_items`, `orders_payments`, `orders_subsidies` |

### 2.2. Шаги обработки

#### Синхронные отчёты (offers, orders)

1. **EXTRACT**: Загрузка данных из API с постраничной пагинацией
2. **TRANSFORM**: Парсинг JSON-ответа в модели SQLAlchemy
3. **LOAD**:
   - Создание схемы и таблицы при необходимости
   - `UPSERT` (offers) или `DELETE + INSERT` (orders)
   - Сохранение сырого JSON в raw-таблицу (offers)

#### Асинхронные отчёты (sales, stocks, goods_movement, prices)

1. **EXTRACT**:
   - POST-запрос на генерацию отчёта
   - Ожидание готовности (polling с rate limiting)
   - Скачивание ZIP-архива по ссылке
2. **TRANSFORM**:
   - Распаковка ZIP в CSV
   - Чтение CSV через pandas
   - Маппинг колонок согласно конфигурации (`report_configs.py`)
   - Приведение типов (`Decimal`, `int`, `str`)
3. **LOAD**:
   - `DELETE` по дате (идемпотентность)
   - `BULK INSERT` в raw-таблицу
   - Очистка временных файлов (опционально)

#### Особенности обработки ошибок

- Сетевые ошибки API логируются и пробрасываются как `RuntimeError`
- `RateLimiter` автоматически ожидает при превышении лимита запросов
- При ошибке в одном отчёте оркестратор продолжает обработку остальных дат (`continue`)
- Отсутствие обязательных колонок в CSV вызывает `ValueError`

---

## 3. Архитектурная модель

### 3.1. Ключевые модули

| Модуль | Назначение |
|--------|------------|
| `app/api/client.py` | Базовый HTTP-клиент для API Яндекс.Маркета |
| `app/api/report_client.py` | Клиент для работы с отчётами (генерация, статус, скачивание) |
| `app/core/pipeline.py` | Пайплайн для асинхронных отчётов (генерация → ожидание → скачивание) |
| `app/core/rate_limiter.py` | Ограничение частоты запросов (скользящее окно) |
| `app/core/date_manager.py` | Управление диапазонами дат для загрузки |
| `app/core/orchestrators/*.py` | Оркестраторы для каждого отчёта (даты, `skip_if_exists`) |
| `app/core/pipelines/*.py` | ETL-пайплайны (extract → transform → load) |
| `app/raw_transformers/*.py` | Трансформеры CSV → SQLAlchemy модели |
| `app/stg_transformers/*.py` | Трансформеры JSON → SQLAlchemy модели |
| `app/storage/models/*.py` | SQLAlchemy модели (`raw`, `orders`, `catalog_mp`) |
| `app/storage/repositories/*.py` | CRUD операции с PostgreSQL |
| `app/processing/file_manager.py` | Работа с ZIP-архивами и CSV-файлами |
| `app/configs/settings.py` | Конфигурация через переменные окружения (Pydantic) |
| `app/configs/logger_settings.py` | Логирование с ротацией файлов |
| `app/configs/report_configs.py` | Конфигурация маппинга колонок CSV → поля БД |

### 3.2. Точки интеграции

- **API Яндекс.Маркета**: `https://api.partner.market.yandex.ru/v2`
- **PostgreSQL**: База `ymdb`, схемы: `raw`, `orders`, `catalog_mp`
- **Airflow**: DAG `ym_etl_daily` (запуск 1 раз в день — планируется)

### 3.3. Структура таблиц

#### `catalog_mp.dim_offers` (справочник товаров)

| Поле | Тип | Описание |
|------|-----|----------|
| `offer_id` | `INTEGER` | PK, идентификатор товара |
| `offer_name` | `STRING` | Наименование товара |
| `market_category_id` | `INTEGER` | Идентификатор категории |
| `length` | `DECIMAL(9,2)` | Длина |
| `width` | `DECIMAL(9,2)` | Ширина |
| `height` | `DECIMAL(9,2)` | Высота |
| `weight` | `DECIMAL(9,2)` | Вес |
| `report_date` | `DATE` | Дата загрузки |

#### `raw.raw_sales_reports` (продажи) — 31 поле  
#### `raw.raw_stocks` (остатки) — 20 полей  
#### `raw.raw_goods_movement` (движение товаров) — 10 полей  
#### `raw.raw_prices` (цены) — 17 полей  

#### `orders.orders` + 5 связанных таблиц  
- `orders_statuses` (SCD Type 2)  
- `orders_commissions`  
- `orders_items`  
- `orders_payments`  
- `orders_subsidies`

---

## 4. Требования к окружению

- **Python**: 3.11+
- **ОС**: Linux (Docker), Windows (локальная разработка)
- **База данных**: PostgreSQL 14+
- **Ключевые библиотеки** (точные версии — в `requirements.txt`):
  - `requests` — HTTP-клиент
  - `SQLAlchemy` — ORM
  - `pandas` — трансформация CSV
  - `pydantic-settings` — конфигурация через env
  - `psycopg2-binary` — драйвер PostgreSQL

---

## 5. Установка и развёртывание

### 5.1. Dev (локально)

```bash
# Создать и активировать виртуальное окружение
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1

# Установить зависимости
pip install -r requirements.txt

# Скопировать example.env → .env, заполнить значения
cp example.env .env

# Создать таблицы в БД
python -m app.storage.init_db

# Запуск конкретного отчёта
python -m app.cli.run_offers
python -m app.cli.run_raw_sales
python -m app.cli.run_raw_stocks
python -m app.cli.run_raw_goods_movement
python -m app.cli.run_raw_prices
python -m app.cli.
```
---
## 6. Использование

### 6.1. Запуск отчётов

```bash
# Справочник товаров (синхронный, пагинация)
python -m app.cli.run_offers

# Продажи (асинхронный CSV)
python -m app.cli.run_raw_sales

# Остатки (асинхронный CSV)
python -m app.cli.run_raw_stocks

# Движение товаров (асинхронный CSV)
python -m app.cli.run_raw_goods_movement

# Цены (асинхронный CSV)
python -m app.cli.run_raw_prices

# Заказы (синхронный, пагинация)
python -m app.cli.run_orders_info
```

### 6.2. Планируемые параметры запуска (CLI)

| Параметр | Описание | Пример |
|----------|----------|--------|
| `--date` | Дата загрузки (YYYY-MM-DD)	| python -m app.cli.run_raw_stocks --date 2026-05-17 |
| `--date_from` |	Начальная дата периода |	python -m app.cli.run_raw_sales --date-from 2026-05-01 |
| `--date-to` | Конечная дата периода | python -m app.cli.run_raw_sales --date-to 2026-05-17 |
|`--skip_if_exists `| Пропуск уже загруженных дат | python -m app.cli.run_raw_stocks --skip-if-exists |
