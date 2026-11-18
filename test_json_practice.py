from Order import Client, Order, OrderItem, UrgentOrder
from json_practice import (
    find_orders_by_client,
    order_to_data,
    order_from_data,
    save_orders,
    main,
)
from decimal import Decimal
import json


def make_order(client_name="Иван", price: Decimal | int | str = 500):
    client = Client(client_name, "+7 000 000-00-00")
    item = OrderItem("Услуга", 1, price)
    return Order(client, [item])


def make_urgent_order(
    *,
    client_name="Иван",
    phone="+7 000 000-00-00",
    quantity=1,
    surcharge: Decimal | int | str
     = 100
):
    client = Client(client_name, phone)
    item = OrderItem("Услуга", quantity, 500)
    return UrgentOrder(client, [item], surcharge)


def test_find_orders_by_client_returns_all_matches():
    orders = [
        make_order("Иван"),
        make_order("Иван"),
        make_order("Анна"),
    ]

    result = find_orders_by_client(orders, "иван")

    assert len(result) == 2
    assert result[0].client.name == "Иван"
    assert result[1].client.name == "Иван"


def test_find_orders_by_client_returns_empty_list_when_no_match():
    orders = [make_order("Иван"), make_order("Анна")]

    result = find_orders_by_client(orders, "Мария")

    assert result == []


def test_order_to_data_for_standard_order():
    order = make_order("Иван")
    data = order_to_data(order)

    assert data["type"] == "standard"
    assert "surcharge" not in data


def test_order_to_data_for_urgent_order():
    order = make_urgent_order(quantity=2, surcharge="150.50")
    data = order_to_data(order)
    assert data["type"] == "urgent"
    assert data["surcharge"] == "150.50"
    assert data["client"]["name"] == "Иван"
    assert data["items"][0]["quantity"] == 2


def test_order_from_data():
    data = {
        "client": {"name": "Иван", "phone": "+7 000 000-00-00"},
        "items": [{"name": "Услуга", "quantity": 2, "unit_price": "500.00"}],
        "status": "В работе",
        "type": "urgent",
        "surcharge": "150.50",
    }
    restored = order_from_data(data)
    assert isinstance(restored, UrgentOrder)
    assert restored.client.name == "Иван"
    assert restored.items[0].quantity == 2
    assert restored.surcharge == Decimal("150.50")
    assert restored.status == "В работе"


def test_save_orders_writes_urgent_order(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    order = make_urgent_order(surcharge="150.50")
    save_orders([order])

    file_path = tmp_path / "orders.json"
    assert file_path.exists()

    saved_data = json.loads(file_path.read_text(encoding="utf-8"))

    assert saved_data[0]["type"] == "urgent"
    assert saved_data[0]["surcharge"] == "150.50"


def test_main_reports_invalid_json(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "orders.json").write_text("это не JSON", encoding="utf-8")

    main()

    output = capsys.readouterr().out
    assert "Не удалось прочитать orders.json" in output
    assert "Меню заказов" not in output


def test_main_starts_without_orders_file(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)

    def choose_exit(prompt):
        return "0"

    monkeypatch.setattr("builtins.input", choose_exit)

    main()

    output = capsys.readouterr().out
    assert "Файл заказов не найден" in output
    assert "Меню заказов" in output
    assert not (tmp_path / "orders.json").exists()


def test_save_orders_preserves_working_status(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    order = make_order("Иван")
    order.start_work()
    save_orders([order])

    file_path = tmp_path / "orders.json"
    saved_data = json.loads(file_path.read_text(encoding="utf-8"))

    assert saved_data[0]["status"] == "В работе"


def test_completed_status_is_saved_to_json(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    order = make_order()
    order.start_work()
    order.complete()
    save_orders([order])
    file_path = tmp_path / "orders.json"
    saved_data = json.loads(file_path.read_text(encoding="utf-8"))

    assert saved_data[0]["status"] == "Завершён"


def test_order_from_data_restores_completed_status():
    order_data = order_to_data(make_order("Иван"))
    order_data["status"] = "Завершён"
    restored_order = order_from_data(order_data)
    assert restored_order.status == "Завершён"


def test_order_from_data_restores_canceled_status():
    order_data = order_to_data(make_order("Иван"))
    order_data["status"] = "Отменён"
    restored_order = order_from_data(order_data)
    assert restored_order.status == "Отменён"


def test_save_orders_preserves_multiple_orders(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    orders = [make_order(), make_urgent_order()]
    save_orders(orders)
    file_path = tmp_path / "orders.json"
    saved_data = json.loads(file_path.read_text(encoding="utf-8"))
    assert len(saved_data) == 2
    assert saved_data[0]["type"] == "standard"
    assert saved_data[1]["type"] == "urgent"


def test_save_orders_writes_empty_list(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    save_orders([])
    file_path = tmp_path / "orders.json"
    saved_data = json.loads(file_path.read_text(encoding="utf-8"))
    assert saved_data == []


def test_order_from_data_restores_standard_order():
    order = make_order()
    data = order_to_data(order)
    restored = order_from_data(data)
    assert type(restored) is Order


def test_order_from_data_restores_multiple_items():
    items = [OrderItem("Подшив брюк", 2, 500), OrderItem("Замена молнии", 1, 100)]
    client = Client("Иван", "+7 950 233 42-42")
    order = Order(client, items)
    data = order_to_data(order)
    restored = order_from_data(data)
    assert len(restored.items) == 2
    assert restored.items[0].name == "Подшив брюк"
    assert restored.items[0].quantity == 2
    assert restored.items[1].name == "Замена молнии"
    assert restored.items[1].quantity == 1


def test_order_from_data_restores_client_data():
    result = order_from_data(order_to_data(make_order()))
    assert result.client.name == "Иван"
    assert result.client.phone == "+7 000 000-00-00"


def test_order_from_data_restores_item_price():
    restored = order_from_data(order_to_data(make_order(price="500.50")))
    assert restored.items[0].unit_price == Decimal("500.50")
