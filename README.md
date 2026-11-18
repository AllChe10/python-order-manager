# Python Order Manager — учебный проект

[![Tests](https://github.com/AllChe10/python-order-manager/actions/workflows/tests.yml/badge.svg)](https://github.com/AllChe10/python-order-manager/actions/workflows/tests.yml)

Консольное приложение для практики Python, ООП, работы с JSON и автоматизированных тестов. Концепция заказов используется для обучения; это не готовая система для действующего ателье.

## Возможности

- Создание обычных и срочных заказов.
- Несколько услуг в одном заказе, количество и цена за единицу.
- Расчёт сумм с помощью `Decimal`.
- Статусы заказа: новый, в работе, завершён и отменён.
- Сохранение и восстановление заказов из JSON.
- Поиск заказов по имени клиента.
- Проверки на `pytest` для модели и JSON-функций.

## Установка

Требуется Python 3.10 или новее. Команды установки выполняются из корня репозитория в PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Set-Location .\order_manager
```

## Запуск приложения

После перехода в папку `order_manager`:

```powershell
..\.venv\Scripts\python.exe json_practice.py
```

Приложение читает и сохраняет файл `orders.json` в текущей папке. В репозитории нет реальных данных клиентов; локальный файл заказов исключён из Git.

## Запуск тестов

Из папки `order_manager`:

```powershell
..\.venv\Scripts\python.exe -m pytest -v
```

Чтобы посмотреть покрытие основных модулей:

```powershell
..\.venv\Scripts\python.exe -m pytest --cov=Order --cov=json_practice --cov-report=term-missing
```

## Структура

```text
order_manager/
├── Order.py
├── json_practice.py
├── test_order.py
└── test_json_practice.py
```

В проекте показаны учебные упражнения с классами `Client`, `OrderItem`, `Order` и `UrgentOrder`, а также работа с файлами и тестами.
