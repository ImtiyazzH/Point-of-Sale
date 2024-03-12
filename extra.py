import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import mysql.connector
import random

# Replace with your database credentials
db_config = {
    'host': 'localhost',
    'user': 'python_app',
    'password': 'python_app',
    'database': 'python_app'
}

# Connect to MySQL
connection = mysql.connector.connect(**db_config)

# Create a cursor object
cursor = connection.cursor()

# Perform database operations

# Close the cursor and connection when done
cursor.close()
connection.close()

class PointOfSaleApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Point of Sale")
        self.master.geometry("600x400")

        # Menu data (you can load this from a file or database in a real application)
        self.menu_items = {
            "Burger": 5.99,
            "Pizza": 8.49,
            "Pasta": 6.99,
            "Salad": 4.99
        }

        self.order = {}  # To store the current order

        # Create GUI elements
        self.menu_label = tk.Label(master, text="Menu:")
        self.menu_label.pack()

        self.menu_listbox = tk.Listbox(master, selectmode=tk.MULTIPLE)
        for item in self.menu_items:
            self.menu_listbox.insert(tk.END, f"{item} - ${self.menu_items[item]:.2f}")
        self.menu_listbox.pack()

        self.add_to_order_button = tk.Button(master, text="Add to Order", command=self.add_to_order)
        self.add_to_order_button.pack()

        self.order_label = tk.Label(master, text="Order:")
        self.order_label.pack()

        self.order_listbox = tk.Listbox(master)
        self.order_listbox.pack()

        self.total_label = tk.Label(master, text="Total: $0.00")
        self.total_label.pack()

        self.checkout_button = tk.Button(master, text="Checkout", command=self.checkout)
        self.checkout_button.pack()

        # Add "Pay Now" button for automatic payment
        self.pay_now_button = tk.Button(master, text="Pay Now", command=self.pay_now)
        self.pay_now_button.pack()

        # Payment method dropdown
        self.payment_method_label = tk.Label(master, text="Payment Method:")
        self.payment_method_label.pack()

        self.payment_methods = ["Credit Card", "Debit Card", "Cash"]
        self.selected_payment_method = tk.StringVar()
        self.payment_method_dropdown = ttk.Combobox(master, textvariable=self.selected_payment_method, values=self.payment_methods)
        self.payment_method_dropdown.pack()

    def add_to_order(self):
        selected_items = self.menu_listbox.curselection()
        for index in selected_items:
            menu_item = self.menu_listbox.get(index)
            item_name = menu_item.split(" - ")[0]
            item_price = self.menu_items[item_name]
            self.order[item_name] = item_price
            self.order_listbox.insert(tk.END, f"{item_name} - ${item_price:.2f}")
        self.update_total()

    def update_total(self):
        total = sum(self.order.values())
        self.total_label.config(text=f"Total: ${total:.2f}")

    def checkout(self):
        total = sum(self.order.values())
        if total > 0:
            checkout_message = f"Thank you for your order! Total: ${total:.2f}"

            # Provide a recommendation
            recommended_item = self.get_recommendation()

            if recommended_item:
                recommendation_response = tk.messagebox.askquestion("Recommendation", f"We recommend trying {recommended_item}. Would you like to add it to your order?")
                if recommendation_response == 'yes':
                    self.order[recommended_item] = self.menu_items[recommended_item]
                    self.order_listbox.insert(tk.END, f"{recommended_item} - ${self.menu_items[recommended_item]:.2f}")
                    self.update_total()  # Update the total after adding the recommended item
                    checkout_message += f"\nRecommended item '{recommended_item}' added to your order. Updated Total: ${sum(self.order.values()):.2f}"

            tk.messagebox.showinfo("Checkout", checkout_message)

            # Automatically trigger payment upon checkout
            self.pay_now()
        else:
            tk.messagebox.showinfo("Checkout", "Your order is empty. Please add items to your order first.")

    def pay_now(self):
        # Simulate payment process (replace this with actual payment integration)
        selected_payment_method = self.selected_payment_method.get()
        if selected_payment_method:
            payment_successful = tk.messagebox.askyesno("Payment", f"Pay ${sum(self.order.values()):.2f} using {selected_payment_method}. Do you want to proceed?")
            if payment_successful:
                tk.messagebox.showinfo("Payment Success", "Payment successful!")
                self.mark_order_as_paid()
            else:
                tk.messagebox.showwarning("Payment Failed", "Payment failed. Please try again.")
        else:
            tk.messagebox.showwarning("Payment Failed", "Payment method not selected. Please try again.")

    def mark_order_as_paid(self):
        # Update the database to mark the order as paid
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Assume you have a column named 'is_paid' in your 'orders' table
        cursor.execute("UPDATE orders SET is_paid = %s WHERE order_number = %s", (True, self.get_last_order_number()))

        connection.commit()
        cursor.close()
        connection.close()

    def get_recommendation(self):
        # In a real-world scenario, you might use more sophisticated recommendation logic.
        # For simplicity, we'll randomly select an item from the menu as a recommendation.
        menu_items = list(self.menu_items.keys())
        random.shuffle(menu_items)
        for item in menu_items:
            if item not in self.order:
                return item
        return None

    def get_last_order_number(self):
        # Retrieve the last order number from the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        cursor.execute("SELECT MAX(order_number) FROM orders")
        last_order_number = cursor.fetchone()[0] or 0  # If no orders exist, start from 0

        cursor.close()
        connection.close()

        return last_order_number

if __name__ == "__main__":
    root = tk.Tk()
    app = PointOfSaleApp(root)
    root.mainloop()
