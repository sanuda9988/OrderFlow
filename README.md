# OrderFlow

OrderFlow is a command-line Python application that processes a store's customer orders.

It reads the current product inventory and a queue of incoming orders from CSV files, validates each order against business rules, updates stock levels, calculates order totals with customer and bulk discounts, and writes an updated inventory CSV and a JSON summary report.

## Requirements

- Python 3.9 or newer
- `pytest` (only needed to run the tests)

## Setup

Run these commands from the project root folder.

**Windows**

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**macOS / Linux**

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run the application

```
python -m src.main
```

This reads `data/inventory.csv` and `data/orders.csv`, then:

- writes `output/updated_inventory.csv` (final stock levels)
- writes `output/summary.json` (summary report)
- prints a summary to the terminal

Example console output for the sample data:

```
========================================
ORDERFLOW SUMMARY
========================================
Total orders : 8
Fulfilled    : 4
Rejected     : 4
Revenue      : $1185.00
Rejected orders:
  ORD-003: OUT_OF_STOCK
  ORD-006: OUT_OF_STOCK
  ORD-007: INVALID_SKU
  ORD-008: INVALID_QUANTITY
Low stock items:
  KB-101 (Mechanical Keyboard): 2 left
  MN-303 (24-inch Monitor): 0 left
```

## Run the tests

```
pytest
```

## Project structure

```
.
├── data/
│   ├── inventory.csv          input: products and stock
│   └── orders.csv             input: queue of customer orders
├── output/                    generated files go here
├── src/
│   ├── __init__.py
│   ├── file_handler.py        reading CSV files, writing CSV/JSON files
│   ├── processor.py           validation, discounts, stock updates
│   └── main.py                entry point and console summary
├── tests/
│   └── test_processor.py      pytest unit tests
├── conftest.py                lets pytest find the src package
├── requirements.txt
└── README.md
```

## Business rules

**Sequential processing.** Orders are processed one by one, in the order they appear in `data/orders.csv`. When an order is fulfilled, stock is reduced immediately, so later orders are checked against the updated stock.

**Validation.** Each order is checked in this exact order. The first failing check rejects the order, and stock and revenue are left unchanged.

| Step | Check | Reason code |
|------|-------|-------------|
| 1 | `customer_type` is `regular` or `vip` (case-insensitive, whitespace trimmed) | `INVALID_CUSTOMER` |
| 2 | `sku` exists in the inventory | `INVALID_SKU` |
| 3 | `quantity` is a positive whole number | `INVALID_QUANTITY` |
| 4 | available stock is at least `quantity` (no partial shipments) | `OUT_OF_STOCK` |

**Pricing.** The subtotal is `unit price x quantity`. Discounts are additive:

- VIP customers get 10% off
- Orders with quantity of 5 or more get an extra 5% off
- A VIP customer ordering 5 or more units therefore gets 15% off

The order total is rounded to 2 decimal places.

## Output files

`output/updated_inventory.csv` has the columns `sku, name, price, stock` with the final stock counts.

`output/summary.json` contains:

```json
{
  "total_orders": 8,
  "fulfilled_count": 4,
  "rejected_count": 4,
  "total_revenue": 1185.0,
  "rejected_orders": [
    {"order_id": "ORD-003", "reason": "OUT_OF_STOCK"}
  ],
  "low_stock_items": [
    {"sku": "KB-101", "name": "Mechanical Keyboard", "stock": 2}
  ]
}
```

(The lists above are shortened. The real file lists every rejected order and every low stock item.)

`low_stock_items` lists every product whose remaining stock is strictly below 5, including products with 0 left.

## Design notes

- **File I/O is separate from business logic.** `processor.py` never touches the disk, so all the rules can be unit-tested with plain Python dictionaries. Only `file_handler.py` reads and writes files.
- **`Decimal` is used for money** instead of `float`, to avoid floating-point errors. Rounding uses `ROUND_HALF_UP`, the usual shop rounding.
- **The input inventory is never modified.** `process_orders()` works on a deep copy and returns the updated inventory in its result.
- **Validation returns early.** Each check returns as soon as it fails, which guarantees the priority order above.

## Edge cases handled

- Whitespace around any CSV value is trimmed.
- `customer_type` is matched case-insensitively (`" VIP "` works).
- A quantity that is negative, zero, empty, text (`abc`) or a decimal (`2.5`) is rejected as `INVALID_QUANTITY`, and the program continues.
- Missing columns or extra columns in an order row do not crash the program.
- An empty orders file, or one with only a header row, produces a summary with zero orders.
- A malformed row in `inventory.csv` (for example a non-numeric price) is skipped with a warning.
- If an input file is missing, the program prints a clear error message and exits instead of showing a traceback.

## Assumptions

- SKU matching is case-sensitive (surrounding whitespace is trimmed). `kb-101` does not match `KB-101`.
- A quantity must be written as plain digits. Values such as `+3` or `2.0` are treated as invalid.
- `total_revenue` in `summary.json` is written as a JSON number.

## Tests

The tests in `tests/test_processor.py` cover:

- regular, VIP and VIP + bulk pricing
- the bulk discount boundary (quantity 4 versus 5)
- invalid quantities, invalid customers and invalid SKUs
- sequential stock depletion across orders
- rejected orders not changing stock or revenue
- an empty order list
