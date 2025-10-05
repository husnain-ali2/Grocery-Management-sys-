# view_products.py
from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import subprocess

class ViewProducts:
    def __init__(self, master):
        self.master = master
        self.master.title("View All Products")
        self.master.geometry("1200x700+100+50")
        
        self.conn = sqlite3.connect("D:\Grocry_store\Database\store.db")
        self.c = self.conn.cursor()
        
        self.create_interface()
        self.load_products()
    
    def create_interface(self):
        # Main Frame
        main_frame = Frame(self.master, padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Heading
        heading = Label(main_frame, text="All Products", font=('arial 20 bold'), fg='steelblue')
        heading.pack(pady=10)
        
        # Controls Frame
        controls_frame = Frame(main_frame)
        controls_frame.pack(fill=X, pady=10)
        
        # Search
        Label(controls_frame, text="Search:", font=('arial 12 bold')).pack(side=LEFT, padx=5)
        self.search_var = StringVar()
        self.search_entry = Entry(controls_frame, textvariable=self.search_var, width=30, font=('arial 12'))
        self.search_entry.pack(side=LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_products)
        
        # Buttons
        Button(controls_frame, text="Refresh", bg='green', fg='white',
               font=('arial 10 bold'), command=self.load_products).pack(side=LEFT, padx=5)
        
        Button(controls_frame, text="Generate PDF", bg='purple', fg='white',
               font=('arial 10 bold'), command=self.generate_pdf).pack(side=LEFT, padx=5)
        
        Button(controls_frame, text="Close", bg='red', fg='white',
               font=('arial 10 bold'), command=self.master.destroy).pack(side=LEFT, padx=5)
        
        # Statistics Frame
        self.stats_frame = Frame(main_frame, bg='lightgray', relief='raised', bd=2)
        self.stats_frame.pack(fill=X, pady=5)
        
        # Products Treeview
        tree_frame = Frame(main_frame)
        tree_frame.pack(fill=BOTH, expand=True, pady=10)
        
        columns = ('ID', 'Name', 'Stock', 'Cost Price', 'Selling Price', 'Vendor', 
                  'Vendor Phone', 'Profit/Unit', 'Total Cost', 'Total Revenue')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        # Define headings and columns
        column_widths = {
            'ID': 50, 'Name': 150, 'Stock': 80, 'Cost Price': 100, 'Selling Price': 100,
            'Vendor': 120, 'Vendor Phone': 120, 'Profit/Unit': 100, 'Total Cost': 100, 'Total Revenue': 100
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.pack(side=RIGHT, fill=Y)
        h_scrollbar.pack(side=BOTTOM, fill=X)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
    
    def load_products(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            self.c.execute("SELECT * FROM products")
            products = self.c.fetchall()
            
            total_products = len(products)
            total_stock = sum(product[2] for product in products)
            total_investment = sum(product[8] for product in products)  # total_cp
            total_revenue = sum(product[9] for product in products)     # total_sp
            
            # Update statistics
            self.update_statistics(total_products, total_stock, total_investment, total_revenue)
            
            for product in products:
                # Format currency values
                formatted_product = list(product)
                formatted_product[3] = f"${product[3]:.2f}"  # cost_price
                formatted_product[4] = f"${product[4]:.2f}"  # selling_price
                formatted_product[7] = f"${product[7]:.2f}"  # assumed_profit
                formatted_product[8] = f"${product[8]:.2f}"  # total_cp
                formatted_product[9] = f"${product[9]:.2f}"  # total_sp
                
                self.tree.insert('', 'end', values=formatted_product)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load products: {e}")
    
    def update_statistics(self, total_products, total_stock, total_investment, total_revenue):
        # Clear previous statistics
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Create statistics labels
        stats = [
            f"Total Products: {total_products}",
            f"Total Stock: {total_stock}",
            f"Total Investment: ${total_investment:.2f}",
            f"Potential Revenue: ${total_revenue:.2f}",
            f"Potential Profit: ${total_revenue - total_investment:.2f}"
        ]
        
        for i, stat in enumerate(stats):
            Label(self.stats_frame, text=stat, font=('arial 10 bold'), 
                  bg='lightgray').grid(row=0, column=i, padx=20, pady=5)
    
    def search_products(self, event=None):
        search_term = self.search_var.get().strip()
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            if search_term:
                self.c.execute('''SELECT * FROM products 
                               WHERE name LIKE ? OR vendor LIKE ? OR id LIKE ? OR vendor_phone LIKE ?''',
                             (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            else:
                self.c.execute("SELECT * FROM products")
            
            products = self.c.fetchall()
            
            for product in products:
                # Format currency values
                formatted_product = list(product)
                formatted_product[3] = f"${product[3]:.2f}"
                formatted_product[4] = f"${product[4]:.2f}"
                formatted_product[7] = f"${product[7]:.2f}"
                formatted_product[8] = f"${product[8]:.2f}"
                formatted_product[9] = f"${product[9]:.2f}"
                
                self.tree.insert('', 'end', values=formatted_product)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Search failed: {e}")
    
    def generate_pdf(self):
        try:
            subprocess.Popen(['python', 'generate_pdf.py'])
            messagebox.showinfo("Success", "PDF generation started in separate window!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF: {e}")
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = Tk()
    app = ViewProducts(root)
    root.mainloop()