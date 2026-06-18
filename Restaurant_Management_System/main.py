"""
main.py
-------
Entry point for the Restaurant Management System.

Provides a continuous console-based, menu-driven interface that
allows staff to manage menu items, customers, and orders. The
application runs in an infinite while loop and exits only when
the user selects the Exit option.


"""

import io
import os
import sys

# Force UTF-8 output on Windows so Unicode characters render correctly
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from restaurant import Restaurant


# ------------------------------------------------------------------ #
#  ANSI colour helpers (gracefully disabled on Windows cmd if needed)  #
# ------------------------------------------------------------------ #

def _c(code: str, text: str) -> str:
    """Wrap text in an ANSI colour code (if terminal supports it)."""
    try:
        if sys.stdout.isatty() or os.name == "nt":
            return f"\033[{code}m{text}\033[0m"
    except Exception:
        pass
    return text


CYAN   = lambda t: _c("96", t)
GREEN  = lambda t: _c("92", t)
YELLOW = lambda t: _c("93", t)
RED    = lambda t: _c("91", t)
BOLD   = lambda t: _c("1",  t)


# ------------------------------------------------------------------ #
#  Banner                                                              #
# ------------------------------------------------------------------ #

BANNER = """
  +======================================================+
  |      RESTAURANT MANAGEMENT SYSTEM                    |
  +======================================================+
"""


# ------------------------------------------------------------------ #
#  Utility helpers                                                     #
# ------------------------------------------------------------------ #

def clear_screen() -> None:
    """Clear the console screen (cross-platform)."""
    os.system("cls" if os.name == "nt" else "clear")


def pause() -> None:
    """Pause execution until the user presses Enter."""
    input("\n  Press Enter to return to the menu...")


def get_input(prompt: str, allow_empty: bool = False) -> str:
    """
    Prompt the user for a string input with optional empty-check.

    Parameters
    ----------
    prompt      : str  – Prompt text to display.
    allow_empty : bool – If True, empty input is allowed.

    Returns
    -------
    str – The stripped user input.
    """
    while True:
        value = input(f"  {prompt}: ").strip()
        if value or allow_empty:
            return value
        print("  ✗ Input cannot be empty. Please try again.")


def get_float_input(prompt: str) -> float:
    """
    Prompt the user for a valid floating-point number.

    Keeps asking until a valid non-negative float is entered.

    Parameters
    ----------
    prompt : str – Prompt text to display.

    Returns
    -------
    float – The validated float value.
    """
    while True:
        try:
            value = float(input(f"  {prompt}: ").strip())
            if value < 0:
                print("  ✗ Value cannot be negative. Please try again.")
            else:
                return value
        except ValueError:
            print("  ✗ Invalid number format. Please enter a numeric value.")


def get_int_choice(prompt: str, low: int, high: int) -> int:
    """
    Prompt the user for an integer choice within [low, high].

    Parameters
    ----------
    prompt : str – Prompt text.
    low    : int – Minimum valid value.
    high   : int – Maximum valid value.

    Returns
    -------
    int – The validated integer choice.
    """
    while True:
        try:
            choice = int(input(f"  {prompt}: ").strip())
            if low <= choice <= high:
                return choice
            print(f"  ✗ Please enter a number between {low} and {high}.")
        except ValueError:
            print("  ✗ Invalid input. Please enter a whole number.")


# ================================================================== #
#  MENU MANAGEMENT SCREENS                                             #
# ================================================================== #

def screen_add_menu_item(restaurant: Restaurant) -> None:
    """Collect details and add a new menu item."""
    print(BOLD("\n  — Add Menu Item —"))
    name     = get_input("Item Name")
    price    = get_float_input("Price (e.g. 9.99)")
    category = get_input("Category (e.g. Burger, Pizza, Drink)")
    restaurant.add_menu_item(name, price, category)


def screen_view_menu(restaurant: Restaurant) -> None:
    """Display the full menu."""
    restaurant.view_menu()


def screen_update_menu_item(restaurant: Restaurant) -> None:
    """Prompt for item ID and update chosen fields."""
    print(BOLD("\n  — Update Menu Item —"))
    restaurant.view_menu()
    item_id = get_input("Enter Item ID to update (e.g. M001)")

    print("  Leave blank to keep the current value.")
    new_name  = input("  New Name     : ").strip() or None
    new_cat   = input("  New Category : ").strip() or None

    new_price = None
    price_str = input("  New Price    : ").strip()
    if price_str:
        try:
            new_price = float(price_str)
        except ValueError:
            print("  ✗ Invalid price — keeping existing price.")

    restaurant.update_menu_item(item_id, new_name, new_price, new_cat)


def screen_delete_menu_item(restaurant: Restaurant) -> None:
    """Prompt for item ID and delete it."""
    print(BOLD("\n  — Delete Menu Item —"))
    restaurant.view_menu()
    item_id = get_input("Enter Item ID to delete (e.g. M001)")

    confirm = input(f"  Confirm delete '{item_id}'? (yes/no): ").strip().lower()
    if confirm == "yes":
        restaurant.delete_menu_item(item_id)
    else:
        print("  ✗ Deletion cancelled.")


def screen_search_menu(restaurant: Restaurant) -> None:
    """Search menu by keyword."""
    print(BOLD("\n  — Search Menu —"))
    keyword = get_input("Enter search keyword")
    restaurant.search_menu_item(keyword)


# ================================================================== #
#  CUSTOMER MANAGEMENT SCREENS                                         #
# ================================================================== #

def screen_register_customer(restaurant: Restaurant) -> None:
    """Collect details and register a new customer."""
    print(BOLD("\n  — Register Customer —"))
    name  = get_input("Full Name")
    phone = get_input("Phone Number")
    email = get_input("Email Address")
    restaurant.register_customer(name, phone, email)


def screen_view_customers(restaurant: Restaurant) -> None:
    """Display all registered customers."""
    restaurant.view_customers()


def screen_search_customer(restaurant: Restaurant) -> None:
    """Search customers by name or ID."""
    print(BOLD("\n  — Search Customer —"))
    keyword = get_input("Enter name or customer ID")
    restaurant.search_customer(keyword)


# ================================================================== #
#  ORDER MANAGEMENT SCREENS                                            #
# ================================================================== #

def screen_create_order(restaurant: Restaurant) -> None:
    """
    Full interactive order creation flow:
    1. Select customer
    2. Add menu items in a loop
    3. Confirm order
    """
    print(BOLD("\n  — Create New Order —"))
    restaurant.view_customers()
    customer_id = get_input("Enter Customer ID (e.g. C001)")

    order = restaurant.create_order(customer_id)
    if order is None:
        return

    # Item selection loop
    while True:
        print(BOLD("\n  — Add Items to Order —"))
        restaurant.view_menu()
        print("  (Type 'done' to finish adding items)")
        item_id = input("  Enter Item ID to add: ").strip()

        if item_id.lower() == "done":
            break
        elif item_id:
            restaurant.add_item_to_order(order.order_id, item_id)
        else:
            print("  ✗ Please enter a valid Item ID or 'done'.")

    # Show current order summary
    order.display_order()

    confirm = input("  Confirm this order? (yes/no): ").strip().lower()
    if confirm != "yes":
        order.cancel_order()
        print("  ✗ Order has been cancelled.")
    else:
        print(f"  ✓ Order '{order.order_id}' confirmed and saved.")


def screen_view_orders(restaurant: Restaurant) -> None:
    """Display all orders."""
    print(BOLD("\n  — View Orders —"))
    print("  Filter by status: 1) All  2) Open  3) Billed  4) Cancelled")
    choice = get_int_choice("Select filter", 1, 4)

    status_map = {1: None, 2: "open", 3: "billed", 4: "cancelled"}
    restaurant.view_orders(status_map[choice])


def screen_generate_bill(restaurant: Restaurant) -> None:
    """Generate the bill for a selected order."""
    print(BOLD("\n  — Generate Bill —"))
    restaurant.view_orders(status_filter="open")
    order_id = get_input("Enter Order ID to bill (e.g. ORD001)")
    restaurant.generate_bill(order_id)


def screen_view_report(restaurant: Restaurant) -> None:
    """Display the sales report."""
    restaurant.view_reports()


# ================================================================== #
#  MAIN MENU                                                           #
# ================================================================== #

MENU_OPTIONS = [
    ("MENU MANAGEMENT", None),
    ("Add Menu Item",      screen_add_menu_item),
    ("View Menu",          screen_view_menu),
    ("Update Menu Item",   screen_update_menu_item),
    ("Delete Menu Item",   screen_delete_menu_item),
    ("Search Menu Item",   screen_search_menu),
    ("CUSTOMER MANAGEMENT", None),
    ("Register Customer",  screen_register_customer),
    ("View Customers",     screen_view_customers),
    ("Search Customer",    screen_search_customer),
    ("ORDER MANAGEMENT",   None),
    ("Create Order",       screen_create_order),
    ("View Orders",        screen_view_orders),
    ("Generate Bill",      screen_generate_bill),
    ("View Sales Report",  screen_view_report),
    ("EXIT",               None),
]


def print_main_menu() -> None:
    """Print the interactive main menu with numbered options."""
    print(BOLD("\n  +==============================+"))
    print(BOLD("  |         MAIN  MENU           |"))
    print(BOLD("  +==============================+"))

    option_num = 0
    for label, func in MENU_OPTIONS:
        if func is None and label not in ("EXIT",):
            # Section header
            print(f"\n  {CYAN('--- ' + label + ' ---')}")
        elif label == "EXIT":
            print(f"\n  {RED('  0.')} {label}")
        else:
            option_num += 1
            print(f"  {YELLOW(f'  {option_num}.')} {label}")


def run_main_menu(restaurant: Restaurant) -> None:
    """
    Run the main application loop.

    Displays the menu, reads user choice, and dispatches to the
    appropriate screen handler. Continues until Exit (0) is chosen.

    Parameters
    ----------
    restaurant : Restaurant – The active restaurant instance.
    """
    # Build a flat callable list for dispatch (exclude section headers)
    callable_options = [
        (label, func)
        for label, func in MENU_OPTIONS
        if func is not None or label == "EXIT"
    ]
    max_option = len(callable_options) - 1  # EXIT is 0, options 1..N

    while True:
        try:
            print_main_menu()
            choice_str = input(f"\n  {BOLD('Enter your choice (0-' + str(max_option) + ')')}: ").strip()

            if not choice_str:
                continue

            choice = int(choice_str)

            if choice == 0:
                print(GREEN("\n  Thank you for using the Restaurant Management System. Goodbye!\n"))
                break
            elif 1 <= choice <= max_option:
                label, func = callable_options[choice - 1]
                clear_screen()
                print(BANNER)
                if func:
                    func(restaurant)
                pause()
            else:
                print(RED(f"  Invalid choice. Please enter 0-{max_option}."))

        except ValueError:
            print(RED("  ✗ Invalid input. Please enter a number."))
        except KeyboardInterrupt:
            print(GREEN("\n\n  Exiting... Goodbye!\n"))
            break
        except Exception as exc:
            print(RED(f"  ✗ An unexpected error occurred: {exc}"))
            pause()


# ================================================================== #
#  Application Entry Point                                             #
# ================================================================== #

def main() -> None:
    """
    Main entry point for the Restaurant Management System.

    Initialises the Restaurant object (which loads all CSV data),
    then starts the interactive menu loop.
    """
    clear_screen()
    print(BANNER)

    try:
        # Initialise the restaurant (loads all CSV data)
        restaurant = Restaurant("The Grand Bistro")
    except Exception as exc:
        print(RED(f"  ✗ Fatal: Could not initialise restaurant system: {exc}"))
        sys.exit(1)

    # Launch the main menu loop
    run_main_menu(restaurant)


if __name__ == "__main__":
    main()
