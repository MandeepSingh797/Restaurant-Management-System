"""
customer.py
-----------
Defines the Customer class for the Restaurant Management System.

Each Customer represents a registered patron of the restaurant,
storing personal contact details and their order history reference.


"""

import csv
import os
import re


class Customer:
    """
    Represents a registered customer of the restaurant.

    Attributes
    ----------
    customer_id : str – Unique identifier for the customer.
    name        : str – Full name of the customer.
    phone       : str – Contact phone number.
    email       : str – Email address.
    """

    # ------------------------------------------------------------------ #
    #  Constructor                                                         #
    # ------------------------------------------------------------------ #

    def __init__(self, customer_id: str, name: str, phone: str, email: str):
        """
        Initialise a new Customer instance.

        Parameters
        ----------
        customer_id : str – Unique customer identifier (e.g. 'C001').
        name        : str – Customer's full name.
        phone       : str – Customer's phone number.
        email       : str – Customer's email address.

        Raises
        ------
        ValueError – If any required field is empty.
        """
        if not customer_id or not customer_id.strip():
            raise ValueError("Customer ID cannot be empty.")
        if not name or not name.strip():
            raise ValueError("Customer name cannot be empty.")

        self.__customer_id = customer_id.strip()
        self.__name = name.strip()
        self.__phone = phone.strip()
        self.__email = email.strip()

    # ------------------------------------------------------------------ #
    #  Properties (Getters)                                                #
    # ------------------------------------------------------------------ #

    @property
    def customer_id(self) -> str:
        """Return the unique customer ID."""
        return self.__customer_id

    @property
    def name(self) -> str:
        """Return the customer's full name."""
        return self.__name

    @property
    def phone(self) -> str:
        """Return the customer's phone number."""
        return self.__phone

    @property
    def email(self) -> str:
        """Return the customer's email address."""
        return self.__email

    # ------------------------------------------------------------------ #
    #  Method 1 – display_customer                                        #
    # ------------------------------------------------------------------ #

    def display_customer(self) -> None:
        """
        Print a formatted customer record to the console.

        Example output
        --------------
        [C001] John Smith        | Phone: 555-1234       | Email: john@example.com
        """
        print(
            f"[{self.__customer_id}] {self.__name:<20} "
            f"| Phone: {self.__phone:<15} "
            f"| Email: {self.__email}"
        )

    # ------------------------------------------------------------------ #
    #  Method 2 – update_phone                                            #
    # ------------------------------------------------------------------ #

    def update_phone(self, new_phone: str) -> bool:
        """
        Update the customer's phone number after basic validation.

        Parameters
        ----------
        new_phone : str – New phone number string.

        Returns
        -------
        bool – True if update succeeded, False otherwise.
        """
        if not new_phone or not new_phone.strip():
            print("  ✗ Error: Phone number cannot be empty.")
            return False
        self.__phone = new_phone.strip()
        print(f"  ✓ Phone updated to '{self.__phone}'")
        return True

    # ------------------------------------------------------------------ #
    #  Method 3 – update_email                                            #
    # ------------------------------------------------------------------ #

    def update_email(self, new_email: str) -> bool:
        """
        Update the customer's email address with format validation.

        Parameters
        ----------
        new_email : str – New email address string.

        Returns
        -------
        bool – True if update succeeded, False otherwise.
        """
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not re.match(pattern, new_email.strip()):
            print("  ✗ Error: Invalid email format (e.g. user@example.com).")
            return False
        self.__email = new_email.strip()
        print(f"  ✓ Email updated to '{self.__email}'")
        return True

    # ------------------------------------------------------------------ #
    #  Method 4 – update_name                                             #
    # ------------------------------------------------------------------ #

    def update_name(self, new_name: str) -> bool:
        """
        Update the customer's full name.

        Parameters
        ----------
        new_name : str – New name string.

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
    #  Method 5 – to_csv                                                  #
    # ------------------------------------------------------------------ #

    def to_csv(self) -> list:
        """
        Serialise this customer to a list suitable for CSV writing.

        Returns
        -------
        list – [customer_id, name, phone, email]
        """
        return [self.__customer_id, self.__name, self.__phone, self.__email]

    # ------------------------------------------------------------------ #
    #  Method 6 – get_summary                                             #
    # ------------------------------------------------------------------ #

    def get_summary(self) -> dict:
        """
        Return a dictionary representation of this customer.

        Returns
        -------
        dict – Keys: customer_id, name, phone, email.
        """
        return {
            "customer_id": self.__customer_id,
            "name": self.__name,
            "phone": self.__phone,
            "email": self.__email,
        }

    # ------------------------------------------------------------------ #
    #  Dunder helpers                                                      #
    # ------------------------------------------------------------------ #

    def __str__(self) -> str:
        return (
            f"Customer(id={self.__customer_id}, name={self.__name}, "
            f"phone={self.__phone}, email={self.__email})"
        )

    def __repr__(self) -> str:
        return self.__str__()


# ------------------------------------------------------------------ #
#  Module-level CSV helpers                                           #
# ------------------------------------------------------------------ #

CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "customers.csv")
CSV_HEADERS = ["customer_id", "name", "phone", "email"]


def load_customers_from_csv(filepath: str = CSV_PATH) -> list:
    """
    Load all customers from the CSV file.

    Parameters
    ----------
    filepath : str – Path to the customers CSV file.

    Returns
    -------
    list[Customer] – A list of Customer objects.
    """
    customers = []
    try:
        with open(filepath, newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                try:
                    customer = Customer(
                        row["customer_id"],
                        row["name"],
                        row["phone"],
                        row["email"],
                    )
                    customers.append(customer)
                except (ValueError, KeyError) as exc:
                    print(f"  ⚠ Skipping invalid customer row: {row} — {exc}")
    except FileNotFoundError:
        print(f"  ⚠ Customers file not found at '{filepath}'. Starting fresh.")
    except Exception as exc:
        print(f"  ✗ Unexpected error loading customers: {exc}")
    finally:
        pass  # Context manager handles file closure
    return customers


def save_customers_to_csv(customers: list, filepath: str = CSV_PATH) -> None:
    """
    Persist all Customer objects to the CSV file.

    Parameters
    ----------
    customers : list[Customer] – Customers to write.
    filepath  : str            – Destination file path.
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(CSV_HEADERS)
            for customer in customers:
                writer.writerow(customer.to_csv())
    except PermissionError:
        print(f"  ✗ Permission denied writing to '{filepath}'.")
    except Exception as exc:
        print(f"  ✗ Error saving customers: {exc}")
    finally:
        pass  # Ensure clean exit
