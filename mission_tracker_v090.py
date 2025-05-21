# Final version of mission_tracker.py (aka MRGT main executable)
# This script includes GUI, Inara + EDDB integration, config handling, and theming.

import tkinter as tk
from tkinter import ttk
import requests
import json
import os

CONFIG_DIR = "C:\\MRGT\\config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "mrgt_config.json")


import urllib.request

def check_for_updates(local_version="0.90"):
    try:
        with urllib.request.urlopen("https://raw.githubusercontent.com/polecatspeaks/mrgt/main/version.json") as response:
            data = json.loads(response.read())
            latest_version = data["version"]
            if latest_version != local_version:
                print(f"⚠️  Update available: {latest_version} (You have: {local_version})")
                print("🔗 Download it from:", data["download_url"])
    except Exception as e:
        print(f"Update check failed: {e}")
def ensure_config():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    if not os.path.exists(CONFIG_FILE):
        api_key = input("Enter your INARA API Key: ").strip()
        cmdr_name = input("Enter your Commander Name: ").strip()
        with open(CONFIG_FILE, "w") as f:
            json.dump({ "INARA_API_KEY": api_key, "INARA_CMDR_NAME": cmdr_name }, f)

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

stations = [
    {
        "Station": "Hooke Gateway",
        "System": "LP 128-32",
        "Factions": "Alliance - Multiple",
        "Mission Types": "Courier, Data, Trade",
        "Suggested Actions": "Stack courier/data missions to other 2 stations, take light cargo trade missions"
    },
    {
        "Station": "Youll Terminal",
        "System": "LP 128-32",
        "Factions": "Alliance - Multiple",
        "Mission Types": "Courier, Data, Trade",
        "Suggested Actions": "Deliver missions, accept return loops, stack new missions back"
    },
    {
        "Station": "Celsius Gateway",
        "System": "LP 128-32",
        "Factions": "Alliance - Multiple",
        "Mission Types": "Courier, Data, Trade",
        "Suggested Actions": "Complete loops, check for wing trade opportunities, board flip if needed"
    }
]

class MissionTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Makhai Rep Grind Tracker (MRGT)")
        self.geometry("900x500")
        self.configure(bg="#1e1e2f")
        self.style = ttk.Style(self)
        self.set_theme()
        self.config = load_config()
        self.create_widgets()
        self.fetch_inara_data()

    def set_theme(self):
        self.style.theme_use("clam")
        self.style.configure("Treeview",
                             background="#1e1e2f",
                             foreground="white",
                             rowheight=25,
                             fieldbackground="#1e1e2f",
                             font=("Segoe UI", 10))
        self.style.map("Treeview", background=[('selected', '#4682b4')])
        self.style.configure("Treeview.Heading",
                             font=("Segoe UI", 10, "bold"),
                             background="#4682b4",
                             foreground="white")
        self.style.configure("TButton",
                             font=("Segoe UI", 10),
                             padding=6,
                             background="#4682b4",
                             foreground="white")
        self.style.configure("TLabel",
                             background="#1e1e2f",
                             foreground="white",
                             font=("Segoe UI", 10))

    def create_widgets(self):
        self.tree_frame = ttk.Frame(self)
        self.tree_frame.pack(padx=10, pady=10, expand=True, fill='both')

        columns = ("Station", "System", "Factions", "Mission Types", "Suggested Actions")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings')

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140 if col != "Suggested Actions" else 340)

        for station in stations:
            self.tree.insert("", tk.END, values=(
                station["Station"],
                station["System"],
                station["Factions"],
                station["Mission Types"],
                station["Suggested Actions"]
            ))

        self.tree.pack(expand=True, fill='both')

        self.status_label = ttk.Label(self, text="Fetching data...")
        self.status_label.pack(pady=5)

        self.refresh_button = ttk.Button(self, text="Refresh Live Data", command=self.fetch_inara_data)
        self.refresh_button.pack(pady=5)

        quit_button = ttk.Button(self, text="Exit", command=self.quit)
        quit_button.pack(pady=5)

    def fetch_inara_data(self):
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config['INARA_API_KEY']}"
            }
            payload = {
                "header": {
                    "appName": "MRGT",
                    "appVersion": "1.0",
                    "isDeveloped": True,
                    "APIkey": self.config['INARA_API_KEY'],
                    "commanderName": self.config['INARA_CMDR_NAME']
                },
                "events": [{"eventName": "getCommanderProfile"}]
            }
            response = requests.post("https://inara.cz/inapi/v1/", headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                cmdr_data = data.get("events", [{}])[0].get("eventData", {})
                current_station = cmdr_data.get("preferredGameRole", "Unknown Station")
                current_system = cmdr_data.get("preferredAllegiance", "Unknown System")
                status = f"Station: {current_station} | System: {current_system}"
                if "kaine" in current_system.lower():
                    status += " | Faction: Kaine Detected ✅"
                self.status_label.config(text=status)
                self.fetch_eddb_data(current_system)
            else:
                self.status_label.config(text="Failed to fetch Inara data.")
        except Exception as e:
            self.status_label.config(text=f"Error accessing Inara API: {e}")

    def fetch_eddb_data(self, system_name):
        try:
            eddb_url = "https://eddb.io/archive/v6/systems_populated.json"
            eddb_response = requests.get(eddb_url)
            if eddb_response.status_code == 200:
                systems_data = eddb_response.json()
                for system in systems_data:
                    if system.get("name", "").lower() == system_name.lower():
                        eddb_info = f" | Population: {system.get('population', 'N/A')} | Allegiance: {system.get('allegiance', 'N/A')} | Government: {system.get('government', 'N/A')}"
                        self.status_label.config(text=self.status_label.cget("text") + eddb_info)
                        break
        except Exception as e:
            print("Error accessing EDDB API:", e)

if __name__ == '__main__':
    check_for_updates()
    ensure_config()
    app = MissionTrackerApp()
    app.mainloop()
