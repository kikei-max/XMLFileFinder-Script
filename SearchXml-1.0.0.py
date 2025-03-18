import os
import re
import time
import json
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

def install_package(package):
    """Install the package using pip."""
    subprocess.check_call([os.sys.executable, "-m", "pip", "install", package])

required_packages = ["tkinter"]

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"Package {package} not found. Installing...")
        install_package(package)

stop_search = False
directory = ""
CONFIG_FILE = "config.json"

def save_config():
    """Save selected folder"""
    if directory:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"directory": directory}, f)
        messagebox.showinfo("Info", "Folder saved successfully!")

def load_config():
    """Load folder from config file"""
    global directory
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            directory = config.get("directory", "")
            if directory and os.path.exists(directory):
                load_xml_files(auto_load=True)
            else:
                directory = ""

    result_text.delete(1.0, tk.END) 
    result_text.insert(tk.END, "SearchXml-1.0.0\n\n")
    result_text.insert(tk.END, "Instructions: This tool is designed for searching XML files. It allows users to search for specific keywords in XML documents located in a selected directory.\n\n")
    result_text.insert(tk.END, "Developer: t-400\n")
    result_text.insert(tk.END, "Discord: https://discord.gg/PSmcjwNYtD\n")
    result_text.insert(tk.END, "YouTube: https://www.youtube.com/@Zoltraak813\n\n")
    result_text.insert(tk.END, "License: This software is provided 'as is', without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.\n")
    result_text.insert(tk.END, "\n")
    result_text.insert(tk.END, "You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit others to whom the Software is provided to do so, subject to the following conditions:\n")
    result_text.insert(tk.END, " - The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n")
    result_text.insert(tk.END, " - The software is not guaranteed to be free of errors or defects.\n")
    result_text.insert(tk.END, " - The software may not be used for illegal purposes or activities.\n")

def clear_config():
    """Delete config file"""
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
        directory = ""
        xml_listbox.delete(0, tk.END)
        messagebox.showinfo("Info", "Saved folder removed!")

def load_xml_files(auto_load=False):
    """Select folder and display XML files"""
    global directory
    if not auto_load:
        directory = filedialog.askdirectory()

    if not directory:
        return

    xml_listbox.delete(0, tk.END)

    xml_files = [f for f in os.listdir(directory) if f.endswith(".xml")]

    if not xml_files:
        messagebox.showinfo("Info", "No XML files found.")
        return

    for xml_file in xml_files:
        xml_listbox.insert(tk.END, xml_file)

def reload_xml_files():
    """Reload XML files from the current folder"""
    if directory:
        load_xml_files(auto_load=True)
        messagebox.showinfo("Info", "XML files reloaded successfully!")
    else:
        messagebox.showwarning("Warning", "No folder selected!")

def search_in_xml():
    """Search XML files"""
    global stop_search
    stop_search = False
    search_keyword = keyword_entry.get().strip()

    if not search_keyword:
        messagebox.showwarning("Warning", "Please enter a search keyword!")
        return

    if not directory:
        messagebox.showwarning("Warning", "Please select an XML folder!")
        return

    xml_files = [f for f in os.listdir(directory) if f.endswith(".xml")]

    if not xml_files:
        messagebox.showinfo("Info", "No XML files found.")
        return

    result_text.delete(1.0, tk.END) 
    status_text.delete(1.0, tk.END)  

    total_files = len(xml_files)
    start_time = time.time()

    def run_search():
        global stop_search
        for index, xml_file in enumerate(xml_files, start=1):
            if stop_search:
                status_text.insert(tk.END, "Search stopped.\n")
                break

            file_path = os.path.join(directory, xml_file)

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                matches = re.findall(r'<entry name="([^"]*' + re.escape(search_keyword) + r'[^"]*)">', content, re.IGNORECASE)

                for match in matches:
                    code_block = re.search(rf'<entry name="{re.escape(match)}".*?<code>(.*?)</code>', content, re.DOTALL)
                    code_text = code_block.group(1).strip() if code_block else "No Code"

                    result_text.insert(tk.END, f"--- {xml_file} ---\n")
                    result_text.insert(tk.END, f"Entry Name: {match}\n")
                    result_text.insert(tk.END, f"Code:\n{code_text}\n")
                    result_text.insert(tk.END, "-" * 50 + "\n")
                    status_text.insert(tk.END, f"[Notice] Found '{search_keyword}' in {xml_file}\n")
                    status_text.see(tk.END)

            except Exception as e:
                status_text.insert(tk.END, f"[Error] Issue in {xml_file}: {e}\n")

            elapsed_time = time.time() - start_time
            progress = (index / total_files) * 100
            estimated_total_time = (elapsed_time / index) * total_files if index > 0 else 0
            remaining_time = estimated_total_time - elapsed_time

            status_text.insert(tk.END, f"Progress: {index}/{total_files} ({progress:.2f}%) - {remaining_time:.2f}\n")
            status_text.see(tk.END)

        status_text.insert(tk.END, "\nSearch completed!\n")

    search_thread = threading.Thread(target=run_search)
    search_thread.start()

def stop_searching():
    """Stop search"""
    global stop_search
    stop_search = True

def reset_all():
    """Reset all data"""
    global directory
    directory = ""
    xml_listbox.delete(0, tk.END)
    result_text.delete(1.0, tk.END)
    status_text.delete(1.0, tk.END)
    keyword_entry.delete(0, tk.END)
    messagebox.showinfo("Info", "All data has been reset!")

def preview_selected_xml(event):
    """Preview selected XML file"""
    selected_index = xml_listbox.curselection()

    if not selected_index:
        return

    xml_file = xml_listbox.get(selected_index[0])
    file_path = os.path.join(directory, xml_file)

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"--- {xml_file} ---\n")
        result_text.insert(tk.END, content)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load {xml_file}: {e}")

root = tk.Tk()
root.title("Xml-1.0.0")
root.geometry("1150x700")
root.resizable(False, False)
top_frame = tk.Frame(root)
top_frame.pack(padx=10, pady=5, fill="x")

load_button = tk.Button(top_frame, text="Load XML", command=load_xml_files, width=12, bg="white")
load_button.pack(side="left", padx=5)

reload_button = tk.Button(top_frame, text="Reload", command=reload_xml_files, width=12, bg="white")
reload_button.pack(side="left", padx=5)

save_button = tk.Button(top_frame, text="Save", command=save_config, width=12, bg="white")
save_button.pack(side="left", padx=5)

clear_button = tk.Button(top_frame, text="Clear Save", command=clear_config, width=12, bg="white")
clear_button.pack(side="left", padx=5)

keyword_label = tk.Label(top_frame, text="Keyword:")
keyword_label.pack(side="left", padx=5)

keyword_entry = tk.Entry(top_frame, width=30)
keyword_entry.pack(side="left", padx=5)

search_button = tk.Button(top_frame, text="Start Search", command=search_in_xml, width=12, bg="white")
search_button.pack(side="left", padx=5)

stop_button = tk.Button(top_frame, text="Stop", command=stop_searching, width=12, bg="white")
stop_button.pack(side="left", padx=5)

reset_button = tk.Button(top_frame, text="Reset", command=reset_all, width=12, bg="white")
reset_button.pack(side="left", padx=5)

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

xml_listbox = tk.Listbox(main_frame, width=50)
xml_listbox.pack(side="left", fill="y")
xml_listbox.bind("<<ListboxSelect>>", preview_selected_xml)

result_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD)
result_text.pack(side="right", fill="both", expand=True)

status_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=8)
status_text.pack(fill="both", expand=True)

load_config()
root.mainloop()