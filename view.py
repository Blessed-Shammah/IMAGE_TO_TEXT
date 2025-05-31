import tkinter as tk
from tkinter import ttk, messagebox
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import csv
import os
import time
import random

class CSVViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Viewer and Search")
        self.root.geometry("600x500")

        # GUI Elements
        self.label = tk.Label(root, text="Names from extracted_list.csv")
        self.label.pack(pady=10)

        # Search Bar
        self.search_frame = tk.Frame(root)
        self.search_frame.pack(fill=tk.X, padx=5)

        self.search_label = tk.Label(self.search_frame, text="Search:")
        self.search_label.pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_list)
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.clear_btn = tk.Button(self.search_frame, text="Clear", command=self.clear_search)
        self.clear_btn.pack(side=tk.LEFT)

        # Frame for Treeview and buttons
        self.tree_frame = tk.Frame(root)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview for displaying names
        self.tree = ttk.Treeview(self.tree_frame, columns=("Copy", "Name", "Tag"), show="headings")
        self.tree.heading("Copy", text="")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Tag", text="Tag")
        self.tree.column("Copy", width=50, anchor="center")
        self.tree.column("Name", width=350)
        self.tree.column("Tag", width=100)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Results Text Area
        self.result_label = tk.Label(root, text="Search Results:")
        self.result_label.pack(pady=5)
        self.result_text = tk.Text(root, height=10, width=70)
        self.result_text.pack(pady=5, padx=5)

        # Load CSV data
        self.names = []
        self.searched = {}  # Track searched names
        self.load_csv()

        # Bind double-click event to search
        self.tree.bind("<Double-1>", self.on_name_click)

        # Bind root window close to ensure cleanup
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_csv(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        csv_file = "extracted_list.csv"
        if not os.path.exists(csv_file):
            messagebox.showerror("Error", f"{csv_file} not found!")
            return

        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader)
                self.names = [row[0] for row in reader if row]

            for name in self.names:
                # Insert row with a placeholder for the Copy button
                item_id = self.tree.insert("", tk.END, values=("", name, self.searched.get(name, "")))
                # Add static Copy button
                copy_button = tk.Button(self.tree_frame, text="Copy", command=lambda n=name: self.copy_to_clipboard(n))
                bbox = self.tree.bbox(item_id, column="Copy")
                if bbox:
                    x, y, _, _ = bbox
                    copy_button.place(x=x + 5, y=y + 5)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")

    def update_list(self, *args):
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_term = self.search_var.get().lower()
        filtered_names = [name for name in self.names if search_term in name.lower()]

        for name in filtered_names:
            item_id = self.tree.insert("", tk.END, values=("", name, self.searched.get(name, "")))
            copy_button = tk.Button(self.tree_frame, text="Copy", command=lambda n=name: self.copy_to_clipboard(n))
            bbox = self.tree.bbox(item_id, column="Copy")
            if bbox:
                x, y, _, _ = bbox
                copy_button.place(x=x + 5, y=y + 5)

    def clear_search(self):
        self.search_var.set("")
        self.update_list()

    def on_name_click(self, event):
        item = self.tree.selection()
        if item:
            name = self.tree.item(item, "values")[1]  # Index 1 is Name (after Copy column)
            self.search_and_display(name, name)

    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", f"{text} copied to clipboard!")

    def search_and_display(self, name, query):
        try:
            # Configure Chrome options to make it look more human-like
            chrome_options = Options()
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

            # Initialize Selenium WebDriver
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                """
            })

            driver.get("https://www.google.com")
            time.sleep(random.uniform(2, 4))

            # Find search box and enter query
            search_box = driver.find_element("name", "q")
            search_box.send_keys(f"{query}")
            search_box.send_keys(Keys.RETURN)
            time.sleep(random.uniform(3, 5))

            # Get the page source and extract text for display
            results = driver.find_element("tag name", "body").text
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, results[:1000])

            # Mark as searched
            self.searched[name] = "Searched"
            self.update_list()

            # Keep browser open until manually closed
            # Driver will be stored to close on application exit

        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")
            if 'driver' in locals():
                driver.quit()

    def on_closing(self):
        # Clean up any remaining browser instances
        if hasattr(self, 'driver'):
            self.driver.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVViewerApp(root)
    root.mainloop()