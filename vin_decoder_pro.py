import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import re
import csv
import os
import json
from datetime import datetime

# ======== MODULE-LEVEL CONFIGURATION ========
HISTORY_FILE = "vin_history.csv"
HISTORY_JSON = "vin_history.json"

# ======== LIGHT BLUE THEME CONFIGURATION ========
class Theme:
    BG_MAIN = "#f0f7ff"
    BG_CARD = "#ffffff"
    BG_INPUT = "#e8f4fd"
    BG_SIDEBAR = "#e1f0fa"
    BG_HOVER = "#d0e8f7"
    BG_SELECTED = "#b8ddf5"
    PRIMARY = "#1976d2"
    PRIMARY_DARK = "#1565c0"
    PRIMARY_LIGHT = "#42a5f5"
    ACCENT = "#2196f3"
    TEXT_DARK = "#1a237e"
    TEXT_PRIMARY = "#263238"
    TEXT_SECONDARY = "#546e7a"
    TEXT_MUTED = "#78909c"
    TEXT_ON_PRIMARY = "#ffffff"
    SUCCESS = "#2e7d32"
    WARNING = "#ed6c02"
    DANGER = "#d32f2f"
    INFO = "#0288d1"
    BORDER = "#bbdefb"
    BORDER_FOCUS = "#1976d2"
    DIVIDER = "#e3f2fd"


class CopyButton(tk.Button):
    def __init__(self, master, text_to_copy, **kwargs):
        self.text_to_copy = str(text_to_copy)
        super().__init__(master, text="📋", command=self._copy,
                        bg=Theme.BG_CARD, fg=Theme.PRIMARY,
                        font=("Segoe UI", 9), relief=tk.FLAT,
                        cursor="hand2", padx=4, pady=0,
                        activebackground=Theme.BG_HOVER,
                        activeforeground=Theme.PRIMARY_DARK,
                        **kwargs)
        self.bind("<Enter>", lambda e: self.config(bg=Theme.BG_HOVER))
        self.bind("<Leave>", lambda e: self.config(bg=Theme.BG_CARD))

    def _copy(self):
        self.clipboard_clear()
        self.clipboard_append(self.text_to_copy)
        self.config(text="✓", fg=Theme.SUCCESS)
        self.after(1500, lambda: self.config(text="📋", fg=Theme.PRIMARY))


class ModernEntry(tk.Entry):
    def __init__(self, master, **kwargs):
        defaults = {
            'font': ("Segoe UI", 13),
            'bg': Theme.BG_INPUT,
            'fg': Theme.TEXT_PRIMARY,
            'insertbackground': Theme.PRIMARY,
            'relief': tk.FLAT,
            'highlightthickness': 2,
            'highlightcolor': Theme.PRIMARY,
            'highlightbackground': Theme.BORDER,
            'selectbackground': Theme.PRIMARY_LIGHT,
            'selectforeground': Theme.TEXT_ON_PRIMARY,
        }
        defaults.update(kwargs)
        super().__init__(master, **defaults)
        self.bind("<Button-3>", self._show_menu)
        self.bind("<Control-a>", self._select_all)
        self.bind("<Control-A>", self._select_all)

    def _show_menu(self, event):
        menu = tk.Menu(self, tearoff=0, bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
                      activebackground=Theme.PRIMARY, activeforeground=Theme.TEXT_ON_PRIMARY,
                      font=("Segoe UI", 10))
        menu.add_command(label="Cut", command=lambda: self.event_generate("<Control-x>"))
        menu.add_command(label="Copy", command=lambda: self.event_generate("<Control-c>"))
        menu.add_command(label="Paste", command=lambda: self.event_generate("<Control-v>"))
        menu.add_separator()
        menu.add_command(label="Select All", command=self._select_all)
        menu.post(event.x_root, event.y_root)

    def _select_all(self, event=None):
        self.select_range(0, tk.END)
        self.icursor(tk.END)
        return "break"


class VINDecoderPro:
    def __init__(self, root):
        self.root = root
        self.root.title("VIN Decoder Pro - Light Edition")
        self.root.geometry("1200x850")
        self.root.configure(bg=Theme.BG_MAIN)
        self.root.minsize(950, 650)

        self.history = self._load_history()
        self.build_ui()
        self._refresh_history_list()

    def build_ui(self):
        # TOP HEADER BAR
        header_bar = tk.Frame(self.root, bg=Theme.PRIMARY, height=60)
        header_bar.pack(fill=tk.X)
        header_bar.pack_propagate(False)

        tk.Label(header_bar, text="VIN DECODER PRO", bg=Theme.PRIMARY, fg=Theme.TEXT_ON_PRIMARY,
                font=("Segoe UI", 18, "bold")).pack(side=tk.LEFT, padx=25, pady=10)

        tk.Label(header_bar, text="Professional Vehicle Identification System",
                bg=Theme.PRIMARY, fg="#bbdefb", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=10, pady=10)

        # MAIN PANED WINDOW
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=Theme.BORDER, sashwidth=5, sashrelief=tk.FLAT)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # LEFT SIDEBAR
        sidebar = tk.Frame(main_paned, bg=Theme.BG_SIDEBAR, width=300)
        main_paned.add(sidebar, minsize=260)

        title_frame = tk.Frame(sidebar, bg=Theme.PRIMARY, height=45)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="SEARCH HISTORY", bg=Theme.PRIMARY, fg=Theme.TEXT_ON_PRIMARY,
                font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=15, pady=8)

        tk.Label(sidebar, text="Double-click to reload a VIN\nRight-click for more options",
                bg=Theme.BG_SIDEBAR, fg=Theme.TEXT_MUTED, font=("Segoe UI", 9),
                justify=tk.LEFT).pack(anchor=tk.W, padx=15, pady=(10, 5))

        list_container = tk.Frame(sidebar, bg=Theme.BG_SIDEBAR, padx=10, pady=5)
        list_container.pack(fill=tk.BOTH, expand=True)

        self.history_listbox = tk.Listbox(list_container, bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
                                         selectbackground=Theme.PRIMARY, selectforeground=Theme.TEXT_ON_PRIMARY,
                                         font=("Consolas", 10), relief=tk.FLAT, highlightthickness=0,
                                         activestyle="none", height=25, bd=0)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.history_listbox.bind("<Double-Button-1>", self._on_history_double_click)
        self.history_listbox.bind("<Button-3>", self._on_history_right_click)

        hist_scroll = tk.Scrollbar(list_container, orient="vertical", command=self.history_listbox.yview,
                                  bg=Theme.BG_SIDEBAR, troughcolor=Theme.BG_SIDEBAR,
                                  activebackground=Theme.PRIMARY, relief=tk.FLAT)
        hist_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_listbox.config(yscrollcommand=hist_scroll.set)

        btn_frame = tk.Frame(sidebar, bg=Theme.BG_SIDEBAR, padx=10, pady=10)
        btn_frame.pack(fill=tk.X)

        self._create_action_btn(btn_frame, "Export CSV", self._export_csv, Theme.PRIMARY)
        self._create_action_btn(btn_frame, "Clear All", self._clear_history, Theme.DANGER)

        self.stats_var = tk.StringVar(value="0 searches in history")
        tk.Label(sidebar, textvariable=self.stats_var, bg=Theme.BG_SIDEBAR, fg=Theme.TEXT_MUTED,
                font=("Segoe UI", 9, "italic")).pack(anchor=tk.W, padx=15, pady=(5, 15))

        # RIGHT CONTENT AREA
        right = tk.Frame(main_paned, bg=Theme.BG_MAIN)
        main_paned.add(right, minsize=650)

        # Input section
        input_card = tk.Frame(right, bg=Theme.BG_CARD, padx=25, pady=25,
                             highlightbackground=Theme.BORDER, highlightthickness=1)
        input_card.pack(fill=tk.X, pady=(0, 15))

        tk.Label(input_card, text="ENTER VEHICLE IDENTIFICATION NUMBER",
                bg=Theme.BG_CARD, fg=Theme.PRIMARY, font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)

        tk.Label(input_card, text="Type or paste a 17-character VIN to decode full vehicle specifications",
                bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED, font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(2, 0))

        input_row = tk.Frame(input_card, bg=Theme.BG_CARD)
        input_row.pack(fill=tk.X, pady=(15, 0))

        self.vin_entry = ModernEntry(input_row, width=30)
        self.vin_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=12, padx=(0, 12))
        self.vin_entry.bind('<Return>', lambda e: self.decode_vin())

        self.decode_btn = tk.Button(input_row, text="DECODE VIN", command=self.decode_vin,
                                    bg=Theme.PRIMARY, fg=Theme.TEXT_ON_PRIMARY,
                                    font=("Segoe UI", 12, "bold"), relief=tk.FLAT,
                                    padx=30, pady=12, cursor="hand2",
                                    activebackground=Theme.PRIMARY_DARK,
                                    activeforeground=Theme.TEXT_ON_PRIMARY)
        self.decode_btn.pack(side=tk.RIGHT)

        paste_btn = tk.Button(input_row, text="Paste", command=self._paste_vin,
                             bg=Theme.BG_INPUT, fg=Theme.PRIMARY, font=("Segoe UI", 12),
                             relief=tk.FLAT, padx=10, pady=12, cursor="hand2",
                             activebackground=Theme.BG_HOVER)
        paste_btn.pack(side=tk.RIGHT, padx=(0, 8))

        # Status bar
        status_frame = tk.Frame(right, bg=Theme.BG_MAIN, height=30)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        status_frame.pack_propagate(False)

        self.status_var = tk.StringVar(value="Ready - Enter a 17-character VIN number")
        self.status_label = tk.Label(status_frame, textvariable=self.status_var,
                                    bg=Theme.BG_MAIN, fg=Theme.TEXT_MUTED,
                                    font=("Segoe UI", 9), anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=5)

        # NOTEBOOK TABS
        self.notebook = ttk.Notebook(right)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background=Theme.BG_MAIN, tabmargins=[2, 5, 2, 0])
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[15, 8],
                       background=Theme.BG_SIDEBAR, foreground=Theme.TEXT_SECONDARY)
        style.map("TNotebook.Tab",
                 background=[("selected", Theme.PRIMARY)],
                 foreground=[("selected", Theme.TEXT_ON_PRIMARY)],
                 expand=[("selected", [1, 1, 1, 0])])

        # Results tab
        self.results_tab = tk.Frame(self.notebook, bg=Theme.BG_MAIN)
        self.notebook.add(self.results_tab, text="  Results  ")

        self.canvas = tk.Canvas(self.results_tab, bg=Theme.BG_MAIN, highlightthickness=0)
        vscroll = tk.Scrollbar(self.results_tab, orient="vertical", command=self.canvas.yview,
                              bg=Theme.BG_SIDEBAR, troughcolor=Theme.BG_MAIN,
                              activebackground=Theme.PRIMARY, relief=tk.FLAT)
        self.scrollable_frame = tk.Frame(self.canvas, bg=Theme.BG_MAIN)

        self.scrollable_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=vscroll.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # Raw Data tab
        self.raw_tab = tk.Frame(self.notebook, bg=Theme.BG_MAIN)
        self.notebook.add(self.raw_tab, text="  Raw JSON  ")

        raw_container = tk.Frame(self.raw_tab, bg=Theme.BG_CARD, padx=2, pady=2,
                                highlightbackground=Theme.BORDER, highlightthickness=1)
        raw_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.raw_text = tk.Text(raw_container, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                               font=("Consolas", 10), relief=tk.FLAT, wrap=tk.WORD,
                               insertbackground=Theme.PRIMARY, padx=15, pady=15,
                               selectbackground=Theme.PRIMARY_LIGHT,
                               selectforeground=Theme.TEXT_ON_PRIMARY)
        raw_scroll = tk.Scrollbar(raw_container, orient="vertical", command=self.raw_text.yview,
                                 bg=Theme.BG_SIDEBAR, troughcolor=Theme.BG_CARD,
                                 activebackground=Theme.PRIMARY, relief=tk.FLAT)
        self.raw_text.config(yscrollcommand=raw_scroll.set)
        self.raw_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        raw_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        raw_toolbar = tk.Frame(self.raw_tab, bg=Theme.BG_MAIN, height=35)
        raw_toolbar.pack(fill=tk.X, before=raw_container)
        raw_toolbar.pack_propagate(False)

        tk.Button(raw_toolbar, text="Copy All", command=self._copy_raw,
                 bg=Theme.BG_CARD, fg=Theme.PRIMARY, font=("Segoe UI", 9),
                 relief=tk.FLAT, padx=15, pady=4, cursor="hand2",
                 activebackground=Theme.BG_HOVER).pack(side=tk.LEFT, padx=5, pady=4)

        tk.Button(raw_toolbar, text="Save JSON", command=self._save_raw_json,
                 bg=Theme.BG_CARD, fg=Theme.PRIMARY, font=("Segoe UI", 9),
                 relief=tk.FLAT, padx=15, pady=4, cursor="hand2",
                 activebackground=Theme.BG_HOVER).pack(side=tk.LEFT, padx=5, pady=4)

        # Copyright footer
        footer = tk.Frame(right, bg=Theme.BG_MAIN, height=30)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        tk.Label(footer, text="2026 3bHussein | ECU Tuning Solutions | Powered by NHTSA VPIC",
                bg=Theme.BG_MAIN, fg=Theme.TEXT_MUTED, font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=10)

    def _create_action_btn(self, parent, text, command, color):
        btn = tk.Button(parent, text=text, command=command, bg=color, fg=Theme.TEXT_ON_PRIMARY,
                       font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=15, pady=8,
                       cursor="hand2", activebackground=Theme.PRIMARY_DARK if color == Theme.PRIMARY else "#b71c1c")
        btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4, pady=4)
        return btn

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width - 20)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _paste_vin(self):
        try:
            clipboard = self.root.clipboard_get().strip().upper()
            clipboard = re.sub(r'[^A-HJ-NPR-Z0-9]', '', clipboard)[:17]
            self.vin_entry.delete(0, tk.END)
            self.vin_entry.insert(0, clipboard)
        except:
            pass

    def clear_results(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.raw_text.delete("1.0", tk.END)

    def create_card(self, parent, title, items, icon=""):
        card = tk.Frame(parent, bg=Theme.BG_CARD, padx=20, pady=20)
        card.pack(fill=tk.X, pady=(0, 12), padx=8)
        card.configure(highlightbackground=Theme.BORDER, highlightthickness=1)

        accent = tk.Frame(card, bg=Theme.PRIMARY, height=4)
        accent.pack(fill=tk.X, pady=(0, 15))

        header = tk.Frame(card, bg=Theme.BG_CARD)
        header.pack(fill=tk.X, pady=(0, 15))

        tk.Label(header, text=f"{icon}  {title}", bg=Theme.BG_CARD, fg=Theme.TEXT_DARK,
                font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)

        copy_all_btn = tk.Button(header, text="Copy All", command=lambda: self._copy_card_items(items),
                                bg=Theme.BG_CARD, fg=Theme.PRIMARY, font=("Segoe UI", 9),
                                relief=tk.FLAT, padx=10, pady=2, cursor="hand2",
                                activebackground=Theme.BG_HOVER)
        copy_all_btn.pack(side=tk.RIGHT)

        for key, value in items:
            if value and str(value).strip() and str(value).lower() not in ['not applicable', 'n/a', '', 'none', 'null']:
                row = tk.Frame(card, bg=Theme.BG_CARD)
                row.pack(fill=tk.X, pady=4)

                tk.Label(row, text=f"{key}", bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
                        font=("Segoe UI", 10), width=26, anchor=tk.W).pack(side=tk.LEFT)

                val_frame = tk.Frame(row, bg=Theme.BG_CARD)
                val_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

                val_label = tk.Label(val_frame, text=str(value), bg=Theme.BG_CARD,
                                    fg=Theme.TEXT_PRIMARY, font=("Segoe UI", 10, "bold"),
                                    wraplength=400, anchor=tk.W, justify=tk.LEFT)
                val_label.pack(side=tk.LEFT)

                CopyButton(val_frame, str(value)).pack(side=tk.RIGHT, padx=(8, 0))

        return card

    def _copy_card_items(self, items):
        text = ""
        for key, value in items:
            if value and str(value).strip() and str(value).lower() not in ['not applicable', 'n/a', '', 'none', 'null']:
                text += f"{key}: {value}\n"
        self.root.clipboard_clear()
        self.root.clipboard_append(text.strip())
        messagebox.showinfo("Copied", "All values from this section copied to clipboard!")

    def _copy_raw(self):
        text = self.raw_text.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", "Raw JSON data copied to clipboard!")

    def _save_raw_json(self):
        text = self.raw_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Empty", "No raw data to save")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"vin_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            messagebox.showinfo("Saved", f"JSON saved to:\n{filepath}")

    def validate_vin(self, vin):
        vin = vin.strip().upper()
        if len(vin) != 17:
            return False, "VIN must be exactly 17 characters long"
        if not re.match(r'^[A-HJ-NPR-Z0-9]+$', vin):
            return False, "VIN contains invalid characters (letters I, O, Q are not allowed)"
        return True, vin

    def decode_vin(self):
        vin = self.vin_entry.get().strip().upper()

        valid, result = self.validate_vin(vin)
        if not valid:
            messagebox.showerror("Invalid VIN", result)
            self.status_var.set(f"Error: {result}")
            self.status_label.config(fg=Theme.DANGER)
            return

        vin = result
        self.status_var.set(f"Decoding VIN: {vin}...")
        self.status_label.config(fg=Theme.WARNING)
        self.root.update()

        try:
            url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
            response = requests.get(url, timeout=15)
            data = response.json()

            if data.get('Results'):
                self.display_results(data['Results'], vin)
                self._save_to_history(vin, data['Results'])
                self.status_var.set(f"Decoded: {vin}  |  {datetime.now().strftime('%H:%M:%S')}")
                self.status_label.config(fg=Theme.SUCCESS)
            else:
                messagebox.showwarning("No Data", "No data found for this VIN in the NHTSA database")
                self.status_var.set("No data found for this VIN")
                self.status_label.config(fg=Theme.WARNING)

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Connection Error",
                f"Failed to connect to NHTSA database:\n{str(e)}\n\nPlease check your internet connection.")
            self.status_var.set("Connection failed - Check internet")
            self.status_label.config(fg=Theme.DANGER)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            self.status_var.set(f"Error: {str(e)[:50]}")
            self.status_label.config(fg=Theme.DANGER)

    def display_results(self, results, vin):
        self.clear_results()

        variables = {}
        for item in results:
            var = item.get('Variable', '')
            val = item.get('Value', '')
            if var:
                variables[var] = val

        # Raw JSON
        self.raw_text.insert("1.0", json.dumps(results, indent=2))

        # QUICK SUMMARY
        summary_items = [
            ("VIN", vin),
            ("Vehicle", f"{variables.get('Model Year', 'N/A')} {variables.get('Make', 'N/A')} {variables.get('Model', 'N/A')}"),
            ("Trim", variables.get('Trim', 'N/A')),
            ("Engine", f"{variables.get('Engine Model', 'N/A')} {variables.get('Displacement (L)', 'N/A')}L {variables.get('Engine Number of Cylinders', 'N/A')}cyl"),
            ("Fuel", variables.get('Fuel Type - Primary', variables.get('Fuel Type', 'N/A'))),
            ("Transmission", f"{variables.get('Transmission Style', 'N/A')} {variables.get('Transmission Speeds', 'N/A')}spd"),
            ("Drive", variables.get('Drive Type', 'N/A')),
            ("Body", variables.get('Body Class', 'N/A')),
        ]
        self.create_card(self.scrollable_frame, "QUICK SUMMARY", summary_items, "")

        # VEHICLE IDENTITY
        identity_items = [
            ("VIN", vin),
            ("Make", variables.get('Make', 'N/A')),
            ("Model", variables.get('Model', 'N/A')),
            ("Model Year", variables.get('Model Year', 'N/A')),
            ("Trim", variables.get('Trim', 'N/A')),
            ("Vehicle Type", variables.get('Vehicle Type', 'N/A')),
            ("Body Class", variables.get('Body Class', 'N/A')),
            ("Series", variables.get('Series', 'N/A')),
            ("Plant City", variables.get('Plant City', 'N/A')),
            ("Plant Country", variables.get('Plant Country', 'N/A')),
            ("Manufacturer", variables.get('Manufacturer Name', 'N/A')),
            ("Destination Market", variables.get('Destination Market', 'N/A')),
        ]
        self.create_card(self.scrollable_frame, "VEHICLE IDENTITY", identity_items, "")

        # ENGINE SPECIFICATIONS
        engine_items = [
            ("Engine Model", variables.get('Engine Model', 'N/A')),
            ("Engine Cylinders", variables.get('Engine Number of Cylinders', 'N/A')),
            ("Displacement (L)", variables.get('Displacement (L)', 'N/A')),
            ("Displacement (CC)", variables.get('Displacement (CC)', 'N/A')),
            ("Engine Power (kW)", variables.get('Engine Power (kW)', 'N/A')),
            ("Engine Power (HP)", self._calc_hp(variables.get('Engine Power (kW)', ''))),
            ("Fuel Type", variables.get('Fuel Type - Primary', variables.get('Fuel Type', 'N/A'))),
            ("Engine Configuration", variables.get('Engine Configuration', 'N/A')),
            ("Engine Brake (HP)", variables.get('Engine Brake (HP)', 'N/A')),
            ("Engine Stroke Cycles", variables.get('Engine Stroke Cycles', 'N/A')),
            ("Valve Train Design", variables.get('Valve Train Design', 'N/A')),
            ("Engine Compression Ratio", variables.get('Engine Compression Ratio', 'N/A')),
            ("Cooling Type", variables.get('Cooling Type', 'N/A')),
            ("Electrification Level", variables.get('Electrification Level', 'N/A')),
            ("Other Engine Info", variables.get('Other Engine Info', 'N/A')),
        ]
        self.create_card(self.scrollable_frame, "ENGINE SPECIFICATIONS", engine_items, "")

        # TRANSMISSION
        trans_items = [
            ("Transmission Style", variables.get('Transmission Style', 'N/A')),
            ("Transmission Speeds", variables.get('Transmission Speeds', 'N/A')),
            ("Drive Type", variables.get('Drive Type', 'N/A')),
            ("Axle Configuration", variables.get('Axle Configuration', 'N/A')),
            ("Axles", variables.get('Axles', 'N/A')),
            ("Wheel Base (mm)", variables.get('Wheel Base (mm)', 'N/A')),
            ("Wheel Base (inches)", variables.get('Wheel Base (inches)', 'N/A')),
        ]
        self.create_card(self.scrollable_frame, "TRANSMISSION & DRIVETRAIN", trans_items, "")

        # SAFETY
        safety_items = [
            ("ABS", variables.get('ABS', 'N/A')),
            ("ESC", variables.get('ESC', 'N/A')),
            ("Traction Control", variables.get('Traction Control', 'N/A')),
            ("TPMS", variables.get('TPMS', 'N/A')),
            ("Air Bag Curtain", variables.get('Air Bag Loc Curtain', 'N/A')),
            ("Air Bag Front", variables.get('Air Bag Loc Front', 'N/A')),
            ("Air Bag Knee", variables.get('Air Bag Loc Knee', 'N/A')),
            ("Air Bag Side", variables.get('Air Bag Loc Side', 'N/A')),
            ("Blind Spot Monitor", variables.get('Blind Spot Monitor', 'N/A')),
            ("Lane Departure Warning", variables.get('Lane Departure Warning', 'N/A')),
            ("Lane Keep System", variables.get('Lane Keep System', 'N/A')),
            ("Forward Collision Warning", variables.get('Forward Collision Warning', 'N/A')),
            ("Adaptive Cruise Control", variables.get('Adaptive Cruise Control', 'N/A')),
            ("Rear Cross Traffic Alert", variables.get('Rear Cross Traffic Alert', 'N/A')),
            ("Keyless Ignition", variables.get('Keyless Ignition', 'N/A')),
            ("Daytime Running Light", variables.get('Daytime Running Light', 'N/A')),
        ]
        self.create_card(self.scrollable_frame, "SAFETY & TECHNOLOGY", safety_items, "")

        # DIMENSIONS
        dim_items = [
            ("GVWR", variables.get('Gross Vehicle Weight Rating', 'N/A')),
            ("GCWR", variables.get('Gross Combination Weight Rating', 'N/A')),
            ("GVWR From", variables.get('Gross Vehicle Weight Rating From', 'N/A')),
            ("GVWR To", variables.get('Gross Vehicle Weight Rating To', 'N/A')),
            ("Bed Length (inches)", variables.get('Bed Length (inches)', 'N/A')),
            ("Bed Type", variables.get('Bed Type', 'N/A')),
            ("Cab Type", variables.get('Cab Type', 'N/A')),
            ("Doors", variables.get('Doors', 'N/A')),
            ("Windows", variables.get('Windows', 'N/A')),
            ("Seat Rows", variables.get('Seat Rows', 'N/A')),
            ("Total Seat Rows", variables.get('Total Seat Rows', 'N/A')),
            ("Seats", variables.get('Seats', 'N/A')),
        ]
        self.create_card(self.scrollable_frame, "DIMENSIONS & CAPACITY", dim_items, "")

        # MANUFACTURER
        mfr_items = [
            ("Manufacturer", variables.get('Manufacturer Name', 'N/A')),
            ("Manufacturer Address", variables.get('Manufacturer Address', 'N/A')),
            ("Manufacturer City", variables.get('Manufacturer City', 'N/A')),
            ("Manufacturer State", variables.get('Manufacturer State', 'N/A')),
            ("Manufacturer Country", variables.get('Manufacturer Country', 'N/A')),
            ("Manufacturer Type", variables.get('Manufacturer Type', 'N/A')),
            ("NCSA Body Type", variables.get('NCSA Body Type', 'N/A')),
            ("NCSA Make", variables.get('NCSA Make', 'N/A')),
            ("NCSA Model", variables.get('NCSA Model', 'N/A')),
            ("Pretensioner", variables.get('Pretensioner', 'N/A')),
            ("Seat Belts All", variables.get('Seat Belts All', 'N/A')),
            ("Seat Belts Type", variables.get('Seat Belts Type', 'N/A')),
        ]
        self.create_card(self.scrollable_frame, "MANUFACTURER DETAILS", mfr_items, "")

        # ADDITIONAL
        additional_items = [
            ("Vehicle Descriptor", variables.get('Vehicle Descriptor', 'N/A')),
            ("Error Code", variables.get('Error Code', 'N/A')),
            ("Error Text", variables.get('Error Text', 'N/A')),
            ("Possible Values", variables.get('Possible Values', 'N/A')),
            ("Suggested VIN", variables.get('Suggested VIN', 'N/A')),
            ("Trim2", variables.get('Trim2', 'N/A')),
            ("Note", variables.get('Note', 'N/A')),
        ]
        self.create_card(self.scrollable_frame, "ADDITIONAL INFORMATION", additional_items, "")

        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(0)

        if self.canvas_window:
            self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width()-25)

    def _calc_hp(self, kw_str):
        try:
            kw = float(kw_str)
            hp = round(kw * 1.34162, 1)
            return f"{hp} HP"
        except:
            return "N/A"

    # ===== HISTORY MANAGEMENT =====
    def _load_history(self):
        history = []
        if os.path.exists(HISTORY_JSON):
            try:
                with open(HISTORY_JSON, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                history = []
        return history

    def _save_history(self):
        with open(HISTORY_JSON, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2)
        self._refresh_history_list()

    def _save_to_history(self, vin, results):
        variables = {}
        for item in results:
            var = item.get('Variable', '')
            val = item.get('Value', '')
            if var and val:
                variables[var] = val

        entry = {
            "timestamp": datetime.now().isoformat(),
            "vin": vin,
            "make": variables.get('Make', 'N/A'),
            "model": variables.get('Model', 'N/A'),
            "year": variables.get('Model Year', 'N/A'),
            "trim": variables.get('Trim', 'N/A'),
            "engine": variables.get('Engine Model', 'N/A'),
            "displacement": variables.get('Displacement (L)', 'N/A'),
            "fuel": variables.get('Fuel Type - Primary', variables.get('Fuel Type', 'N/A')),
            "transmission": variables.get('Transmission Style', 'N/A'),
            "drive": variables.get('Drive Type', 'N/A'),
            "body": variables.get('Body Class', 'N/A'),
            "plant": variables.get('Plant Country', 'N/A'),
        }

        self.history = [h for h in self.history if h['vin'] != vin]
        self.history.insert(0, entry)
        self.history = self.history[:100]
        self._save_history()

    def _refresh_history_list(self):
        self.history_listbox.delete(0, tk.END)
        for entry in self.history:
            display = f"{entry['vin']} | {entry['year']} {entry['make']} {entry['model']}"
            self.history_listbox.insert(tk.END, display)
        self.stats_var.set(f"{len(self.history)} searches in history")

    def _on_history_double_click(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            idx = selection[0]
            vin = self.history[idx]['vin']
            self.vin_entry.delete(0, tk.END)
            self.vin_entry.insert(0, vin)
            self.decode_vin()

    def _on_history_right_click(self, event):
        selection = self.history_listbox.curselection()
        if not selection:
            return
        idx = selection[0]

        menu = tk.Menu(self.root, tearoff=0, bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
                      activebackground=Theme.PRIMARY, activeforeground=Theme.TEXT_ON_PRIMARY,
                      font=("Segoe UI", 10))
        menu.add_command(label="Load & Decode", command=lambda: self._on_history_double_click(None))
        menu.add_command(label="Copy VIN", command=lambda: self._copy_vin_from_history(idx))
        menu.add_separator()
        menu.add_command(label="Delete Entry", command=lambda: self._delete_history_entry(idx))
        menu.post(event.x_root, event.y_root)

    def _copy_vin_from_history(self, idx):
        vin = self.history[idx]['vin']
        self.root.clipboard_clear()
        self.root.clipboard_append(vin)

    def _delete_history_entry(self, idx):
        del self.history[idx]
        self._save_history()

    def _export_csv(self):
        if not self.history:
            messagebox.showinfo("Export", "No history to export")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"vin_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        if not filepath:
            return

        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                if self.history:
                    writer = csv.DictWriter(f, fieldnames=self.history[0].keys())
                    writer.writeheader()
                    writer.writerows(self.history)
            messagebox.showinfo("Export Complete", f"History exported to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export:\n{str(e)}")

    def _clear_history(self):
        if not self.history:
            return
        if messagebox.askyesno("Clear History", "Are you sure you want to delete all search history?"):
            self.history = []
            self._save_history()
            if os.path.exists(HISTORY_JSON):
                os.remove(HISTORY_JSON)
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)


def main():
    root = tk.Tk()
    app = VINDecoderPro(root)
    root.mainloop()

if __name__ == "__main__":
    main()
