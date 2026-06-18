"""
restaurant.py
-------------
Defines the Restaurant class — the central controller for the
Restaurant Management System.

The Restaurant class owns the in-memory data stores (menu, customers,
orders) and co-ordinates all CRUD operations and report generation.
All changes are automatically persisted to CSV files.


"""

import os

from menu_item import (
    MenuItem,
    load_menu_from_csv,
    save_menu_to_csv,
)
from customer import (
    Customer,
    load_customers_from_csv,
    save_customers_to_csv,
)
from order import (
    Order,
    load_orders_from_csv,
    save_orders_to_csv,
)


class Restaurant:
    """
    Central controller class for the Restaurant Management System.

    Manages the menu, registered customers, and order history.
    Provides high-level operations that wrap the underlying domain
    classes and persist all changes to CSV files automatically.

    Attributes
    ----------
    name       : str              – Name of the restaurant.
    _menu      : list[MenuItem]   – In-memory menu item store.
    _customers : list[Customer]   – In-memory customer store.
    _orders    : list[Order]      – In-memory order history store.
    """

    # ------------------------------------------------------------------ #
    #  Constructor                                                         #
    # ------------------------------------------------------------------ #

    def __init__(self, name: str, data_dir: str = None):
        """
        Initialise the Restaurant and load all data from CSV files.

        Parameters
        ----------
        name     : str – Display name of the restaurant.
        data_dir : str – Optional custom path to the data directory.
        """
        self.__name = name

        # Resolve data directory paths
        base = data_dir if data_dir else os.path.join(
            os.path.dirname(__file__), "data"
        )
        self.__menu_csv = os.path.join(base, "menu.csv")
        self.__customers_csv = os.path.join(base, "customers.csv")
        self.__orders_csv = os.path.join(base, "orders.csv")

        # Load persisted data on startup
        self.__menu: list[MenuItem] = load_menu_from_csv(self.__menu_csv)
        self.__customers: list[Customer] = load_customers_from_csv(
            self.__customers_csv
        )
        self.__orders: list[Order] = load_orders_from_csv(self.__orders_csv)

        print(f"\n  ✓ {self.__name} system loaded.")
        print(
            f"    Menu items: {len(self.__menu)}  |  "
            f"Customers: {len(self.__customers)}  |  "
            f"Orders: {len(self.__orders)}"
        )

    # ------------------------------------------------------------------ #
    #  Properties                                                          #
    # ------------------------------------------------------------------ #

    @property
    def name(self) -> str:
        """Return the restaurant name."""
        return self.__name

    @property
    def menu(self) -> list:
        """Return a copy of the menu list."""
        return list(self.__menu)

    @property
    def customers(self) -> list:
        """Return a copy of the customers list."""
        return list(self.__customers)

    @property
    def orders(self) -> list:
        """Return a copy of the orders list."""
        return list(self.__orders)

    # ------------------------------------------------------------------ #
    #  Internal ID generators                                              #
    # ------------------------------------------------------------------ #

    def __next_item_id(self) -> str:
        """Generate the next sequential menu item ID."""
        if not self.__menu:
            return "M001"
        # Extract numeric parts and find max
        nums = []
        for item in self.__menu:
            try:
                nums.append(int(item.item_id[1:]))
            except (ValueError, IndexError):
                pass
        return f"M{(max(nums) + 1):03d}" if nums else "M001"

    def __next_customer_id(self) -> str:
        """Generate the next sequential customer ID."""
        if not self.__customers:
            return "C001"
        nums = []
        for cust in self.__customers:
            try:
                nums.append(int(cust.customer_id[1:]))
            except (ValueError, IndexError):
                pass
        return f"C{(max(nums) + 1):03d}" if nums else "C001"

    def __next_order_id(self) -> str:
        """Generate the next sequential order ID."""
        if not self.__orders:
            return "ORD001"
        nums = []
        for order in self.__orders:
            try:
                nums.append(int(order.order_id[3:]))
            except (ValueError, IndexError):
                pass
        return f"ORD{(max(nums) + 1):03d}" if nums else "ORD001"

    # ================================================================== #
    #  MENU MANAGEMENT                                                     #
    # ================================================================== #

    # ------------------------------------------------------------------ #
    #  Method 1 – add_menu_item                                           #
    # ------------------------------------------------------------------ #

    def add_menu_item(self, name: str, price: float, category: str) -> MenuItem:
        """
        Create and add a new MenuItem to the menu.

        Parameters
        ----------
        name     : str   – Item name.
        price    : float – Item price.
        category : str   – Item category.

        Returns
        -------
        MenuItem – The newly created item, or None on failure.
        """
        try:
            item_id = self.__next_item_id()
            new_item = MenuItem(item_id, name, price, category)
            self.__menu.append(new_item)
            save_menu_to_csv(self.__menu, self.__menu_csv)
            print(f"  ✓ Menu item '{name}' added with ID '{item_id}'.")
            return new_item
        except ValueError as exc:
            print(f"  ✗ Could not add menu item: {exc}")
            return None

    # ------------------------------------------------------------------ #
    #  Method 2 – view_menu                                               #
    # ------------------------------------------------------------------ #

    def view_menu(self, category_filter: str = None) -> None:
        """
        Display all menu items, optionally filtered by category.

        Parameters
        ----------
        category_filter : str – If provided, only show items in this category.
        """
        separator = "-" * 65
        title = (
            f"{self.__name} — Menu"
            if not category_filter
            else f"{self.__name} — Menu ({category_filter})"
        )
        print(f"\n  {title}")
        print(f"  {separator}")

        # Filter items if category specified
        items_to_show = [
            item
            for item in self.__menu
            if (not category_filter or
                item.category.lower() == category_filter.lower())
        ]

        if not items_to_show:
            print("  (No items found)")
        else:
            for item in items_to_show:
                item.display_item()

        print(f"  {separator}")
        print(f"  Total items displayed: {len(items_to_show)}\n")

    # ------------------------------------------------------------------ #
    #  Method 3 – update_menu_item                                        #
    # ------------------------------------------------------------------ #

    def update_menu_item(
        self,
        item_id: str,
        new_name: str = None,
        new_price: float = None,
        new_category: str = None,
    ) -> bool:
        """
        Update attributes of an existing menu item.

        Parameters
        ----------
        item_id      : str   – ID of the item to update.
        new_name     : str   – Optional new name.
        new_price    : float – Optional new price.
        new_category : str   – Optional new category.

        Returns
        -------
        bool – True if the item was found and updated.
        """
        item = self.__find_menu_item(item_id)
        if item is None:
            print(f"  ✗ Menu item '{item_id}' not found.")
            return False

        updated = False
        if new_name:
            updated = item.update_name(new_name) or updated
        if new_price is not None:
            updated = item.update_price(new_price) or updated
        if new_category:
            updated = item.update_category(new_category) or updated

        if updated:
            save_menu_to_csv(self.__menu, self.__menu_csv)
        return updated

    # ------------------------------------------------------------------ #
    #  Method 4 – delete_menu_item                                        #
    # ------------------------------------------------------------------ #

    def delete_menu_item(self, item_id: str) -> bool:
        """
        Remove a menu item by its ID.

        Parameters
        ----------
        item_id : str – ID of the item to delete.

        Returns
        -------
        bool – True if the item was found and removed.
        """
        for index, item in enumerate(self.__menu):
            if item.item_id == item_id:
                removed = self.__menu.pop(index)
                save_menu_to_csv(self.__menu, self.__menu_csv)
                print(f"  ✓ Menu item '{removed.name}' (ID: {item_id}) deleted.")
                return True

        print(f"  ✗ Menu item '{item_id}' not found.")
        return False

    # ------------------------------------------------------------------ #
    #  Method 5 – search_menu_item                                        #
    # ------------------------------------------------------------------ #

    def search_menu_item(self, keyword: str) -> list:
        """
        Search for menu items whose name or category contains the keyword.

        Parameters
        ----------
        keyword : str – Case-insensitive search term.

        Returns
        -------
        list[MenuItem] – Matching menu items.
        """
        keyword_lower = keyword.lower()
        results = [
            item
            for item in self.__menu
            if keyword_lower in item.name.lower()
            or keyword_lower in item.category.lower()
        ]

        print(f"\n  Search results for '{keyword}':")
        if results:
            for item in results:
                item.display_item()
        else:
            print("  (No matching items found)")

        return results

    # ------------------------------------------------------------------ #
    #  Internal helper – find menu item by ID                             #
    # ------------------------------------------------------------------ #

    def __find_menu_item(self, item_id: str):
        """Return the MenuItem with the given ID, or None."""
        for item in self.__menu:
            if item.item_id == item_id:
                return item
        return None

    # ================================================================== #
    #  CUSTOMER MANAGEMENT                                                 #
    # ================================================================== #

    # ------------------------------------------------------------------ #
    #  Method 6 – register_customer                                       #
    # ------------------------------------------------------------------ #

    def register_customer(
        self, name: str, phone: str, email: str
    ) -> Customer:
        """
        Register a new customer with the restaurant.

        Parameters
        ----------
        name  : str – Customer's full name.
        phone : str – Contact phone number.
        email : str – Email address.

        Returns
        -------
        Customer – The newly registered Customer, or None on failure.
        """
        try:
            cust_id = self.__next_customer_id()
            new_customer = Customer(cust_id, name, phone, email)
            self.__customers.append(new_customer)
            save_customers_to_csv(self.__customers, self.__customers_csv)
            print(f"  ✓ Customer '{name}' registered with ID '{cust_id}'.")
            return new_customer
        except ValueError as exc:
            print(f"  ✗ Could not register customer: {exc}")
            return None

    # ------------------------------------------------------------------ #
    #  Method 7 – view_customers                                          #
    # ------------------------------------------------------------------ #

    def view_customers(self) -> None:
        """Display all registered customers in a formatted table."""
        separator = "-" * 70
        print(f"\n  {self.__name} — Registered Customers")
        print(f"  {separator}")

        if not self.__customers:
            print("  (No customers registered yet)")
        else:
            for customer in self.__customers:
                customer.display_customer()

        print(f"  {separator}")
        print(f"  Total customers: {len(self.__customers)}\n")

    # ------------------------------------------------------------------ #
    #  Method 8 – search_customer                                         #
    # ------------------------------------------------------------------ #

    def search_customer(self, keyword: str) -> list:
        """
        Search for customers by name or ID.

        Parameters
        ----------
        keyword : str – Case-insensitive search term.

        Returns
        -------
        list[Customer] – Matching customers.
        """
        keyword_lower = keyword.lower()
        results = [
            cust
            for cust in self.__customers
            if keyword_lower in cust.name.lower()
            or keyword_lower in cust.customer_id.lower()
        ]

        print(f"\n  Customer search results for '{keyword}':")
        if results:
            for cust in results:
                cust.display_customer()
        else:
            print("  (No matching customers found)")

        return results

    # ------------------------------------------------------------------ #
    #  Internal helper – find customer by ID                              #
    # ------------------------------------------------------------------ #

    def __find_customer(self, customer_id: str):
        """Return the Customer with the given ID, or None."""
        for cust in self.__customers:
            if cust.customer_id == customer_id:
                return cust
        return None

    # ================================================================== #
    #  ORDER MANAGEMENT                                                    #
    # ================================================================== #

    # ------------------------------------------------------------------ #
    #  Method 9 – create_order                                            #
    # ------------------------------------------------------------------ #

    def create_order(self, customer_id: str) -> Order:
        """
        Create a new empty Order for an existing customer.

        Parameters
        ----------
        customer_id : str – ID of the customer placing the order.

        Returns
        -------
        Order – The new Order object, or None if customer not found.
        """
        customer = self.__find_customer(customer_id)
        if customer is None:
            print(f"  ✗ Customer '{customer_id}' not found. Please register first.")
            return None

        order_id = self.__next_order_id()
        new_order = Order(order_id, customer_id)
        self.__orders.append(new_order)
        print(f"  ✓ Order '{order_id}' created for customer '{customer.name}'.")
        return new_order

    # ------------------------------------------------------------------ #
    #  Method 10 – add_item_to_order                                      #
    # ------------------------------------------------------------------ #

    def add_item_to_order(self, order_id: str, item_id: str) -> bool:
        """
        Add a menu item to an existing open order.

        Parameters
        ----------
        order_id : str – ID of the target order.
        item_id  : str – ID of the menu item to add.

        Returns
        -------
        bool – True if item was successfully added.
        """
        order = self.__find_order(order_id)
        if order is None:
            print(f"  ✗ Order '{order_id}' not found.")
            return False

        item = self.__find_menu_item(item_id)
        if item is None:
            print(f"  ✗ Menu item '{item_id}' not found.")
            return False

        result = order.add_item(item)
        if result:
            save_orders_to_csv(self.__orders, self.__orders_csv)
        return result

    # ------------------------------------------------------------------ #
    #  Method 11 – remove_item_from_order                                 #
    # ------------------------------------------------------------------ #

    def remove_item_from_order(self, order_id: str, item_id: str) -> bool:
        """
        Remove a menu item from an existing open order.

        Parameters
        ----------
        order_id : str – ID of the target order.
        item_id  : str – ID of the menu item to remove.

        Returns
        -------
        bool – True if item was successfully removed.
        """
        order = self.__find_order(order_id)
        if order is None:
            print(f"  ✗ Order '{order_id}' not found.")
            return False

        result = order.remove_item(item_id)
        if result:
            save_orders_to_csv(self.__orders, self.__orders_csv)
        return result

    # ------------------------------------------------------------------ #
    #  Method 12 – view_orders                                            #
    # ------------------------------------------------------------------ #

    def view_orders(self, status_filter: str = None) -> None:
        """
        Display all orders, optionally filtered by status.

        Parameters
        ----------
        status_filter : str – Optional: 'open', 'billed', or 'cancelled'.
        """
        separator = "-" * 65
        print(f"\n  {self.__name} — Order History")
        print(f"  {separator}")

        orders_to_show = [
            order
            for order in self.__orders
            if (not status_filter or
                order.status.lower() == status_filter.lower())
        ]

        if not orders_to_show:
            print("  (No orders found)")
        else:
            for order in orders_to_show:
                cust = self.__find_customer(order.customer_id)
                cust_name = cust.name if cust else order.customer_id
                total_str = f"${order.calculate_total():.2f}"
                print(
                    f"  [{order.order_id}] Customer: {cust_name:<20} "
                    f"| Items: {len(order.items):<3} "
                    f"| Total: {total_str:<10} "
                    f"| Status: {order.status.upper()}"
                )

        print(f"  {separator}")
        print(f"  Orders displayed: {len(orders_to_show)}\n")

    # ------------------------------------------------------------------ #
    #  Method 13 – generate_bill                                          #
    # ------------------------------------------------------------------ #

    def generate_bill(self, order_id: str) -> float:
        """
        Generate and print the bill for a given order.

        Parameters
        ----------
        order_id : str – The order to bill.

        Returns
        -------
        float – Total amount billed, or 0.0 if order not found.
        """
        order = self.__find_order(order_id)
        if order is None:
            print(f"  ✗ Order '{order_id}' not found.")
            return 0.0

        cust = self.__find_customer(order.customer_id)
        cust_name = cust.name if cust else order.customer_id

        order.generate_bill(cust_name)
        save_orders_to_csv(self.__orders, self.__orders_csv)
        return order.calculate_total()

    # ------------------------------------------------------------------ #
    #  Method 14 – view_reports (Sales Report)                            #
    # ------------------------------------------------------------------ #

    def view_reports(self) -> dict:
        """
        Generate and display a comprehensive sales report.

        Calculates total orders, total revenue, average order value,
        and identifies the most popular menu item across all billed orders.

        Returns
        -------
        dict – Report statistics.
        """
        separator = "=" * 50

        # Only count billed orders in revenue stats
        billed_orders = [o for o in self.__orders if o.status == "billed"]
        total_orders = len(self.__orders)
        total_billed = len(billed_orders)
        total_revenue = sum(o.calculate_total() for o in billed_orders)
        avg_value = total_revenue / total_billed if total_billed > 0 else 0.0

        # Count item popularity across billed orders
        item_counts: dict = {}
        for order in billed_orders:
            for item in order.items:
                item_name = item["name"]
                item_counts[item_name] = item_counts.get(item_name, 0) + 1

        most_popular = (
            max(item_counts, key=item_counts.get)
            if item_counts
            else "N/A"
        )
        most_popular_count = item_counts.get(most_popular, 0)

        print(f"\n{separator}")
        print("           📊  SALES REPORT  📊")
        print(separator)
        print(f"  Restaurant     : {self.__name}")
        print(f"  Total Orders   : {total_orders}")
        print(f"  Billed Orders  : {total_billed}")
        print(f"  Open Orders    : {len([o for o in self.__orders if o.status == 'open'])}")
        print(f"  Cancelled      : {len([o for o in self.__orders if o.status == 'cancelled'])}")
        print(separator)
        print(f"  Total Revenue  : ${total_revenue:.2f}")
        print(f"  Avg Order Value: ${avg_value:.2f}")
        print(f"  Most Popular   : {most_popular} ({most_popular_count} orders)")
        print(separator)

        # Category breakdown
        if item_counts:
            print("  Top Selling Items:")
            sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
            for rank, (item_name, count) in enumerate(sorted_items[:5], 1):
                print(f"    {rank}. {item_name:<25} — {count} order(s)")
            print(separator)

        stats = {
            "total_orders": total_orders,
            "billed_orders": total_billed,
            "total_revenue": round(total_revenue, 2),
            "average_order_value": round(avg_value, 2),
            "most_popular_item": most_popular,
        }
        return stats

    # ------------------------------------------------------------------ #
    #  Internal helper – find order by ID                                 #
    # ------------------------------------------------------------------ #

    def __find_order(self, order_id: str):
        """Return the Order with the given ID, or None."""
        for order in self.__orders:
            if order.order_id == order_id:
                return order
        return None

    # ------------------------------------------------------------------ #
    #  Dunder helpers                                                      #
    # ------------------------------------------------------------------ #

    def __str__(self) -> str:
        return (
            f"Restaurant(name={self.__name}, "
            f"menu_items={len(self.__menu)}, "
            f"customers={len(self.__customers)}, "
            f"orders={len(self.__orders)})"
        )

    def __repr__(self) -> str:
        return self.__str__()
