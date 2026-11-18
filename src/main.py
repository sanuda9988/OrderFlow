from pathlib import Path

from .file_handler import read_inventory, read_orders, write_inventory, write_summary
from .processor import process_orders, get_low_stock_items

BASE = Path(__file__).resolve().parent.parent


def main():
    inventory = read_inventory(BASE / "data" / "inventory.csv")
    orders = read_orders(BASE / "data" / "orders.csv")

    result = process_orders(inventory, orders)
    low_stock = get_low_stock_items(result["inventory"])

    (BASE / "output").mkdir(exist_ok=True)
    write_inventory(BASE / "output" / "updated_inventory.csv", result["inventory"])
    write_summary(BASE / "output" / "summary.json", {
        "total_orders": result["total_orders"],
        "fulfilled_count": result["fulfilled_count"],
        "rejected_count": result["rejected_count"],
        "total_revenue": float(result["total_revenue"]),
        "rejected_orders": result["rejected_orders"],
        "low_stock_items": low_stock,
    })    
        
    print("=" * 40)
    print("ORDERFLOW SUMMARY")
    print("=" * 40)
    print(f"Total orders : {result['total_orders']}")
    print(f"Fulfilled    : {result['fulfilled_count']}")
    print(f"Rejected     : {result['rejected_count']}")
    print(f"Revenue      : ${result['total_revenue']:.2f}")
    print("Rejected orders:")
    for r in result["rejected_orders"]:
        print(f"  {r['order_id']}: {r['reason']}")
    print("Low stock items:")
    for item in low_stock:
        print(f"  {item['sku']} ({item['name']}): {item['stock']} left")

        

if __name__ == "__main__":
    main()