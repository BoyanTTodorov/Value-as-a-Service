import tkinter as tk
from queries import Queries
from database import DatabaseManager
from ttkbootstrap import Style, Window, ttk
from decimal import Decimal
from datetime import datetime
import threading
import pandas as pd
from tkinter import filedialog

class DataTableApp:
    def __init__(self, root):
        # Initialize the ttkbootstrap style and theme
        self.style = Style(theme='superhero')  # Change the theme if you prefer another (e.g., 'darkly', 'flatly', etc.)

        self.root = root
        self.root.title("VAS")
        self.create_widgets()

    def create_widgets(self):
        # Create a frame for date selection
        date_frame = ttk.Frame(self.root)
        date_frame.pack(pady=10)

        # Create "From" label and Entry for date
        ttk.Label(date_frame, text="From (yyyy-mm-dd):").pack(side=tk.LEFT, padx=5)
        self.start_date = ttk.Entry(date_frame)
        self.start_date.pack(side=tk.LEFT, padx=5)

        # Create "To" label and Entry for date
        ttk.Label(date_frame, text="To (yyyy-mm-dd):").pack(side=tk.LEFT, padx=5)
        self.end_date = ttk.Entry(date_frame)
        self.end_date.pack(side=tk.LEFT, padx=5)

        # Create a button to load data based on the selected date range
        load_button = ttk.Button(date_frame, text="Load Data", bootstyle="primary", command=self.start_load_data_thread)
        load_button.pack(side=tk.LEFT, padx=5)

        # Create a button to save the data to a report
        save_button = ttk.Button(date_frame, text="Save Report", bootstyle="success", command=self.save_report)
        save_button.pack(side=tk.LEFT, padx=5)

        # Create a frame for the Treeview and the loading bar
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        # Create the Treeview (table)
        self.tree = ttk.Treeview(self.main_frame, columns=("column1", "column2"), show="headings")
        self.tree.pack(expand=True, fill=tk.BOTH)

        # Define columns
        self.tree.heading("column1", text="Creation Date")
        self.tree.heading("column2", text="Quantity")

        # Create a vertical scrollbar
        self.scroll_y = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.tree.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.scroll_y.set)

        # Create a horizontal scrollbar
        self.scroll_x = ttk.Scrollbar(self.main_frame, orient="horizontal", command=self.tree.xview)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.configure(xscrollcommand=self.scroll_x.set)

        # Create a loading bar using ttkbootstrap's ttk
        self.loading_bar = ttk.Progressbar(self.main_frame, mode='indeterminate', bootstyle="info")
        self.loading_bar.pack(pady=10, fill=tk.X)
        self.loading_bar.place(relx=0.5, rely=0.9, anchor=tk.CENTER)
        self.loading_bar_visible = False

    def start_load_data_thread(self):
        # Start the loading bar and data loading in a separate thread
        if not self.loading_bar_visible:
            self.loading_bar_visible = True
            self.loading_bar.start()
        threading.Thread(target=self.load_data).start()

    def load_data(self):
        try:
            # Get the selected date range from the date entries
            start_date = self.start_date.get()
            end_date = self.end_date.get()

            # Initialize database connection and get data
            db = DatabaseManager()
            queries = Queries(start_date, end_date)  # Pass dates to Queries
            columns, rows = db.get_data(queries.vas)

            # Update the Treeview in the main thread
            self.root.after(0, self.update_treeview, columns, rows)
        finally:
            # Stop the loading bar after data is loaded
            if self.loading_bar_visible:
                self.loading_bar_visible = False
                self.loading_bar.stop()

        # Bind the Ctrl+C key to copy data from the treeview
        self.tree.bind("<Control-c>", self.copy_to_clipboard)

    def update_treeview(self, columns, rows):
        # Configure columns in Treeview
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col)

        # Clear existing rows in Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Initialize total quantity
        total_qty = Decimal(0)

        # Preprocess rows and insert into Treeview
        for row in rows:
            date_str, qty = row
            # Convert date from 'yyyymmdd' to 'yyyy-mm-dd'
            formatted_date = datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
            # Convert Decimal to int
            formatted_qty = int(qty) if isinstance(qty, Decimal) else qty
            # Add to total quantity
            total_qty += Decimal(formatted_qty)
            # Insert the processed row into the Treeview
            self.tree.insert("", tk.END, values=(formatted_date, formatted_qty))

        # Add total row to Treeview
        self.tree.insert("", tk.END, values=("Total", int(total_qty)))

    def copy_to_clipboard(self, event):
        # Get selected item
        selected_item = self.tree.selection()

        # Check if any item is selected
        if selected_item:
            # Get the values of the selected item
            item_values = self.tree.item(selected_item, "values")

            # Convert the values to a string to copy to clipboard
            item_str = "\t".join(map(str, item_values))  # Tab-separated string

            # Clear clipboard and copy the data
            self.root.clipboard_clear()
            self.root.clipboard_append(item_str)

        return "break"  # To prevent default behavior

    def save_report(self):
        # Open a file dialog to select the save location
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])

        if file_path:
            # Get all data from the Treeview except the 'Total' row
            rows = []
            for item in self.tree.get_children():
                values = self.tree.item(item)["values"]
                if values[0] != "Total":
                    rows.append(values)

            # Create a DataFrame from the Treeview data
            df = pd.DataFrame(rows, columns=["Creation Date", "Quantity"])

            # Export the DataFrame to an Excel file
            df.to_excel(file_path, index=False)
            print(f"Data exported to {file_path}")

# Main entry point using ttkbootstrap's root initialization
if __name__ == "__main__":
    root = Window(themename="superhero")  # Use ttkbootstrap's Window
    app = DataTableApp(root)
    root.mainloop()