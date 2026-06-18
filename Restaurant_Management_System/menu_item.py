"""
menu_item.py
------------
Defines the MenuItem class for the Restaurant Management System.

Each MenuItem represents a single item on the restaurant's menu,
storing its ID, name, price, and category. The class supports
display, update, CSV serialisation, and validation operations.


"""

import csv
import os


class MenuItem:
    """
    Represents a single item available on the restaurant menu.

    Attributes
    ----------
    item_id   : str  – Unique identifier for the menu item.
    name      : str  – Display name of the menu item.
    price     : float – Price of the item in USD.
    category  : str  – Category (e.g. 'Burger', 'Pizza', 'Drink').
    """

    # ------------------------------------------------------------------ #
    #  Constructor                                                         #
    # ------------------------------------------------------------------ #

    def __init__(self, item_id: str, name: str, price: float, category: str):
        """
        Initialise a new MenuItem instance.

        Parameters
        ----------
        item_id  : str   – Unique menu item identifier.
        name     : str   – Name of the menu item.
        price    : float – Price of the menu item (must be >= 0).
        category : str   – Category the item belongs to.

        Raises
        ------
        ValueError – If price is negative.
        """
        self.__item_id = item_id
        self.__name = name
        self.__category = category

        # Validate price on construction
        if float(price) < 0:
            raise ValueError(f"Price cannot be negative. Received: {price}")
        self.__price = float(price)

    # ------------------------------------------------------------------ #
    #  Properties (Getters)                                                #
    # ------------------------------------------------------------------ #

    @property
    def item_id(self) -> str:
        """Return the unique item ID."""
        return self.__item_id

    @property
    def name(self) -> str:
        """Return the item name."""
        return self.__name

    @property
    def price(self) -> float:
        """Return the item price."""
        return self.__price

    @property
    def category(self) -> str:
        """Return the item category."""
        return self.__category

    # ------------------------------------------------------------------ #
    #  Method 1 – display_item                                            #
    # ------------------------------------------------------------------ #

    def display_item(self) -> None:
        """
        Print a formatted summary of the menu item to the console.

        Example output
        --------------
        [M001] Burger           | Category: Burger      | Price: $5.99
        """
        print(
            f"[{self.__item_id}] {self.__name:<20} "
            f"| Category: {self.__category:<15} "
            f"| Price: ${self.__price:.2f}"
        )

    # ------------------------------------------------------------------ #
    #  Method 2 – update_price                                            #
    # ------------------------------------------------------------------ #

    def update_price(self, new_price: float) -> bool:
        """
        Update the price of this menu item after validation.

        Parameters
        ----------
        new_price : float – The new price value to set.

        Returns
        -------
        bool – True if update succeeded, False otherwise.
        """
        try:
            new_price = float(new_price)
            if new_price < 0:
                print("  ✗ Error: Price cannot be negative.")
                return False
            self.__price = new_price
            print(f"  ✓ Price updated to ${self.__price:.2f}")
            return True
        except (ValueError, TypeError):
            print("  ✗ Error: Invalid price format. Please enter a number.")
            return False

    # ------------------------------------------------------------------ #
    #  Method 3 – update_name                                             #
    # ------------------------------------------------------------------ #

    def update_name(self, new_name: str) -> bool:
        """
        Update the display name of this menu item.

        Parameters
        ----------
        new_name : str – The new name string.

        Returns
        -------
        bool – True if update succeeded, False otherwise.
        """
        if not new_name or not new_name.strip():
            print("  ✗ Error: Name cannot be empty.")
            return False
        self.__name = new_name.strip()
        print(f"  ✓ Name updated to '{self.__name}'")
        return True

    # ------------------------------------------------------------------ #
    #  Method 4 – update_category                                         #
    # ------------------------------------------------------------------ #

    def update_category(self, new_category: str) -> bool:
        """
        Update the category of this menu item.

        Parameters
        ----------
        new_category : str – The new category string.

        Returns
        -------
        bool – True if update succeeded, False otherwise.
        """
        if not new_category or not new_category.strip():
            print("  ✗ Error: Category cannot be empty.")
            return False
        self.__category = new_category.strip()
        print(f"  ✓ Category updated to '{self.__category}'")
        return True

    # ------------------------------------------------------------------ #
    #  Method 5 – to_csv                                                  #
    # ------------------------------------------------------------------ #

    def to_csv(self) -> list:
        """
        Serialise this menu item to a list suitable for CSV writing.

        Returns
        -------
        list – [item_id, name, price, category]
        """
        return [self.__item_id, self.__name, f"{self.__price:.2f}", self.__category]

    # ------------------------------------------------------------------ #
    #  Method 6 – is_valid                                                #
    # ------------------------------------------------------------------ #

    def is_valid(self) -> bool:
        """
        Validate that all required fields are non-empty and price >= 0.

        Returns
        -------
        bool – True if the item is valid.
        """
        return (
            bool(self.__item_id)
            and bool(self.__name)
            and bool(self.__category)
            and self.__price >= 0
        )

    # ------------------------------------------------------------------ #
    #  Dunder helpers                                                      #
    # ------------------------------------------------------------------ #

    def __str__(self) -> str:
        return (
            f"MenuItem(id={self.__item_id}, name={self.__name}, "
            f"price=${self.__price:.2f}, category={self.__category})"
        )

    def __repr__(self) -> str:
        return self.__str__()


# ------------------------------------------------------------------ #
#  Module-level CSV helpers                                           #
# ------------------------------------------------------------------ #

CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "menu.csv")
CSV_HEADERS = ["item_id", "name", "price", "category"]


def load_menu_from_csv(filepath: str = CSV_PATH) -> list:
    """
    Load all menu items from the CSV file.

    Parameters
    ----------
    filepath : str – Path to the menu CSV file.

    Returns
    -------
    list[MenuItem] – A list of MenuItem objects.
    """
    items = []
    try:
        with open(filepath, newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                try:
                    item = MenuItem(
                        row["item_id"],
                        row["name"],
                        float(row["price"]),
                        row["category"],
                    )
                    items.append(item)
                except (ValueError, KeyError) as exc:
                    print(f"  ⚠ Skipping invalid row: {row} — {exc}")
    except FileNotFoundError:
        print(f"  ⚠ Menu file not found at '{filepath}'. Starting with empty menu.")
    except Exception as exc:
        print(f"  ✗ Unexpected error loading menu: {exc}")
    finally:
        pass  # Resource cleanup handled by context manager
    return items


def save_menu_to_csv(items: list, filepath: str = CSV_PATH) -> None:
    """
    Persist all MenuItem objects to the CSV file.

    Parameters
    ----------
    items    : list[MenuItem] – Items to write.
    filepath : str            – Destination file path.
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(CSV_HEADERS)
            for item in items:
                writer.writerow(item.to_csv())
    except PermissionError:
        print(f"  ✗ Permission denied writing to '{filepath}'.")
    except Exception as exc:
        print(f"  ✗ Error saving menu: {exc}")
    finally:
        pass  # Ensure we always exit cleanly
