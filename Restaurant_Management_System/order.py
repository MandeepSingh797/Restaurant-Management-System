"""
order.py
--------
Defines the Order class for the Restaurant Management System.

An Order tracks which customer placed it, which menu items were
selected, and computes the running total. Orders are persisted to
a CSV file for historical reporting.


"""

import csv
import os
from datetime import datetime


class Order:
    """
    Represents a single customer order within the restaurant system.

    Attributes
    ----------
    order_id    : str            – Unique order identifier.
    customer_id : str            – ID of the customer who placed the order.
    items       : list[dict]     – List of ordered items; each dict holds
                                   item_id, name, and price.
    timestamp   : str            – ISO-format date-time when order was created.
    status      : str            – Current status ('open', 'billed', 'cancelled').
    """

    # Valid order status values
    VALID_STATUSES = ("open", "billed", "cancelled")

    # ------------------------------------------------------------------ #
    #  Constructor                                                         #
    # ------------------------------------------------------------------ #

    def __init__(
        self,
        order_id: str,
        customer_id: str,
        items: list = None,
        timestamp: str = None,
        status: str = "open",
    ):
        """
        Initialise a new Order instance.

        Parameters
        ----------
        order_id    : str  – Unique order identifier (e.g. 'ORD001').
        customer_id : str  – ID of the customer who placed the order.
        items       : list – Pre-existing item list (used when loading from CSV).
        timestamp   : str  – Creation timestamp; defaults to now.
        status      : str  – Order status; defaults to 'open'.

        Raises
        ------
        ValueError – If order_id or customer_id is empty.
        """
        if not order_id or not order_id.strip():
            raise ValueError("Order ID cannot be empty.")
        if not customer_id or not customer_id.strip():
            raise ValueError("Customer ID cannot be empty.")

        self.__order_id = order_id.strip()
        self.__customer_id = customer_id.strip()
        self.__items = items if items is not None else []
        self.__timestamp = timestamp if timestamp else datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self.__status = status if status in self.VALID_STATUSES else "open"

    # ------------------------------------------------------------------ #
    #  Properties (Getters)                                                #
    # ------------------------------------------------------------------ #

    @property
    def order_id(self) -> str:
        """Return the unique order ID."""
        return self.__order_id

    @property
    def customer_id(self) -> str:
        """Return the customer ID associated with this order."""
        return self.__customer_id

    @property
    def items(self) -> list:
        """Return a copy of the ordered items list."""
        return list(self.__items)

    @property
    def timestamp(self) -> str:
        """Return the order creation timestamp."""
        return self.__timestamp

    @property
    def status(self) -> str:
        """Return the current order status."""
        return self.__status

    # ------------------------------------------------------------------ #
    #  Method 1 – add_item                                                #
    # ------------------------------------------------------------------ #

    def add_item(self, menu_item) -> bool:
        """
        Add a MenuItem to this order.

        Parameters
        ----------
        menu_item : MenuItem – The item to add.

        Returns
        -------
        bool – True if added successfully.
        """
        if self.__status != "open":
            print(f"  ✗ Cannot modify a '{self.__status}' order.")
            return False

        self.__items.append(
            {
                "item_id": menu_item.item_id,
                "name": menu_item.name,
                "price": menu_item.price,
            }
        )
        print(f"  ✓ '{menu_item.name}' (${menu_item.price:.2f}) added to order.")
        return True

    # ------------------------------------------------------------------ #
    #  Method 2 – remove_item                                             #
    # ------------------------------------------------------------------ #

    def remove_item(self, item_id: str) -> bool:
        """
        Remove the first occurrence of a menu item (by item_id) from this order.

        Parameters
        ----------
        item_id : str – The item ID to remove.

        Returns
        -------
        bool – True if the item was found and removed, False otherwise.
        """
        if self.__status != "open":
            print(f"  ✗ Cannot modify a '{self.__status}' order.")
            return False

        for index, item in enumerate(self.__items):
            if item["item_id"] == item_id:
                removed = self.__items.pop(index)
                print(f"  ✓ '{removed['name']}' removed from order.")
                return True

        print(f"  ✗ Item ID '{item_id}' not found in this order.")
        return False

    # ------------------------------------------------------------------ #
    #  Method 3 – calculate_total                                         #
    # ------------------------------------------------------------------ #

    def calculate_total(self) -> float:
        """
        Calculate and return the total price of all items in the order.

        Returns
        -------
        float – Sum of all item prices.
        """
        total = 0.0
        for item in self.__items:
            total += float(item["price"])
        return round(total, 2)

    # ------------------------------------------------------------------ #
    #  Method 4 – display_order                                           #
    # ------------------------------------------------------------------ #

    def display_order(self) -> None:
        """
        Print a formatted summary of this order to the console.

        Shows order ID, customer ID, status, timestamp, all items,
        and the running total.
        """
        separator = "=" * 50
        print(separator)
        print(f"  Order ID   : {self.__order_id}")
        print(f"  Customer   : {self.__customer_id}")
        print(f"  Status     : {self.__status.upper()}")
        print(f"  Date/Time  : {self.__timestamp}")
        print(separator)

        if not self.__items:
            print("  (No items in this order)")
        else:
            for item in self.__items:
                print(f"  {item['name']:<25} ${float(item['price']):.2f}")

        print(separator)
        print(f"  {'TOTAL':<25} ${self.calculate_total():.2f}")
        print(separator)

    # ------------------------------------------------------------------ #
    #  Method 5 – generate_bill                                           #
    # ------------------------------------------------------------------ #

    def generate_bill(self, customer_name: str = "") -> None:
        """
        Print a formatted customer-facing receipt/bill to the console.

        Parameters
        ----------
        customer_name : str – Optional customer name to display on bill.
        """
        separator = "=" * 44
        print(f"\n{separator}")
        print("           🍽  RESTAURANT BILL  🍽")
        print(separator)
        print(f"  Customer  : {customer_name if customer_name else self.__customer_id}")
        print(f"  Order ID  : {self.__order_id}")
        print(f"  Date/Time : {self.__timestamp}")
        print(separator)

        if not self.__items:
            print("  (No items in this order)")
        else:
            for item in self.__items:
                print(f"  {item['name']:<28} ${float(item['price']):.2f}")

        print(separator)
        print(f"  {'TOTAL':<28} ${self.calculate_total():.2f}")
        print(separator)
        print("       Thank you for dining with us!")
        print(f"{separator}\n")

        # Mark order as billed
        self.__status = "billed"

    # ------------------------------------------------------------------ #
    #  Method 6 – to_csv                                                  #
    # ------------------------------------------------------------------ #

    def to_csv(self) -> list:
        """
        Serialise this order to a list suitable for CSV writing.

        Items are encoded as a pipe-separated string:
          item_id:name:price|item_id:name:price|...

        Returns
        -------
        list – [order_id, customer_id, items_str, total, timestamp, status]
        """
        items_str = "|".join(
            f"{i['item_id']}:{i['name']}:{i['price']}" for i in self.__items
        )
        return [
            self.__order_id,
            self.__customer_id,
            items_str,
            f"{self.calculate_total():.2f}",
            self.__timestamp,
            self.__status,
        ]

    # ------------------------------------------------------------------ #
    #  Method 7 – cancel_order                                            #
    # ------------------------------------------------------------------ #

    def cancel_order(self) -> bool:
        """
        Mark this order as cancelled if it is currently open.

        Returns
        -------
        bool – True if successfully cancelled.
        """
        if self.__status == "open":
            self.__status = "cancelled"
            print(f"  ✓ Order '{self.__order_id}' has been cancelled.")
            return True
        else:
            print(f"  ✗ Order is already '{self.__status}' and cannot be cancelled.")
            return False

    # ------------------------------------------------------------------ #
    #  Dunder helpers                                                      #
    # ------------------------------------------------------------------ #

    def __str__(self) -> str:
        return (
            f"Order(id={self.__order_id}, customer={self.__customer_id}, "
            f"items={len(self.__items)}, total=${self.calculate_total():.2f}, "
            f"status={self.__status})"
        )

    def __repr__(self) -> str:
        return self.__str__()


# ------------------------------------------------------------------ #
#  Module-level CSV helpers                                           #
# ------------------------------------------------------------------ #

CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "orders.csv")
CSV_HEADERS = ["order_id", "customer_id", "items", "total", "timestamp", "status"]


def load_orders_from_csv(filepath: str = CSV_PATH) -> list:
    """
    Load all orders from the CSV file.

    Parameters
    ----------
    filepath : str – Path to the orders CSV file.

    Returns
    -------
    list[Order] – A list of Order objects.
    """
    orders = []
    try:
        with open(filepath, newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                try:
                    # Decode pipe-separated items string back to list of dicts
                    items = []
                    if row.get("items"):
                        for entry in row["items"].split("|"):
                            parts = entry.split(":")
                            if len(parts) == 3:
                                items.append(
                                    {
                                        "item_id": parts[0],
                                        "name": parts[1],
                                        "price": float(parts[2]),
                                    }
                                )
                    order = Order(
                        row["order_id"],
                        row["customer_id"],
                        items,
                        row.get("timestamp"),
                        row.get("status", "open"),
                    )
                    orders.append(order)
                except (ValueError, KeyError) as exc:
                    print(f"  ⚠ Skipping invalid order row: {row} — {exc}")
    except FileNotFoundError:
        print(f"  ⚠ Orders file not found at '{filepath}'. Starting fresh.")
    except Exception as exc:
        print(f"  ✗ Unexpected error loading orders: {exc}")
    finally:
        pass  # Context manager handles file closure
    return orders


def save_orders_to_csv(orders: list, filepath: str = CSV_PATH) -> None:
    """
    Persist all Order objects to the CSV file.

    Parameters
    ----------
    orders   : list[Order] – Orders to write.
    filepath : str         – Destination file path.
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(CSV_HEADERS)
            for order in orders:
                writer.writerow(order.to_csv())
    except PermissionError:
        print(f"  ✗ Permission denied writing to '{filepath}'.")
    except Exception as exc:
        print(f"  ✗ Error saving orders: {exc}")
    finally:
        pass  # Ensure clean exit
