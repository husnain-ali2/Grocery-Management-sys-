# add_product.py
from tkinter import *
import tkinter as tk
import sqlite3
from tkinter import messagebox

class AddProduct:
    def __init__(self, master):
        self.master = master
        self.master.title("Add New Product")
        self.master.geometry("600x500+400+200")
        
        self.conn = sqlite3.connect("D:\Grocry_store\Database\store.db")
        self.c = self.conn.cursor()
        
        self.last_id = self.get_next_id()
        self.entries_list = []  # List to track entry order for navigation
        self.current_focus_index = 1  # Start from product name (skip product ID)
        self.create_form()
        self.bind_keyboard_events()
    
    def get_next_id(self):
        try:
            self.c.execute("SELECT MAX(id) FROM products")
            result = self.c.fetchone()
            return 1 if result[0] is None else result[0] + 1
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to get next ID: {e}")
            return 1
    
    def create_form(self):
        # Main Frame
        main_frame = Frame(self.master, padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Heading
        heading = Label(main_frame, text="Add New Product", font=('arial 20 bold'), fg='steelblue')
        heading.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Form Labels and Entries
        labels = [
            ("Product ID:", 1),
            ("Product Name:", 2),
            ("Stock:", 3),
            ("Cost Price:", 4),
            ("Selling Price:", 5),
            ("Vendor:", 6),
            ("Vendor Phone:", 7)
        ]
        
        self.entries = {}
        self.entries_list = []  # Reset list
        
        for i, (text, row) in enumerate(labels):
            label = Label(main_frame, text=text, font=('arial 12 bold'))
            label.grid(row=row, column=0, sticky='w', pady=10, padx=10)
            
            if text == "Product ID:":
                entry = Entry(main_frame, width=25, font=('arial 12'), state='readonly', bg='lightyellow')
                entry.insert(0, str(self.last_id))
            else:
                entry = Entry(main_frame, width=25, font=('arial 12'))
            
            entry.grid(row=row, column=1, pady=10, padx=10)
            field_name = text.lower().replace(' ', '_').replace(':', '')
            self.entries[field_name] = entry
            self.entries_list.append(entry)  # Add to navigation list
        
        # Buttons
        btn_frame = Frame(main_frame)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=30)
        
        self.btn_add = Button(btn_frame, text="Add Product", width=15, height=2,
               bg='steelblue', fg='white', font=('arial 12 bold'),
               command=self.add_product)
        self.btn_add.pack(side=LEFT, padx=10)
        
        self.btn_clear = Button(btn_frame, text="Clear", width=15, height=2,
               bg='orange', fg='white', font=('arial 12 bold'),
               command=self.clear_form)
        self.btn_clear.pack(side=LEFT, padx=10)
        
        self.btn_close = Button(btn_frame, text="Close", width=15, height=2,
               bg='red', fg='white', font=('arial 12 bold'),
               command=self.master.destroy)
        self.btn_close.pack(side=LEFT, padx=10)
        
        # Add buttons to navigation list
        self.entries_list.extend([self.btn_add, self.btn_clear, self.btn_close])
        
        # Set focus to name field
        self.entries['product_name'].focus_set()
        self.current_focus_index = 1  # Product name is at index 1
    
    def bind_keyboard_events(self):
        # Bind keyboard events to the master window
        self.master.bind('<Down>', self.navigate_down)
        self.master.bind('<Up>', self.navigate_up)
        self.master.bind('<Return>', self.handle_enter)
        self.master.bind('<Escape>', lambda e: self.master.destroy())
        
        # Bind Tab key for normal tab navigation
        self.master.bind('<Tab>', self.handle_tab)
        
        # Additional shortcuts
        self.master.bind('<F1>', lambda e: self.add_product())
        self.master.bind('<F2>', lambda e: self.clear_form())
        self.master.bind('<F3>', lambda e: self.master.destroy())
    
    def navigate_down(self, event):
        """Move focus to next field using Down arrow"""
        if self.current_focus_index < len(self.entries_list) - 1:
            self.current_focus_index += 1
            self.set_focus_to_current()
        return "break"  # Prevent default behavior
    
    def navigate_up(self, event):
        """Move focus to previous field using Up arrow"""
        if self.current_focus_index > 0:
            self.current_focus_index -= 1
            self.set_focus_to_current()
        return "break"  # Prevent default behavior
    
    def set_focus_to_current(self):
        """Set focus to the current field in navigation"""
        current_widget = self.entries_list[self.current_focus_index]
        current_widget.focus_set()
        
        # If it's an Entry widget, select all text for easy editing
        if isinstance(current_widget, Entry):
            current_widget.select_range(0, END)
    
    def handle_enter(self, event):
        """Handle Enter key - Add product if on last field, otherwise move down"""
        if self.current_focus_index == len(self.entries_list) - 3:  # Add Product button
            self.add_product()
        elif self.current_focus_index == len(self.entries_list) - 2:  # Clear button
            self.clear_form()
        elif self.current_focus_index == len(self.entries_list) - 1:  # Close button
            self.master.destroy()
        else:
            self.navigate_down(event)
        return "break"
    
    def handle_tab(self, event):
        """Handle Tab key for normal navigation and update current focus index"""
        # Let the default tab navigation happen
        self.master.after(10, self.update_focus_index)
        return None  # Allow default tab behavior
    
    def update_focus_index(self):
        """Update current focus index based on which widget has focus"""
        focused_widget = self.master.focus_get()
        if focused_widget in self.entries_list:
            self.current_focus_index = self.entries_list.index(focused_widget)
    
    def add_product(self):
        name = self.entries['product_name'].get().strip()
        stock = self.entries['stock'].get().strip()
        cp = self.entries['cost_price'].get().strip()
        sp = self.entries['selling_price'].get().strip()
        vendor = self.entries['vendor'].get().strip()
        vendor_phone = self.entries['vendor_phone'].get().strip()
        
        # Validate all fields are filled
        if not all([name, stock, cp, sp, vendor, vendor_phone]):
            messagebox.showinfo("Error", "Please fill all the entries")
            self.entries['product_name'].focus_set()
            self.current_focus_index = 1
            return
        
        # Validate numeric fields
        try:
            stock = int(stock)
            cp = float(cp)
            sp = float(sp)
        except ValueError:
            messagebox.showinfo("Error", "Please enter valid numbers for Stock, Cost Price, and Selling Price")
            self.entries['stock'].focus_set()
            self.current_focus_index = 2
            return
        
        # Validate positive values
        if stock <= 0 or cp <= 0 or sp <= 0:
            messagebox.showinfo("Error", "Please enter positive values for Stock, Cost Price, and Selling Price")
            self.entries['stock'].focus_set()
            self.current_focus_index = 2
            return
        
        # Calculate additional fields
        assumed_profit = sp - cp
        total_cp = cp * stock
        total_sp = sp * stock
        
        # Insert into database
        try:
            self.c.execute('''INSERT INTO products 
                          (name, stock, cost_price, selling_price, vendor, vendor_phone, assumed_profit, total_cp, total_sp) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (name, stock, cp, sp, vendor, vendor_phone, assumed_profit, total_cp, total_sp))
            self.conn.commit()
            
            # Get the actual assigned ID
            self.c.execute("SELECT last_insert_rowid()")
            assigned_id = self.c.fetchone()[0]
            
            messagebox.showinfo("Success", f"Product '{name}' added successfully!\nProduct ID: {assigned_id}")
            self.clear_form()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add product: {e}")
    
    def clear_form(self):
        for field_name, entry in self.entries.items():
            if field_name != 'product_id':
                entry.delete(0, END)
        self.entries['product_name'].focus_set()
        self.current_focus_index = 1
        self.refresh_id()
    
    def refresh_id(self):
        self.last_id = self.get_next_id()
        self.entries['product_id'].config(state='normal')
        self.entries['product_id'].delete(0, END)
        self.entries['product_id'].insert(0, str(self.last_id))
        self.entries['product_id'].config(state='readonly')
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = Tk()
    app = AddProduct(root)
    root.mainloop()# add_product.py
from tkinter import *
import tkinter as tk
import sqlite3
from tkinter import messagebox

class AddProduct:
    def __init__(self, master):
        self.master = master
        self.master.title("Add New Product")
        self.master.geometry("600x500+400+200")
        
        self.conn = sqlite3.connect("D:\Grocry_store\Database\store.db")
        self.c = self.conn.cursor()
        
        self.last_id = self.get_next_id()
        self.entries_list = []  # List to track entry order for navigation
        self.current_focus_index = 1  # Start from product name (skip product ID)
        self.create_form()
        self.bind_keyboard_events()
    
    def get_next_id(self):
        try:
            self.c.execute("SELECT MAX(id) FROM products")
            result = self.c.fetchone()
            return 1 if result[0] is None else result[0] + 1
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to get next ID: {e}")
            return 1
    
    def create_form(self):
        # Main Frame
        main_frame = Frame(self.master, padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Heading
        heading = Label(main_frame, text="Add New Product", font=('arial 20 bold'), fg='steelblue')
        heading.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Form Labels and Entries
        labels = [
            ("Product ID:", 1),
            ("Product Name:", 2),
            ("Stock:", 3),
            ("Cost Price:", 4),
            ("Selling Price:", 5),
            ("Vendor:", 6),
            ("Vendor Phone:", 7)
        ]
        
        self.entries = {}
        self.entries_list = []  # Reset list
        
        for i, (text, row) in enumerate(labels):
            label = Label(main_frame, text=text, font=('arial 12 bold'))
            label.grid(row=row, column=0, sticky='w', pady=10, padx=10)
            
            if text == "Product ID:":
                entry = Entry(main_frame, width=25, font=('arial 12'), state='readonly', bg='lightyellow')
                entry.insert(0, str(self.last_id))
            else:
                entry = Entry(main_frame, width=25, font=('arial 12'))
            
            entry.grid(row=row, column=1, pady=10, padx=10)
            field_name = text.lower().replace(' ', '_').replace(':', '')
            self.entries[field_name] = entry
            self.entries_list.append(entry)  # Add to navigation list
        
        # Buttons
        btn_frame = Frame(main_frame)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=30)
        
        self.btn_add = Button(btn_frame, text="Add Product", width=15, height=2,
               bg='steelblue', fg='white', font=('arial 12 bold'),
               command=self.add_product)
        self.btn_add.pack(side=LEFT, padx=10)
        
        self.btn_clear = Button(btn_frame, text="Clear", width=15, height=2,
               bg='orange', fg='white', font=('arial 12 bold'),
               command=self.clear_form)
        self.btn_clear.pack(side=LEFT, padx=10)
        
        self.btn_close = Button(btn_frame, text="Close", width=15, height=2,
               bg='red', fg='white', font=('arial 12 bold'),
               command=self.master.destroy)
        self.btn_close.pack(side=LEFT, padx=10)
        
        # Add buttons to navigation list
        self.entries_list.extend([self.btn_add, self.btn_clear, self.btn_close])
        
        # Set focus to name field
        self.entries['product_name'].focus_set()
        self.current_focus_index = 1  # Product name is at index 1
    
    def bind_keyboard_events(self):
        # Bind keyboard events to the master window
        self.master.bind('<Down>', self.navigate_down)
        self.master.bind('<Up>', self.navigate_up)
        self.master.bind('<Return>', self.handle_enter)
        self.master.bind('<Escape>', lambda e: self.master.destroy())
        
        # Bind Tab key for normal tab navigation
        self.master.bind('<Tab>', self.handle_tab)
        
        # Additional shortcuts
        self.master.bind('<F1>', lambda e: self.add_product())
        self.master.bind('<F2>', lambda e: self.clear_form())
        self.master.bind('<F3>', lambda e: self.master.destroy())
    
    def navigate_down(self, event):
        """Move focus to next field using Down arrow"""
        if self.current_focus_index < len(self.entries_list) - 1:
            self.current_focus_index += 1
            self.set_focus_to_current()
        return "break"  # Prevent default behavior
    
    def navigate_up(self, event):
        """Move focus to previous field using Up arrow"""
        if self.current_focus_index > 0:
            self.current_focus_index -= 1
            self.set_focus_to_current()
        return "break"  # Prevent default behavior
    
    def set_focus_to_current(self):
        """Set focus to the current field in navigation"""
        current_widget = self.entries_list[self.current_focus_index]
        current_widget.focus_set()
        
        # If it's an Entry widget, select all text for easy editing
        if isinstance(current_widget, Entry):
            current_widget.select_range(0, END)
    
    def handle_enter(self, event):
        """Handle Enter key - Add product if on last field, otherwise move down"""
        if self.current_focus_index == len(self.entries_list) - 3:  # Add Product button
            self.add_product()
        elif self.current_focus_index == len(self.entries_list) - 2:  # Clear button
            self.clear_form()
        elif self.current_focus_index == len(self.entries_list) - 1:  # Close button
            self.master.destroy()
        else:
            self.navigate_down(event)
        return "break"
    
    def handle_tab(self, event):
        """Handle Tab key for normal navigation and update current focus index"""
        # Let the default tab navigation happen
        self.master.after(10, self.update_focus_index)
        return None  # Allow default tab behavior
    
    def update_focus_index(self):
        """Update current focus index based on which widget has focus"""
        focused_widget = self.master.focus_get()
        if focused_widget in self.entries_list:
            self.current_focus_index = self.entries_list.index(focused_widget)
    
    def add_product(self):
        name = self.entries['product_name'].get().strip()
        stock = self.entries['stock'].get().strip()
        cp = self.entries['cost_price'].get().strip()
        sp = self.entries['selling_price'].get().strip()
        vendor = self.entries['vendor'].get().strip()
        vendor_phone = self.entries['vendor_phone'].get().strip()
        
        # Validate all fields are filled
        if not all([name, stock, cp, sp, vendor, vendor_phone]):
            messagebox.showinfo("Error", "Please fill all the entries")
            self.entries['product_name'].focus_set()
            self.current_focus_index = 1
            return
        
        # Validate numeric fields
        try:
            stock = int(stock)
            cp = float(cp)
            sp = float(sp)
        except ValueError:
            messagebox.showinfo("Error", "Please enter valid numbers for Stock, Cost Price, and Selling Price")
            self.entries['stock'].focus_set()
            self.current_focus_index = 2
            return
        
        # Validate positive values
        if stock <= 0 or cp <= 0 or sp <= 0:
            messagebox.showinfo("Error", "Please enter positive values for Stock, Cost Price, and Selling Price")
            self.entries['stock'].focus_set()
            self.current_focus_index = 2
            return
        
        # Calculate additional fields
        assumed_profit = sp - cp
        total_cp = cp * stock
        total_sp = sp * stock
        
        # Insert into database
        try:
            self.c.execute('''INSERT INTO products 
                          (name, stock, cost_price, selling_price, vendor, vendor_phone, assumed_profit, total_cp, total_sp) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (name, stock, cp, sp, vendor, vendor_phone, assumed_profit, total_cp, total_sp))
            self.conn.commit()
            
            # Get the actual assigned ID
            self.c.execute("SELECT last_insert_rowid()")
            assigned_id = self.c.fetchone()[0]
            
            messagebox.showinfo("Success", f"Product '{name}' added successfully!\nProduct ID: {assigned_id}")
            self.clear_form()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add product: {e}")
    
    def clear_form(self):
        for field_name, entry in self.entries.items():
            if field_name != 'product_id':
                entry.delete(0, END)
        self.entries['product_name'].focus_set()
        self.current_focus_index = 1
        self.refresh_id()
    
    def refresh_id(self):
        self.last_id = self.get_next_id()
        self.entries['product_id'].config(state='normal')
        self.entries['product_id'].delete(0, END)
        self.entries['product_id'].insert(0, str(self.last_id))
        self.entries['product_id'].config(state='readonly')
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = Tk()
    app = AddProduct(root)
    root.mainloop()