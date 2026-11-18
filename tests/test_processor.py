from decimal import Decimal

from src.processor import calculate_total, parse_quantity, process_orders


def make_inventory():
    return {
        "KB-101": {"name": "Keyboard", "price": Decimal("100.00"), "stock": 10},
        "MN-303": {"name": "Monitor", "price": Decimal("200.00"), "stock": 2},
    }


def make_order(order_id, customer, sku, qty):
    return {"order_id": order_id, "customer_type": customer, "sku": sku, "quantity": qty}


def test_regular_customer_pays_full_price():
    assert calculate_total(Decimal("100"), 3, "regular") == Decimal("300.00")


def test_vip_gets_10_percent():
    assert calculate_total(Decimal("100"), 4, "vip") == Decimal("360.00")


def test_vip_bulk_gets_15_percent():
    assert calculate_total(Decimal("100"), 5, "vip") == Decimal("425.00")


def test_bulk_boundary_quantity_5():
    assert calculate_total(Decimal("100"), 4, "regular") == Decimal("400.00")
    assert calculate_total(Decimal("100"), 5, "regular") == Decimal("475.00")


def test_invalid_quantities():
    for bad in ["-2", "0", "abc", "2.5", "", None]:
        assert parse_quantity(bad) is None
    assert parse_quantity(" 7 ") == 7


def test_invalid_customer_and_sku():
    result = process_orders(make_inventory(), [
        make_order("O1", "gold", "KB-101", "1"),
        make_order("O2", "vip", "XX-999", "1"),
    ])
    reasons = [r["reason"] for r in result["rejected_orders"]]
    assert reasons == ["INVALID_CUSTOMER", "INVALID_SKU"]


def test_sequential_stock_depletion():
    result = process_orders(make_inventory(), [
        make_order("O1", "regular", "MN-303", "2"),
        make_order("O2", "regular", "MN-303", "1"),
    ])
    assert result["fulfilled_count"] == 1
    assert result["rejected_orders"] == [{"order_id": "O2", "reason": "OUT_OF_STOCK"}]
    assert result["inventory"]["MN-303"]["stock"] == 0


def test_rejected_order_does_not_change_stock_or_revenue():
    result = process_orders(make_inventory(), [make_order("O1", "regular", "KB-101", "99")])
    assert result["inventory"]["KB-101"]["stock"] == 10
    assert result["total_revenue"] == Decimal("0.00")


def test_empty_orders_does_not_crash():
    result = process_orders(make_inventory(), [])
    assert result["total_orders"] == 0