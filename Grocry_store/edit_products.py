# edit_products.py
from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class EditProducts:
    def __init__(self, master):
        self.master = master
        self.master.title("Edit Products")
        self.master.geometry("1000x700+200+100")
        
        self.conn = sqlite3.connect("D:\Grocry_store\Database\store.db")
        self.c = self.conn.cursor()
        
        self.create_interface()
        self.load_products()
    
    def create_interface(self):
        # Main Frame
        main_frame = Frame(self.master, padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Heading
        heading = Label(main_frame, text="Edit Products", font=('arial 20 bold'), fg='steelblue')
        heading.pack(pady=10)
        
        # Search Frame
        search_frame = Frame(main_frame)
        search_frame.pack(fill=X, pady=10)
        
        Label(search_frame, text="Search:", font=('arial 12 bold')).pack(side=LEFT, padx=5)
        self.search_var = StringVar()
        self.search_entry = Entry(search_frame, textvariable=self.search_var, width=30, font=('arial 12'))
        self.search_entry.pack(side=LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_products)
        
        Button(search_frame, text="Refresh", bg='green', fg='white',
               font=('arial 10 bold'), command=self.load_products).pack(side=LEFT, padx=5)
        
        # Products Treeview
        tree_frame = Frame(main_frame)
        tree_frame.pack(fill=BOTH, expand=True, pady=10)
        
        columns = ('ID', 'Name', 'Stock', 'Cost Price', 'Selling Price', 'Vendor', 'Vendor Phone')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Bind double click to edit
        self.tree.bind('<Double-1>', self.edit_selected_product)
        
        # Edit Form Frame
        self.edit_frame = LabelFrame(main_frame, text="Edit Product Details", font=('arial 12 bold'))
        self.edit_frame.pack(fill=X, pady=10)
        
        # Edit Form
        edit_labels = ["Product ID:", "Product Name:", "Stock:", "Cost Price:", "Selling Price:", "Vendor:", "Vendor Phone:"]
        self.edit_entries = {}
        
        for i, text in enumerate(edit_labels):
            row = i // 2
            col = (i % 2) * 2
            Label(self.edit_frame, text=text, font=('arial 10 bold')).grid(row=row, column=col, sticky='w', pady=5, padx=5)
            entry = Entry(self.edit_frame, width=20, font=('arial 10'))
            entry.grid(row=row, column=col+1, pady=5, padx=5)
            field_name = text.lower().replace(' ', '_').replace(':', '')
            self.edit_entries[field_name] = entry
        
        # Edit Buttons
        btn_frame = Frame(self.edit_frame)
        btn_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        Button(btn_frame, text="Update Product", bg='green', fg='white',
               font=('arial 10 bold'), command=self.update_product).pack(side=LEFT, padx=5)
        
        Button(btn_frame, text="Delete Product", bg='red', fg='white',
               font=('arial 10 bold'), command=self.delete_product).pack(side=LEFT, padx=5)
        
        Button(btn_frame, text="Clear Form", bg='orange', fg='white',
               font=('arial 10 bold'), command=self.clear_edit_form).pack(side=LEFT, padx=5)
        
        Button(btn_frame, text="Close", bg='gray', fg='white',
               font=('arial 10 bold'), command=self.master.destroy).pack(side=LEFT, padx=5)
    
    def load_products(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            self.c.execute("SELECT * FROM products")
            products = self.c.fetchall()
            
            for product in products:
                self.tree.insert('', 'end', values=product)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load products: {e}")
    
    def search_products(self, event=None):
        search_term = self.search_var.get().strip()
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            if search_term:
                self.c.execute('''SELECT * FROM products 
                               WHERE name LIKE ? OR vendor LIKE ? OR id LIKE ?''',
                             (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            else:
                self.c.execute("SELECT * FROM products")
            
            products = self.c.fetchall()
            
            for product in products:
                self.tree.insert('', 'end', values=product)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Search failed: {e}")
    
    def edit_selected_product(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            product_data = self.tree.item(selected_item[0], 'values')
            self.fill_edit_form(product_data)
    
    def fill_edit_form(self, product_data):
        self.clear_edit_form()
        
        # Fill the form with product data
        self.edit_entries['product_id'].insert(0, product_data[0])
        self.edit_entries['product_name'].insert(0, product_data[1])
        self.edit_entries['stock'].insert(0, product_data[2])
        self.edit_entries['cost_price'].insert(0, product_data[3])
        self.edit_entries['selling_price'].insert(0, product_data[4])
        self.edit_entries['vendor'].insert(0, product_data[5])
        self.edit_entries['vendor_phone'].insert(0, product_data[6])
    
    def update_product(self):
        try:
            product_id = self.edit_entries['product_id'].get()
            name = self.edit_entries['product_name'].get()
            stock = self.edit_entries['stock'].get()
            cp = self.edit_entries['cost_price'].get()
            sp = self.edit_entries['selling_price'].get()
            vendor = self.edit_entries['vendor'].get()
            vendor_phone = self.edit_entries['vendor_phone'].get()
            
            if not all([product_id, name, stock, cp, sp, vendor, vendor_phone]):
                messagebox.showinfo("Error", "Please fill all fields")
                return
            
            # Validate numeric fields
            try:
                stock = int(stock)
                cp = float(cp)
                sp = float(sp)
            except ValueError:
                messagebox.showinfo("Error", "Please enter valid numbers for Stock, Cost Price, and Selling Price")
                return
            
            # Calculate updated values
            assumed_profit = sp - cp
            total_cp = cp * stock
            total_sp = sp * stock
            
            self.c.execute('''UPDATE products SET 
                          name=?, stock=?, cost_price=?, selling_price=?, vendor=?, vendor_phone=?,
                          assumed_profit=?, total_cp=?, total_sp=?
                          WHERE id=?''',
                          (name, stock, cp, sp, vendor, vendor_phone, assumed_profit, total_cp, total_sp, product_id))
            self.conn.commit()
            
            messagebox.showinfo("Success", f"Product '{name}' updated successfully!")
            self.load_products()
            self.clear_edit_form()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update product: {e}")
    
    def delete_product(self):
        product_id = self.edit_entries['product_id'].get()
        if not product_id:
            messagebox.showinfo("Error", "Please select a product to delete")
            return
        
        result = messagebox.askyesno("Confirm Delete", 
                                   f"Are you sure you want to delete product ID: {product_id}?")
        if result:
            try:
                self.c.execute("DELETE FROM products WHERE id=?", (product_id,))
                self.conn.commit()
                
                messagebox.showinfo("Success", "Product deleted successfully!")
                self.load_products()
                self.clear_edit_form()
                
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to delete product: {e}")
    
    def clear_edit_form(self):
        for entry in self.edit_entries.values():
            entry.delete(0, END)
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = Tk()
    app = EditProducts(root)
    root.mainloop()