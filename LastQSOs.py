import sqlite3
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk


class LastQSOs(ttk.Frame):

    COLUMNS = ("rowid", "Call", "Name", "Date", "Time", "Band", "Freq", "Mode", "Report", "Grid", "State", "Country")

    def __init__(self, master, conn, on_pick=None):
        super().__init__(master, padding=8)
        self.conn = conn
        self.on_pick = on_pick
        self.font = tkfont.nametofont("TkDefaultFont")
        self.limit_var = tk.IntVar(value=10)
        self._build_ui()
        self.refresh()
        #self._schedule_autorefresh()

    def colw(self, chars): return self.font.measure("0" * chars) + 16 # padding for treeview

    def _build_ui(self):
        # Controls row
        controls = ttk.Frame(self)
        controls.pack(fill="x", pady=(0, 8))

        ttk.Label(controls, text="Show last:").pack(side="left")
        self.combo = ttk.Combobox(
            controls, width=5, state="readonly",
            values=(5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000),
            textvariable=self.limit_var
        )
        self.combo.pack(side="left", padx=(6, 12))
        self.combo.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        self.refresh_btn = ttk.Button(controls, text="Refresh", command=self.refresh)
        self.refresh_btn.pack(side="left")

        # Treeview + scrollbar
        self.tree = ttk.Treeview(
            self,
            columns=self.COLUMNS,
            show="headings",
            height=12
        )
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        # Column headings and widths , Name, Date, Time, FreqBand, Mode, Report, Grid, State, Country
        headings = {
            "rowid": "QSO",
            "Call": "Call",
            "Name": "Name",
            "Date": "Date",
            "Time": "Time",
            "Band": "Band",
            "Freq": "Freq",
            "Mode": "Mode",
            "Report": "Report",
            "Grid": "Grid",
            "State": "State",
            "Country": "Country",
        }
        widths = {
            "rowid": self.colw(7),
            "Call": self.colw(9),
            "Name": self.colw(15),
            "Date": self.colw(9),
            "Time": self.colw(5),
            "Band": self.colw(5),
            "Freq": self.colw(7),
            "Mode": self.colw(5),
            "Report": self.colw(6),
            "Grid": self.colw(7),
            "State": self.colw(6),
            "Country": self.colw(15),
        }
        for col in self.COLUMNS:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def fetch_last_qsos(self, limit=10):
        # If datetime_utc is ISO-8601 text, simple ORDER BY works correctly.
        sql = """
            SELECT rowid, Call, Name, Date, Time, Band, Freq, Mode, Report, Grid, State, Country
            FROM logbook
            ORDER BY Date DESC
            LIMIT ?
        """
        return self.conn.execute(sql, (limit,)).fetchall()

    def fetch_qsos_by_call(self, call, limit=10):
        # If datetime_utc is ISO-8601 text, simple ORDER BY works correctly.
        sql = """
            SELECT rowid, Call, Name, Date, Time, Band, Freq, Mode, Report, Grid, State, Country
            FROM logbook
            WHERE Call=?
            ORDER BY Date DESC
            LIMIT ?
        """
        return self.conn.execute(sql, (call,limit,)).fetchall()

    def _on_select(self, event=None):
        # Call the callback with the rowid of what we just selected
        sel = self.tree.selection()
        if not sel:
            return
        qso_id = int(self.tree.set(sel[0], "rowid"))
        if self.on_pick:
            self.on_pick(qso_id)

    def refresh(self):
        # Clear then repopulate with newest first
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        try:
            rows = self.fetch_last_qsos(self.limit_var.get())
        except sqlite3.Error as e:
            # Show a simple error row if DB is unavailable
            #self.tree.insert("", "end", values=("DB error:", str(e), "", "", "", ""))
            return

        for row in rows:
            self.tree.insert("", "end", values=row)

    def lookup(self, call):
        # Clear then repopulate with newest first
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        try:
            rows = self.fetch_qsos_by_call(call, self.limit_var.get())
        except sqlite3.Error as e:
            # Show a simple error row if DB is unavailable
            #self.tree.insert("", "end", values=("DB error:", str(e), "", "", "", ""))
            return

        for row in rows:
            self.tree.insert("", "end", values=row)

    def _schedule_autorefresh(self):
        # Light periodic refresh. Adjust interval (ms) as you like.
        self.after(5000, self._tick)

    def _tick(self):
        self.refresh()
        self._schedule_autorefresh()
