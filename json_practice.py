import json
from Order import Client, Order, OrderItem, UrgentOrder


def order_to_data(order):
    items_data = []

    for item in order.items:
        items_data.append(
            {
                "name": item.name,
                "quantity": item.quantity,
                "unit_price": str(item.unit_price),
            }
        )

    order_data = {
        "client": {
            "name": order.client.name,
            "phone": order.client.phone,
        },
        "items": items_data,
        "status": order.status,
    }

    if isinstance(order, UrgentOrder):
        order_data["type"] = "urgent"
        order_data["surcharge"] = str(order.surcharge)
    else:
        order_data["type"] = "standard"

    return order_data


def order_from_data(data):
    client = Client(data["client"]["name"], data["client"]["phone"])

    items = []
    for item_data in data["items"]:
        item = OrderItem(
            item_data["name"],
            item_data["quantity"],
            item_data["unit_price"],
        )
        items.append(item)

    if data["type"] == "urgent":
        order = UrgentOrder(client, items, data["surcharge"])
    else:
        order = Order(client, items)

    if data["status"] == "В работе":
        order.start_work()
    elif data["status"] == "Завершён":
        order.start_work()
        order.complete()
    elif data["status"] == "Отменён":
        order.cancel()
    elif data["status"] != "Новый":
        raise ValueError("Неизвестный статус")
    return order


def save_orders(orders):
    orders_data = []

    for order in orders:
        orders_data.append(order_to_data(order))

    with open("orders.json", "w", encoding="utf-8") as file:
        json.dump(orders_data, file, ensure_ascii=False, indent=2)


def create_order():
    client_name = ask_required_text("Имя клиента: ")
    client_phone = ask_required_text("Телефон клиента: ")
    client = Client(client_name, client_phone)
    order_items = []
    while True:
        service_name = ask_required_text("Название услуги: ")
        try:
            quantity = int(input("Количество: "))
        except ValueError:
            print("Количество должно быть целым числом.")
            continue
        unit_price = input("Цена за одну услугу: ")
        try:
            item = OrderItem(service_name, quantity, unit_price)
        except ValueError as error:
            print(error)
            continue
        order_items.append(item)
        if not ask_yes_no("Добавить ещё одну позицию? (да/нет): "):
            break
    if ask_yes_no("Срочный заказ? (да/нет): "):
        while True:
            surcharge = input("Доплата за срочность: ")
            try:
                new_order = UrgentOrder(client, order_items, surcharge)
            except ValueError as error:
                print(error)
                continue
            break
    else:
        new_order = Order(client, order_items)
    return new_order


def ask_required_text(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Поле не должно быть пустым.")


def ask_yes_no(prompt):
    while True:
        answer = input(prompt).strip().lower()
        if answer == "да":
            return True
        elif answer == "нет":
            return False
        else:
            print("Введите «да» или «нет».")


def select_order(orders):
    if not orders:
        print("Заказов пока нет.")
        return None

    for number, order in enumerate(orders, start=1):
        print(f"{number}. {order.client.name} — {order.status}")

    try:
        order_number = int(input("Номер заказа: "))
    except ValueError:
        print("Введите номер целым числом.")
        return None

    if order_number < 1 or order_number > len(orders):
        print("Заказа с таким номером нет.")
        return None

    return orders[order_number - 1]


def find_orders_by_client(orders, client_name):
    matches = []

    for order in orders:
        if order.client.name.lower() == client_name.lower():
            matches.append(order)

    return matches


def main():
    try:
        with open("orders.json", "r", encoding="utf-8") as file:
            restored_orders_data = json.load(file)
    except FileNotFoundError:
        print("Файл заказов не найден, начинаем с пустого списка.")
        restored_orders_data = []
    except json.JSONDecodeError as error:
        print(f"Не удалось прочитать orders.json: {error}")
        return
    restored_orders = []
    for order_data in restored_orders_data:
        restored_orders.append(order_from_data(order_data))

    while True:
        print("\nМеню заказов")
        print("1 — показать все заказы")
        print("2 — показать заказ")
        print("3 — начать работу над заказом")
        print("4 — завершить заказ")
        print("5 — отменить заказ")
        print("6 — создать заказ")
        print("7 — найти заказы клиента")
        print("0 — выйти")

        choice = input("Выбери действие: ")

        if choice == "1":
            for number, restored_order in enumerate(restored_orders, start=1):
                print(f"\nЗаказ №{number}")
                restored_order.show_info()

        elif choice == "2":
            selected_order = select_order(restored_orders)

            if selected_order is not None:
                selected_order.show_info()
        elif choice == "3":
            selected_order = select_order(restored_orders)
            if selected_order is not None:
                selected_order.start_work()
                save_orders(restored_orders)
        elif choice == "4":
            selected_order = select_order(restored_orders)
            if selected_order is not None:
                selected_order.complete()
                save_orders(restored_orders)
        elif choice == "5":
            selected_order = select_order(restored_orders)
            if selected_order is not None:
                selected_order.cancel()
                save_orders(restored_orders)
                print(f"Текущий статус: {selected_order.status}")
        elif choice == "6":
            new_order = create_order()
            restored_orders.append(new_order)
            save_orders(restored_orders)
            print("Заказ создан и сохранён.")
        elif choice == "7":
            client_name = ask_required_text("Введите имя клиента: ")
            matches = find_orders_by_client(restored_orders, client_name)
            if matches:
                for order in matches:
                    order.show_info()
            else:
                print("Заказы клиента не найдены.")

        elif choice == "0":
            print("Выход из программы")
            break
        else:
            print("Нет такого пункта")


if __name__ == "__main__":
    main()
