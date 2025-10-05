# orders.py
from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class OrderManagement:
    def __init__(self, master):
        self.master = master
        self.master.title("Order Management System")
        self.master.geometry("1100x700+150+50")
        
        self.conn = sqlite3.connect("D:\Grocry_store\Database\store.db")
        self.c = self.conn.cursor()
        
        # Create orders table if not exists
        self.create_orders_table()
        
        self.current_order_items = []
        self.selected_product_index = -1
        self.create_interface()
        
        # Bind keyboard events
        self.bind_keyboard_events()
    
    def create_orders_table(self):
        try:
            self.c.execute('''CREATE TABLE IF NOT EXISTS orders
                             (order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                              customer_name TEXT NOT NULL,
                              customer_phone TEXT,
                              order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                              total_amount REAL NOT NULL,
                              status TEXT DEFAULT 'Pending',
                              payment_method TEXT)''')
            
            self.c.execute('''CREATE TABLE IF NOT EXISTS order_items
                             (item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                              order_id INTEGER,
                              product_id INTEGER,
                              product_name TEXT NOT NULL,
                              quantity INTEGER NOT NULL,
                              unit_price REAL NOT NULL,
                              total_price REAL NOT NULL,
                              FOREIGN KEY (order_id) REFERENCES orders (order_id))''')
            
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to create orders table: {e}")
    
    def create_interface(self):
        # Main Frame
        main_frame = Frame(self.master, padx=10, pady=10)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Heading
        heading = Label(main_frame, text="Order Management System", 
                       font=('arial 18 bold'), fg='steelblue')
        heading.pack(pady=5)
        
        # Create Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=BOTH, expand=True, pady=10)
        
        # Create Order Tab
        self.create_order_tab(notebook)
        
        # View Orders Tab
        self.create_orders_tab(notebook)
        
        # Set default tab
        notebook.select(0)
    
    def create_order_tab(self, notebook):
        # Create Order Frame
        order_frame = Frame(notebook)
        notebook.add(order_frame, text="Create New Order")
        
        # Left Side - Customer Info and Products
        left_frame = Frame(order_frame)
        left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        
        # Customer Information (Simplified)
        customer_frame = LabelFrame(left_frame, text="Customer Information", font=('arial 10 bold'))
        customer_frame.pack(fill=X, pady=5)
        
        Label(customer_frame, text="Customer Name:*", font=('arial 9 bold')).grid(row=0, column=0, sticky='w', pady=3, padx=5)
        self.customer_name = Entry(customer_frame, width=25, font=('arial 9'))
        self.customer_name.grid(row=0, column=1, pady=3, padx=5)
        
        Label(customer_frame, text="Phone:", font=('arial 9 bold')).grid(row=1, column=0, sticky='w', pady=3, padx=5)
        self.customer_phone = Entry(customer_frame, width=25, font=('arial 9'))
        self.customer_phone.grid(row=1, column=1, pady=3, padx=5)
        
        Label(customer_frame, text="Payment:", font=('arial 9 bold')).grid(row=2, column=0, sticky='w', pady=3, padx=5)
        self.payment_method = ttk.Combobox(customer_frame, width=22, font=('arial 9'),
                                          values=['Cash', 'Credit Card', 'Debit Card', 'Digital Payment'])
        self.payment_method.set('Cash')
        self.payment_method.grid(row=2, column=1, pady=3, padx=5)
        
        # Products Search
        search_frame = Frame(left_frame)
        search_frame.pack(fill=X, pady=5)
        
        Label(search_frame, text="Search Product:", font=('arial 9 bold')).pack(side=LEFT, padx=5)
        self.search_var = StringVar()
        self.search_entry = Entry(search_frame, textvariable=self.search_var, width=25, font=('arial 9'))
        self.search_entry.pack(side=LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_products)
        
        # Products Selection
        products_frame = LabelFrame(left_frame, text="Available Products", font=('arial 10 bold'))
        products_frame.pack(fill=BOTH, expand=True, pady=5)
        
        # Products Treeview
        columns = ('ID', 'Name', 'Stock', 'Price')
        self.products_tree = ttk.Treeview(products_frame, columns=columns, show='headings', height=12)
        
        column_widths = {'ID': 50, 'Name': 150, 'Stock': 60, 'Price': 80}
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar for products
        products_scrollbar = ttk.Scrollbar(products_frame, orient=VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscroll=products_scrollbar.set)
        products_scrollbar.pack(side=RIGHT, fill=Y)
        self.products_tree.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Load products
        self.load_available_products()
        
        # Right Side - Current Order
        right_frame = Frame(order_frame)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=5, pady=5)
        
        # Current Order Frame
        current_order_frame = LabelFrame(right_frame, text="Current Order", font=('arial 10 bold'))
        current_order_frame.pack(fill=BOTH, expand=True, pady=5)
        
        # Order Items Treeview
        order_columns = ('Product', 'Qty', 'Price', 'Total')
        self.order_tree = ttk.Treeview(current_order_frame, columns=order_columns, show='headings', height=12)
        
        order_widths = {'Product': 150, 'Qty': 50, 'Price': 80, 'Total': 80}
        for col in order_columns:
            self.order_tree.heading(col, text=col)
            self.order_tree.column(col, width=order_widths.get(col, 100))
        
        # Scrollbar for order items
        order_scrollbar = ttk.Scrollbar(current_order_frame, orient=VERTICAL, command=self.order_tree.yview)
        self.order_tree.configure(yscroll=order_scrollbar.set)
        order_scrollbar.pack(side=RIGHT, fill=Y)
        self.order_tree.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Order Summary
        summary_frame = LabelFrame(right_frame, text="Order Summary", font=('arial 10 bold'))
        summary_frame.pack(fill=X, pady=5)
        
        self.summary_labels = {}
        summary_items = [
            ("Subtotal:", "subtotal"),
            ("Tax (10%):", "tax"),
            ("Discount:", "discount"),
            ("Total Amount:", "total")
        ]
        
        for i, (text, key) in enumerate(summary_items):
            Label(summary_frame, text=text, font=('arial 9 bold')).grid(row=i, column=0, sticky='w', pady=1, padx=5)
            value_label = Label(summary_frame, text="$0.00", font=('arial 9'))
            value_label.grid(row=i, column=1, sticky='w', pady=1, padx=5)
            self.summary_labels[key] = value_label
        
        # Discount Frame
        discount_frame = Frame(summary_frame)
        discount_frame.grid(row=2, column=1, sticky='w', pady=1, padx=5)
        
        self.discount_var = StringVar(value="0")
        discount_entry = Entry(discount_frame, textvariable=self.discount_var, width=6, font=('arial 9'))
        discount_entry.pack(side=LEFT)
        discount_entry.bind('<KeyRelease>', self.update_order_summary)
        Label(discount_frame, text="%", font=('arial 9')).pack(side=LEFT, padx=2)
        
        # Keyboard Shortcuts Info
        shortcut_frame = LabelFrame(right_frame, text="Keyboard Shortcuts", font=('arial 9 bold'))
        shortcut_frame.pack(fill=X, pady=5)
        
        shortcuts = [
            "↑/↓: Navigate products",
            "Enter/Space: Add to order", 
            "+/-: Change quantity",
            "Delete: Remove item",
            "F1: Place Order",
            "F2: Clear Order"
        ]
        
        for i, shortcut in enumerate(shortcuts):
            Label(shortcut_frame, text=shortcut, font=('arial 8')).grid(row=i//2, column=i%2, sticky='w', padx=5, pady=1)
        
        # Order Buttons
        button_frame = Frame(right_frame)
        button_frame.pack(fill=X, pady=10)
        
        Button(button_frame, text="Place Order (F1)", bg='#27ae60', fg='white',
               font=('arial 9 bold'), command=self.place_order).pack(side=LEFT, padx=3)
        
        Button(button_frame, text="Clear Order (F2)", bg='#e74c3c', fg='white',
               font=('arial 9 bold'), command=self.clear_current_order).pack(side=LEFT, padx=3)
        
        Button(button_frame, text="Print Bill", bg='#3498db', fg='white',
               font=('arial 9 bold'), command=self.print_bill).pack(side=LEFT, padx=3)
        
        Button(button_frame, text="Close", bg='#95a5a6', fg='white',
               font=('arial 9 bold'), command=self.master.destroy).pack(side=LEFT, padx=3)
        
        # Set focus to customer name
        self.customer_name.focus_set()
    
    def create_orders_tab(self, notebook):
        # View Orders Frame
        orders_frame = Frame(notebook)
        notebook.add(orders_frame, text="View Orders")
        
        # Search and Filter Frame
        filter_frame = Frame(orders_frame)
        filter_frame.pack(fill=X, pady=5, padx=10)
        
        Label(filter_frame, text="Search:", font=('arial 9 bold')).pack(side=LEFT, padx=3)
        self.order_search_var = StringVar()
        search_entry = Entry(filter_frame, textvariable=self.order_search_var, width=20, font=('arial 9'))
        search_entry.pack(side=LEFT, padx=3)
        search_entry.bind('<KeyRelease>', self.search_orders)
        
        Label(filter_frame, text="Status:", font=('arial 9 bold')).pack(side=LEFT, padx=3)
        self.status_filter = ttk.Combobox(filter_frame, width=12, font=('arial 9'),
                                         values=['All', 'Pending', 'Completed', 'Cancelled'])
        self.status_filter.set('All')
        self.status_filter.pack(side=LEFT, padx=3)
        self.status_filter.bind('<<ComboboxSelected>>', self.filter_orders)
        
        Button(filter_frame, text="Refresh", bg='#3498db', fg='white',
               font=('arial 9 bold'), command=self.load_orders).pack(side=LEFT, padx=3)
        
        # Orders Treeview
        tree_frame = Frame(orders_frame)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        columns = ('Order ID', 'Customer', 'Date', 'Total', 'Status')
        self.orders_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        order_widths = {'Order ID': 80, 'Customer': 120, 'Date': 120, 'Total': 80, 'Status': 80}
        for col in columns:
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=order_widths.get(col, 100))
        
        # Scrollbar
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscroll=v_scrollbar.set)
        v_scrollbar.pack(side=RIGHT, fill=Y)
        self.orders_tree.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Order Actions Frame
        action_frame = Frame(orders_frame)
        action_frame.pack(fill=X, pady=5, padx=10)
        
        Button(action_frame, text="View Details", bg='#3498db', fg='white',
               font=('arial 9 bold'), command=self.view_order_details).pack(side=LEFT, padx=2)
        
        Button(action_frame, text="Update Status", bg='#2ecc71', fg='white',
               font=('arial 9 bold'), command=self.update_order_status).pack(side=LEFT, padx=2)
        
        Button(action_frame, text="Delete Order", bg='#e74c3c', fg='white',
               font=('arial 9 bold'), command=self.delete_order).pack(side=LEFT, padx=2)
        
        Button(action_frame, text="Print Bill", bg='#9b59b6', fg='white',
               font=('arial 9 bold'), command=self.print_bill_from_history).pack(side=LEFT, padx=2)
        
        # Load orders
        self.load_orders()
    
    def bind_keyboard_events(self):
        # Bind global keyboard events
        self.master.bind('<Up>', self.navigate_products_up)
        self.master.bind('<Down>', self.navigate_products_down)
        self.master.bind('<Return>', self.add_selected_product)
        self.master.bind('<space>', self.add_selected_product)
        self.master.bind('<plus>', self.increase_quantity)
        self.master.bind('<equal>', self.increase_quantity)  # For + key without shift
        self.master.bind('<minus>', self.decrease_quantity)
        self.master.bind('<Delete>', self.remove_selected_order_item)
        self.master.bind('<F1>', lambda e: self.place_order())
        self.master.bind('<F2>', lambda e: self.clear_current_order())
        
        # Bind tab navigation
        self.master.bind('<Control-Tab>', self.focus_next_widget)
        self.master.bind('<Control-ISO_Left_Tab>', self.focus_previous_widget)
    
    def navigate_products_up(self, event):
        if not self.products_tree.selection():
            # Select first item if none selected
            items = self.products_tree.get_children()
            if items:
                self.products_tree.selection_set(items[0])
                self.products_tree.focus(items[0])
        else:
            current = self.products_tree.selection()[0]
            prev = self.products_tree.prev(current)
            if prev:
                self.products_tree.selection_set(prev)
                self.products_tree.focus(prev)
    
    def navigate_products_down(self, event):
        if not self.products_tree.selection():
            # Select first item if none selected
            items = self.products_tree.get_children()
            if items:
                self.products_tree.selection_set(items[0])
                self.products_tree.focus(items[0])
        else:
            current = self.products_tree.selection()[0]
            next_item = self.products_tree.next(current)
            if next_item:
                self.products_tree.selection_set(next_item)
                self.products_tree.focus(next_item)
    
    def add_selected_product(self, event):
        selected_item = self.products_tree.selection()
        if selected_item:
            product_data = self.products_tree.item(selected_item[0], 'values')
            product_id, product_name, stock, price = product_data
            
            # Check if product already in order
            for i, item in enumerate(self.current_order_items):
                if item['product_id'] == product_id:
                    # Increase quantity by 1
                    self.current_order_items[i]['quantity'] += 1
                    self.current_order_items[i]['total_price'] = self.current_order_items[i]['unit_price'] * self.current_order_items[i]['quantity']
                    self.refresh_order_display()
                    self.update_order_summary()
                    return
            
            # Add new item with quantity 1
            self.current_order_items.append({
                'product_id': product_id,
                'product_name': product_name,
                'quantity': 1,
                'unit_price': float(price),
                'total_price': float(price)
            })
            
            self.refresh_order_display()
            self.update_order_summary()
    
    def increase_quantity(self, event):
        selected_order_item = self.order_tree.selection()
        if selected_order_item:
            index = self.order_tree.index(selected_order_item[0])
            if 0 <= index < len(self.current_order_items):
                self.current_order_items[index]['quantity'] += 1
                self.current_order_items[index]['total_price'] = self.current_order_items[index]['unit_price'] * self.current_order_items[index]['quantity']
                self.refresh_order_display()
                self.update_order_summary()
    
    def decrease_quantity(self, event):
        selected_order_item = self.order_tree.selection()
        if selected_order_item:
            index = self.order_tree.index(selected_order_item[0])
            if 0 <= index < len(self.current_order_items):
                if self.current_order_items[index]['quantity'] > 1:
                    self.current_order_items[index]['quantity'] -= 1
                    self.current_order_items[index]['total_price'] = self.current_order_items[index]['unit_price'] * self.current_order_items[index]['quantity']
                    self.refresh_order_display()
                    self.update_order_summary()
                else:
                    # Remove item if quantity becomes 0
                    self.current_order_items.pop(index)
                    self.refresh_order_display()
                    self.update_order_summary()
    
    def remove_selected_order_item(self, event):
        selected_item = self.order_tree.selection()
        if selected_item:
            index = self.order_tree.index(selected_item[0])
            if 0 <= index < len(self.current_order_items):
                self.current_order_items.pop(index)
                self.refresh_order_display()
                self.update_order_summary()
    
    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return "break"
    
    def focus_previous_widget(self, event):
        event.widget.tk_focusPrev().focus()
        return "break"
    
    def load_available_products(self):
        # Clear existing data
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        try:
            self.c.execute("SELECT id, name, stock, selling_price FROM products WHERE stock > 0 ORDER BY name")
            products = self.c.fetchall()
            
            for product in products:
                self.products_tree.insert('', 'end', values=product)
                
            # Select first item by default
            items = self.products_tree.get_children()
            if items:
                self.products_tree.selection_set(items[0])
                self.products_tree.focus(items[0])
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load products: {e}")
    
    def search_products(self, event=None):
        search_term = self.search_var.get().strip().lower()
        
        # Clear existing data
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        try:
            if search_term:
                self.c.execute("SELECT id, name, stock, selling_price FROM products WHERE stock > 0 AND (name LIKE ? OR id LIKE ?) ORDER BY name",
                             (f'%{search_term}%', f'%{search_term}%'))
            else:
                self.c.execute("SELECT id, name, stock, selling_price FROM products WHERE stock > 0 ORDER BY name")
            
            products = self.c.fetchall()
            
            for product in products:
                self.products_tree.insert('', 'end', values=product)
            
            # Select first item if available
            items = self.products_tree.get_children()
            if items:
                self.products_tree.selection_set(items[0])
                self.products_tree.focus(items[0])
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Search failed: {e}")
    
    def refresh_order_display(self):
        # Clear existing data
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
        
        for item in self.current_order_items:
            self.order_tree.insert('', 'end', values=(
                item['product_name'],
                item['quantity'],
                f"${item['unit_price']:.2f}",
                f"${item['total_price']:.2f}"
            ))
        
        # Select the last added item
        if self.current_order_items:
            last_item = self.order_tree.get_children()[-1]
            self.order_tree.selection_set(last_item)
            self.order_tree.focus(last_item)
    
    def update_order_summary(self, event=None):
        subtotal = sum(item['total_price'] for item in self.current_order_items)
        
        # Calculate tax (10%)
        tax = subtotal * 0.10
        
        # Calculate discount
        try:
            discount_percent = float(self.discount_var.get() or 0)
            discount = subtotal * (discount_percent / 100)
        except ValueError:
            discount = 0
        
        total = subtotal + tax - discount
        
        # Update labels
        self.summary_labels['subtotal'].config(text=f"${subtotal:.2f}")
        self.summary_labels['tax'].config(text=f"${tax:.2f}")
        self.summary_labels['discount'].config(text=f"${discount:.2f}")
        self.summary_labels['total'].config(text=f"${total:.2f}")
    
    def clear_current_order(self):
        self.current_order_items.clear()
        self.refresh_order_display()
        self.update_order_summary()
        self.customer_name.delete(0, END)
        self.customer_phone.delete(0, END)
        self.payment_method.set('Cash')
        self.discount_var.set("0")
        self.customer_name.focus_set()
    
    def place_order(self):
        if not self.current_order_items:
            messagebox.showinfo("Error", "Please add products to the order")
            return
        
        if not self.customer_name.get().strip():
            messagebox.showinfo("Error", "Please enter customer name")
            self.customer_name.focus_set()
            return
        
        try:
            # Calculate final total
            subtotal = sum(item['total_price'] for item in self.current_order_items)
            tax = subtotal * 0.10
            discount_percent = float(self.discount_var.get() or 0)
            discount = subtotal * (discount_percent / 100)
            total_amount = subtotal + tax - discount
            
            # Insert order
            self.c.execute('''INSERT INTO orders 
                           (customer_name, customer_phone, total_amount, payment_method)
                           VALUES (?, ?, ?, ?)''',
                           (self.customer_name.get().strip(),
                            self.customer_phone.get().strip(),
                            total_amount,
                            self.payment_method.get()))
            
            order_id = self.c.lastrowid
            
            # Insert order items
            for item in self.current_order_items:
                self.c.execute('''INSERT INTO order_items 
                               (order_id, product_id, product_name, quantity, unit_price, total_price)
                               VALUES (?, ?, ?, ?, ?, ?)''',
                               (order_id, item['product_id'], item['product_name'],
                                item['quantity'], item['unit_price'], item['total_price']))
                
                # Update product stock
                self.c.execute("UPDATE products SET stock = stock - ? WHERE id = ?",
                              (item['quantity'], item['product_id']))
            
            self.conn.commit()
            
            # Show success message and ask to print bill
            result = messagebox.askyesno("Success", 
                                       f"Order placed successfully!\nOrder ID: {order_id}\nTotal Amount: ${total_amount:.2f}\n\nDo you want to print the bill?")
            
            if result:
                self.print_bill(order_id)
            
            self.clear_current_order()
            self.load_available_products()  # Refresh available products
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to place order: {e}")
    
    def print_bill(self, order_id=None):
        if not order_id:
            # Print current order (before placing)
            if not self.current_order_items:
                messagebox.showinfo("Info", "No items in current order to print")
                return
            
            # Create a temporary order for printing
            customer_name = self.customer_name.get().strip() or "Walk-in Customer"
            subtotal = sum(item['total_price'] for item in self.current_order_items)
            tax = subtotal * 0.10
            discount_percent = float(self.discount_var.get() or 0)
            discount = subtotal * (discount_percent / 100)
            total_amount = subtotal + tax - discount
            
            self.show_bill_preview(customer_name, "TEMP", total_amount, self.current_order_items)
        else:
            # Print existing order
            try:
                self.c.execute('''SELECT customer_name, total_amount FROM orders WHERE order_id = ?''', (order_id,))
                order = self.c.fetchone()
                
                self.c.execute('''SELECT product_name, quantity, unit_price, total_price 
                                 FROM order_items WHERE order_id = ?''', (order_id,))
                items = self.c.fetchall()
                
                current_order_items = []
                for item in items:
                    current_order_items.append({
                        'product_name': item[0],
                        'quantity': item[1],
                        'unit_price': item[2],
                        'total_price': item[3]
                    })
                
                self.show_bill_preview(order[0], order_id, order[1], current_order_items)
                
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to load order for printing: {e}")
    
    def print_bill_from_history(self):
        selected_item = self.orders_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select an order first")
            return
        
        order_data = self.orders_tree.item(selected_item[0], 'values')
        order_id = order_data[0]
        self.print_bill(order_id)
    
    def show_bill_preview(self, customer_name, order_id, total_amount, items):
        # Create bill preview window
        bill_window = Toplevel(self.master)
        bill_window.title(f"Bill - Order #{order_id}")
        bill_window.geometry("400x600+400+100")
        
        # Bill content
        bill_content = f"""
{'='*40}
         GROCERY STORE
{'='*40}
Order ID: {order_id}
Customer: {customer_name}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*40}
ITEMS:
{'='*40}
"""
        
        for item in items:
            bill_content += f"{item['product_name'][:20]:<20}\n"
            bill_content += f"{' ':>20} {item['quantity']:>2} x ${item['unit_price']:>6.2f} = ${item['total_price']:>7.2f}\n"
        
        bill_content += f"{'='*40}\n"
        
        # Calculate totals
        subtotal = sum(item['total_price'] for item in items)
        tax = subtotal * 0.10
        total = subtotal + tax
        
        bill_content += f"Subtotal: ${subtotal:>26.2f}\n"
        bill_content += f"Tax (10%): ${tax:>25.2f}\n"
        bill_content += f"{'='*40}\n"
        bill_content += f"TOTAL: ${total:>29.2f}\n"
        bill_content += f"{'='*40}\n"
        bill_content += "     THANK YOU FOR YOUR BUSINESS!\n"
        bill_content += f"{'='*40}"
        
        # Bill text widget
        bill_text = Text(bill_window, font=('Courier', 10), width=45, height=35)
        bill_text.pack(padx=10, pady=10, fill=BOTH, expand=True)
        bill_text.insert(END, bill_content)
        bill_text.config(state=DISABLED)
        
        # Buttons frame
        btn_frame = Frame(bill_window)
        btn_frame.pack(pady=10)
        
        Button(btn_frame, text="Print", bg='#3498db', fg='white',
               font=('arial 9 bold'), command=lambda: self.actual_print(bill_content)).pack(side=LEFT, padx=5)
        
        Button(btn_frame, text="Save as Text", bg='#2ecc71', fg='white',
               font=('arial 9 bold'), command=lambda: self.save_bill(bill_content)).pack(side=LEFT, padx=5)
        
        Button(btn_frame, text="Close", bg='#e74c3c', fg='white',
               font=('arial 9 bold'), command=bill_window.destroy).pack(side=LEFT, padx=5)
    
    def actual_print(self, bill_content):
        # This is a simplified print function
        # In a real application, you would use a proper printing library
        messagebox.showinfo("Print", "Bill sent to printer!\n\nIn a real application, this would connect to an actual printer.")
    
    def save_bill(self, bill_content):
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Bill As"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(bill_content)
                messagebox.showinfo("Success", f"Bill saved as: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save bill: {e}")
    
    def load_orders(self):
        # Clear existing data
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        
        try:
            self.c.execute('''SELECT order_id, customer_name, 
                             strftime('%Y-%m-%d %H:%M', order_date), total_amount, status
                             FROM orders ORDER BY order_date DESC''')
            orders = self.c.fetchall()
            
            for order in orders:
                self.orders_tree.insert('', 'end', values=order)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load orders: {e}")
    
    def search_orders(self, event=None):
        search_term = self.order_search_var.get().strip()
        
        # Clear existing data
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        
        try:
            if search_term:
                self.c.execute('''SELECT order_id, customer_name, 
                                 strftime('%Y-%m-%d %H:%M', order_date), total_amount, status
                                 FROM orders 
                                 WHERE customer_name LIKE ? OR order_id LIKE ?
                                 ORDER BY order_date DESC''',
                             (f'%{search_term}%', f'%{search_term}%'))
            else:
                self.c.execute('''SELECT order_id, customer_name, 
                                 strftime('%Y-%m-%d %H:%M', order_date), total_amount, status
                                 FROM orders ORDER BY order_date DESC''')
            
            orders = self.c.fetchall()
            
            for order in orders:
                self.orders_tree.insert('', 'end', values=order)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Search failed: {e}")
    
    def filter_orders(self, event=None):
        status = self.status_filter.get()
        
        if status == 'All':
            self.load_orders()
            return
        
        # Clear existing data
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        
        try:
            self.c.execute('''SELECT order_id, customer_name, 
                             strftime('%Y-%m-%d %H:%M', order_date), total_amount, status
                             FROM orders WHERE status = ? ORDER BY order_date DESC''', (status,))
            orders = self.c.fetchall()
            
            for order in orders:
                self.orders_tree.insert('', 'end', values=order)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Filter failed: {e}")
    
    def view_order_details(self, event=None):
        selected_item = self.orders_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select an order first")
            return
        
        order_data = self.orders_tree.item(selected_item[0], 'values')
        order_id = order_data[0]
        
        try:
            # Get order details
            self.c.execute('''SELECT * FROM orders WHERE order_id = ?''', (order_id,))
            order = self.c.fetchone()
            
            # Get order items
            self.c.execute('''SELECT product_name, quantity, unit_price, total_price 
                             FROM order_items WHERE order_id = ?''', (order_id,))
            items = self.c.fetchall()
            
            # Create details window
            details_window = Toplevel(self.master)
            details_window.title(f"Order Details - ID: {order_id}")
            details_window.geometry("500x400+200+100")
            
            # Order Information
            info_frame = LabelFrame(details_window, text="Order Information", font=('arial 10 bold'))
            info_frame.pack(fill=X, padx=10, pady=10)
            
            info_text = f"""Order ID: {order[0]}
Customer: {order[1]}
Phone: {order[2] or 'N/A'}
Date: {order[3]}
Total Amount: ${order[4]:.2f}
Status: {order[5]}
Payment Method: {order[6]}"""
            
            Label(info_frame, text=info_text, font=('arial 9'), justify=LEFT).pack(padx=10, pady=10)
            
            # Order Items
            items_frame = LabelFrame(details_window, text="Order Items", font=('arial 10 bold'))
            items_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
            
            # Create treeview for items
            columns = ('Product', 'Qty', 'Price', 'Total')
            items_tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=6)
            
            for col in columns:
                items_tree.heading(col, text=col)
                items_tree.column(col, width=100)
            
            # Add items to treeview
            for item in items:
                items_tree.insert('', 'end', values=item)
            
            items_tree.pack(fill=BOTH, expand=True, padx=5, pady=5)
            
            # Close button
            Button(details_window, text="Close", command=details_window.destroy).pack(pady=10)
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load order details: {e}")
    
    def update_order_status(self):
        selected_item = self.orders_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select an order first")
            return
        
        order_data = self.orders_tree.item(selected_item[0], 'values')
        order_id = order_data[0]
        current_status = order_data[4]
        
        # Create status selection dialog
        status_window = Toplevel(self.master)
        status_window.title("Update Order Status")
        status_window.geometry("250x150+400+300")
        
        Label(status_window, text=f"Order #{order_id}", font=('arial 10 bold')).pack(pady=5)
        
        status_var = StringVar(value=current_status)
        status_combo = ttk.Combobox(status_window, textvariable=status_var,
                                   values=['Pending', 'Completed', 'Cancelled'],
                                   state='readonly')
        status_combo.pack(pady=10)
        
        def update_status():
            try:
                self.c.execute("UPDATE orders SET status = ? WHERE order_id = ?",
                              (status_var.get(), order_id))
                self.conn.commit()
                messagebox.showinfo("Success", "Order status updated successfully!")
                status_window.destroy()
                self.load_orders()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to update status: {e}")
        
        Button(status_window, text="Update", command=update_status).pack(pady=5)
    
    def delete_order(self):
        selected_item = self.orders_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select an order first")
            return
        
        order_data = self.orders_tree.item(selected_item[0], 'values')
        order_id = order_data[0]
        
        result = messagebox.askyesno("Confirm Delete", 
                                   f"Delete order #{order_id}?")
        if result:
            try:
                # Restore product stock
                self.c.execute('''SELECT product_id, quantity FROM order_items WHERE order_id = ?''', (order_id,))
                items = self.c.fetchall()
                
                for product_id, quantity in items:
                    self.c.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (quantity, product_id))
                
                # Delete order items and order
                self.c.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
                self.c.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
                
                self.conn.commit()
                messagebox.showinfo("Success", "Order deleted successfully!")
                self.load_orders()
                self.load_available_products()
                
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to delete order: {e}")
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = Tk()
    app = OrderManagement(root)
    root.mainloop()