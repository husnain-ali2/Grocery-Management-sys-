# main_app.py
from tkinter import *
import tkinter as tk
from tkinter import messagebox
import subprocess
import os

class MainApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Grocery Store Management System")
        self.master.geometry("800x700+300+100")  # Increased height for new button
        self.master.configure(bg='#ecf0f1')
        
        self.create_main_interface()
    
    def create_main_interface(self):
        # Header
        header_frame = Frame(self.master, bg='#2c3e50', height=100)
        header_frame.pack(fill=X)
        header_frame.pack_propagate(False)
        
        Label(header_frame, text="Grocery Store Management System", 
              font=('Arial', 24, 'bold'), fg='white', bg='#2c3e50').pack(expand=True)
        
        # Main Content
        main_frame = Frame(self.master, bg='#ecf0f1', padx=50, pady=50)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Buttons
        buttons = [
            ("Add New Product", "#3498db", self.open_add_product),
            ("Edit Products", "#2ecc71", self.open_edit_products),
            ("View All Products", "#e74c3c", self.open_view_products),
            ("Manage Orders", "#f39c12", self.open_orders),  # New Order button
            ("Exit", "#95a5a6", self.master.quit)
        ]
        
        for i, (text, color, command) in enumerate(buttons):
            btn = Button(main_frame, text=text, width=25, height=3,
                        bg=color, fg='white', font=('Arial', 14, 'bold'),
                        command=command)
            btn.pack(pady=10)  # Reduced padding to fit all buttons
    
    def open_add_product(self):
        try:
            subprocess.Popen(['python', 'add_product.py'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Add Product: {e}")
    
    def open_edit_products(self):
        try:
            subprocess.Popen(['python', 'edit_products.py'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Edit Products: {e}")
    
    def open_view_products(self):
        try:
            subprocess.Popen(['python', 'view_products.py'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open View Products: {e}")
    
    def open_orders(self):
        try:
            subprocess.Popen(['python', 'orders.py'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Orders: {e}")
    
if __name__ == "__main__":
    root = Tk()
    app = MainApp(root)
    root.mainloop()