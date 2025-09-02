import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

contacts_list = []

def normalize_number(raw: str) -> str:
    """Keep only digits and '+' for WhatsApp search"""
    raw = str(raw).strip()
    return raw.replace(" ", "")

def load_csv():
    global contacts_list
    path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])
    if not path:
        return
    try:
        df = pd.read_csv(path)
        first_col = df.iloc[:, 0].dropna().astype(str)
        contacts_list = [normalize_number(x) for x in first_col]
        messagebox.showinfo("Success", f"Loaded {len(contacts_list)} contacts from file.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load CSV: {e}")

def send_messages():
    if not contacts_list:
        messagebox.showerror("Error", "Please load a CSV file first.")
        return

    msg = message_entry.get("1.0", tk.END).strip()
    if not msg:
        messagebox.showerror("Error", "Please enter a message.")
        return

    try:
        driver = webdriver.Chrome()
        driver.get("https://web.whatsapp.com")
        messagebox.showinfo("Login", "Scan the QR code in WhatsApp Web, then click OK.")
        wait = WebDriverWait(driver, 60)
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']")))

        for contact in contacts_list:
            try:
                # Locate search box
                search_box = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//div[@contenteditable='true' and @role='textbox']")))
                search_box.clear()
                search_box.send_keys(contact)
                time.sleep(2)
                search_box.send_keys(Keys.ENTER)
                time.sleep(2)

                # Message box
                message_box = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//div[@contenteditable='true' and @role='textbox' and @data-tab='10']")))
                message_box.send_keys(msg)
                message_box.send_keys(Keys.ENTER)
                time.sleep(1)

                status_label.config(text=f"Sent to {contact}")
                root.update()
            except Exception as e:
                messagebox.showerror("Error", f"Failed for {contact}: {e}")

        messagebox.showinfo("Done", "All messages sent successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Selenium error: {e}")

# GUI
root = tk.Tk()
root.title("WhatsApp Bulk Messenger (Fast)")
root.geometry("500x400")

tk.Label(root, text="Enter Message:", font=("Arial", 12)).pack(pady=5)
message_entry = tk.Text(root, height=5, width=50)
message_entry.pack(pady=5)

tk.Button(root, text="Load Contacts from CSV", font=("Arial", 12), command=load_csv).pack(pady=10)
tk.Button(root, text="Send Messages", font=("Arial", 12), command=send_messages).pack(pady=10)

status_label = tk.Label(root, text="", font=("Arial", 10), fg="green")
status_label.pack(pady=5)

root.mainloop()
