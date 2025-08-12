import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# File paths
PRODUCT_FILE = 'data.json'
PURCHASE_FILE = 'purchase.json'
SALES_FILE = 'sales.json'

# Load data
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def save_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# ---------------- GUI START ----------------
class SilverShopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Silver Shop Inventory")
        self.products = load_data(PRODUCT_FILE)
        self.purchases = load_data(PURCHASE_FILE)
        self.sales = load_data(SALES_FILE)

        self.setup_ui()

    def setup_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True)

        # Tabs
        self.product_tab = ttk.Frame(notebook)
        self.purchase_tab = ttk.Frame(notebook)
        self.sales_tab = ttk.Frame(notebook)

        notebook.add(self.product_tab, text="Products")
        notebook.add(self.purchase_tab, text="Purchases")
        notebook.add(self.sales_tab, text="Sales")

        self.setup_products_tab()
        self.setup_purchase_tab()
        self.setup_sales_tab()

    # ---------- PRODUCTS TAB ----------
    def setup_products_tab(self):
        # Entry Form
        form = tk.Frame(self.product_tab)
        form.pack(pady=10)

        self.product_name = tk.Entry(form)
        self.product_quantity = tk.Entry(form)
        self.product_weight = tk.Entry(form)

        for label, widget in zip(["Product", "Quantity", "Weight (g)"],
                                 [self.product_name, self.product_quantity, self.product_weight]):
            tk.Label(form, text=label).pack()
            widget.pack()

        btns = tk.Frame(self.product_tab)
        btns.pack(pady=5)
        tk.Button(btns, text="Add Product", command=self.add_product).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Edit Selected", command=self.edit_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=5)

        # Table
        self.tree = ttk.Treeview(self.product_tab, columns=('Product', 'Quantity', 'Weight'), show='headings')
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True, pady=10)
        self.refresh_tree()

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for item in self.products:
            self.tree.insert('', 'end', values=(item['product'], item['quantity'], item['weight']))

    def add_product(self):
        name = self.product_name.get().strip()
        qty = self.product_quantity.get().strip()
        weight = self.product_weight.get().strip()

        if not name or not qty or not weight:
            messagebox.showwarning("Missing", "All fields are required.")
            return

        try:
            product = {
                "product": name,
                "quantity": int(qty),
                "weight": float(weight)
            }
        except:
            messagebox.showerror("Invalid", "Quantity must be number & weight decimal.")
            return

        self.products.append(product)
        save_data(self.products, PRODUCT_FILE)
        self.refresh_tree()
        self.clear_entries()

    def edit_selected(self):
        selected = self.tree.focus()
        if not selected:
            return

        index = self.tree.index(selected)
        self.products[index] = {
            "product": self.product_name.get(),
            "quantity": int(self.product_quantity.get()),
            "weight": float(self.product_weight.get())
        }
        save_data(self.products, PRODUCT_FILE)
        self.refresh_tree()
        self.clear_entries()

    def delete_selected(self):
        selected = self.tree.focus()
        if not selected:
            return
        index = self.tree.index(selected)
        del self.products[index]
        save_data(self.products, PRODUCT_FILE)
        self.refresh_tree()

    def clear_entries(self):
        self.product_name.delete(0, tk.END)
        self.product_quantity.delete(0, tk.END)
        self.product_weight.delete(0, tk.END)

    # ---------- PURCHASE TAB ----------
    def setup_purchase_tab(self):
        frame = tk.Frame(self.purchase_tab)
        frame.pack(pady=10)

        self.purchase_name = tk.Entry(frame)
        self.purchase_weight = tk.Entry(frame)
        self.purchase_quantity = tk.Entry(frame)

        tk.Label(frame, text="Vendor Name").pack()
        self.purchase_name.pack()
        tk.Label(frame, text="Product").pack()
        self.purchase_product = ttk.Combobox(frame, values=self.get_product_names())
        self.purchase_product.pack()
        tk.Label(frame, text="Weight (g)").pack()
        self.purchase_weight.pack()
        tk.Label(frame, text="Quantity").pack()
        self.purchase_quantity.pack()

        tk.Button(frame, text="Record Purchase", command=self.record_purchase).pack(pady=10)

    def record_purchase(self):
        vendor = self.purchase_name.get()
        product = self.purchase_product.get()
        qty = self.purchase_quantity.get()
        weight = self.purchase_weight.get()

        if not product or not qty or not weight:
            messagebox.showwarning("Missing", "All fields required.")
            return

        try:
            qty = int(qty)
            weight = float(weight)
        except:
            messagebox.showerror("Invalid", "Weight/Quantity invalid")
            return

        for p in self.products:
            if p['product'] == product:
                p['quantity'] += qty
                p['weight'] += weight
                break

        save_data(self.products, PRODUCT_FILE)
        self.purchases.append({
            "vendor": vendor,
            "product": product,
            "quantity": qty,
            "weight": weight
        })
        save_data(self.purchases, PURCHASE_FILE)
        self.refresh_tree()
        messagebox.showinfo("Success", "Purchase recorded.")

    # ---------- SALES TAB ----------
    def setup_sales_tab(self):
        frame = tk.Frame(self.sales_tab)
        frame.pack(pady=10)

        self.sales_name = tk.Entry(frame)
        self.sales_weight = tk.Entry(frame)
        self.sales_quantity = tk.Entry(frame)

        tk.Label(frame, text="Customer Name").pack()
        self.sales_name.pack()
        tk.Label(frame, text="Product").pack()
        self.sales_product = ttk.Combobox(frame, values=self.get_product_names())
        self.sales_product.pack()
        tk.Label(frame, text="Weight (g)").pack()
        self.sales_weight.pack()
        tk.Label(frame, text="Quantity").pack()
        self.sales_quantity.pack()

        tk.Button(frame, text="Record Sale", command=self.record_sale).pack(pady=10)

    def record_sale(self):
        customer = self.sales_name.get()
        product = self.sales_product.get()
        qty = self.sales_quantity.get()
        weight = self.sales_weight.get()

        if not product or not qty or not weight:
            messagebox.showwarning("Missing", "All fields required.")
            return

        try:
            qty = int(qty)
            weight = float(weight)
        except:
            messagebox.showerror("Invalid", "Weight/Quantity invalid")
            return

        for p in self.products:
            if p['product'] == product:
                p['quantity'] -= qty
                p['weight'] -= weight
                break

        save_data(self.products, PRODUCT_FILE)
        self.sales.append({
            "customer": customer,
            "product": product,
            "quantity": qty,
            "weight": weight
        })
        save_data(self.sales, SALES_FILE)
        self.refresh_tree()
        messagebox.showinfo("Success", "Sale recorded.")

    def get_product_names(self):
        return [p['product'] for p in self.products]

# Run app
if __name__ == '__main__':
    root = tk.Tk()
    app = SilverShopApp(root)
    root.mainloop()
