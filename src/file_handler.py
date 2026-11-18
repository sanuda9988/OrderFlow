import csv
import json
from decimal import Decimal

def read_inventory(path):
    inventory = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            sku = row["sku"].strip()
            inventory[sku] = {
                "name": row["name"].strip(),
                "price": Decimal(row["price"].strip()),
                "stock": int(row["stock"].strip()),
            }

    return inventory


def read_orders(path):
    orders = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            clean = {}
            for key, value in row.items():
                if key is not None:
                    clean[key.strip()] = (value or "").strip()
            
            orders.append(clean)

    return orders


def write_inventory(path, inventory):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sku", "name", "price", "stock"])
        for sku, item in inventory.items():
            writer.writerow([sku, item["name"], f"{item['price']:.2f}", item["stock"]])


def write_summary(path, summary):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


