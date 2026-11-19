import copy
from decimal import Decimal, ROUND_HALF_UP


def parse_quantity(text):
    """Return a positive int, or None if text is not a valid positive integer."""
    text = (text or "").strip()
    if not (text.isascii() and text.isdigit()):
        return None
    quantity = int(text)
    if quantity <= 0:
        return None
    return quantity


def calculate_total(price, quantity, customer_type):
    discount = Decimal("0")
    if customer_type == "vip":
        discount += Decimal("0.10")
    if quantity >= 5:
        discount += Decimal("0.05")
    total = price * quantity * (1 - discount)
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def validate_order(order, inventory):
    """Return (reason, None) if rejected, or (None, clean_data) if valid."""
    customer_type = order.get("customer_type", "").strip().lower()
    if customer_type not in ("regular", "vip"):
        return "INVALID_CUSTOMER", None

    sku = order.get("sku", "").strip()
    if sku not in inventory:
        return "INVALID_SKU", None

    quantity = parse_quantity(order.get("quantity"))
    if quantity is None:
        return "INVALID_QUANTITY", None

    if inventory[sku]["stock"] < quantity:
        return "OUT_OF_STOCK", None

    return None, {"customer_type": customer_type, "sku": sku, "quantity": quantity}


def get_low_stock_items(inventory):
    items = []
    for sku, item in inventory.items():
        if item["stock"] < 5:
            items.append({"sku": sku, "name": item["name"], "stock": item["stock"]})
    return items


def process_orders(inventory, orders):
    inventory = copy.deepcopy(inventory)  
    fulfilled = 0
    rejected = []
    seen_ids = set()
    revenue = Decimal("0.00")

    for order in orders:
        order_id = order.get("order_id", "").strip()
        if order_id in seen_ids:
            rejected.append({"order_id": order_id, "reason": "DUPLICATE_ORDER_ID"})
            continue
        seen_ids.add(order_id)

        reason, data = validate_order(order, inventory)
        if reason is not None:
            rejected.append({"order_id": order.get("order_id", ""), "reason": reason})
            continue

        item = inventory[data["sku"]]
        revenue += calculate_total(item["price"], data["quantity"], data["customer_type"])
        item["stock"] -= data["quantity"]
        fulfilled += 1

    return {
        "total_orders": len(orders),
        "fulfilled_count": fulfilled,
        "rejected_count": len(rejected),
        "total_revenue": revenue,
        "rejected_orders": rejected,
        "inventory": inventory,
    }