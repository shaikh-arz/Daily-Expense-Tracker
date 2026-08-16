import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime

# ── File to save expenses ──────────────────────────────────────────────────────
DATA_FILE = "expenses.json"

# ── Load / Save helpers ────────────────────────────────────────────────────────
def load_expenses():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_expenses(expenses):
    with open(DATA_FILE, "w") as f:
        json.dump(expenses, f, indent=2)

# ── Colours & fonts (simple palette) ──────────────────────────────────────────
BG        = "#1E1E2E"   # dark navy background
CARD      = "#2A2A3E"   # slightly lighter card
ACCENT    = "#7C3AED"   # violet accent
ACCENT2   = "#A78BFA"   # lighter violet
GREEN     = "#22C55E"
RED       = "#EF4444"
TEXT      = "#E2E8F0"
MUTED     = "#94A3B8"

FONT_H1   = ("Segoe UI", 22, "bold")
FONT_H2   = ("Segoe UI", 14, "bold")
FONT_BODY = ("Segoe UI", 11)
FONT_SM   = ("Segoe UI", 9)

CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Health",
              "Entertainment", "Education", "Other"]

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════
class ExpenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Expense Tracker")
        self.root.geometry("820x620")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.expenses = load_expenses()

        # Show the main / home screen first
        self.show_home_screen()

    # ── Screen switcher ────────────────────────────────────────────────────────
    def clear_screen(self):
        """Destroy every widget currently on screen."""
        for widget in self.root.winfo_children():
            widget.destroy()

    # ══════════════════════════════════════════════════════════════════════════
    # 1.  HOME / MAIN SCREEN
    # ══════════════════════════════════════════════════════════════════════════
    def show_home_screen(self):
        self.clear_screen()

        # ── Header bar ──────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=ACCENT, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="💰 Daily Expense Tracker",
                 font=FONT_H1, bg=ACCENT, fg="white").pack(side="left", padx=20, pady=15)

        today = datetime.now().strftime("%d %b %Y")
        tk.Label(header, text=today, font=FONT_BODY, bg=ACCENT, fg=ACCENT2
                 ).pack(side="right", padx=20)

        # ── Summary cards ───────────────────────────────────────────────────
        summary_frame = tk.Frame(self.root, bg=BG)
        summary_frame.pack(fill="x", padx=20, pady=16)

        total_today = sum(e["amount"] for e in self.expenses
                         if e["date"] == datetime.now().strftime("%Y-%m-%d"))
        total_all   = sum(e["amount"] for e in self.expenses)
        count_today = sum(1 for e in self.expenses
                         if e["date"] == datetime.now().strftime("%Y-%m-%d"))

        for label, value, colour in [
            ("Today's Total",   f"₹{total_today:,.2f}",    GREEN),
            ("All-time Total",  f"₹{total_all:,.2f}",      ACCENT2),
            ("Today's Entries", str(count_today),           "#FBBF24"),
        ]:
            card = tk.Frame(summary_frame, bg=CARD, bd=0, relief="flat")
            card.pack(side="left", expand=True, fill="x", padx=6, ipady=12)
            tk.Label(card, text=label,  font=FONT_SM,   bg=CARD, fg=MUTED ).pack()
            tk.Label(card, text=value,  font=("Segoe UI", 18, "bold"),
                     bg=CARD, fg=colour).pack()

        # ── Action buttons ──────────────────────────────────────────────────
        btn_frame = tk.Frame(self.root, bg=BG)
        btn_frame.pack(fill="x", padx=20, pady=4)

        self._btn(btn_frame, "➕  Add Expense",      self.show_add_screen,    ACCENT ).pack(side="left", padx=6)
        self._btn(btn_frame, "📋  View All",          self.show_list_screen,   "#0EA5E9").pack(side="left", padx=6)
        self._btn(btn_frame, "📊  Category Summary",  self.show_summary_screen,"#F59E0B").pack(side="left", padx=6)
        self._btn(btn_frame, "🗑  Clear All",          self.clear_all,          RED,
                  width=14).pack(side="right", padx=6)

        # ── Recent expenses table ───────────────────────────────────────────
        tk.Label(self.root, text="Recent Expenses", font=FONT_H2,
                 bg=BG, fg=TEXT).pack(anchor="w", padx=26, pady=(10,4))

        table_frame = tk.Frame(self.root, bg=BG)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0,16))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                         background=CARD, foreground=TEXT,
                         fieldbackground=CARD, rowheight=30,
                         font=FONT_BODY)
        style.configure("Custom.Treeview.Heading",
                         background=ACCENT, foreground="white",
                         font=("Segoe UI", 10, "bold"))
        style.map("Custom.Treeview", background=[("selected", ACCENT)])

        cols = ("Date", "Category", "Description", "Amount")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings",
                                  style="Custom.Treeview", height=10)
        for col, w in zip(cols, [110, 110, 280, 100]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center" if col != "Description" else "w")

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Fill with most-recent-first
        for exp in reversed(self.expenses[-50:]):
            self.tree.insert("", "end",
                             values=(exp["date"], exp["category"],
                                     exp["description"],
                                     f"₹{exp['amount']:,.2f}"))

    # ══════════════════════════════════════════════════════════════════════════
    # 2.  ADD EXPENSE SCREEN
    # ══════════════════════════════════════════════════════════════════════════
    def show_add_screen(self):
        self.clear_screen()

        # Header
        header = tk.Frame(self.root, bg=ACCENT, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="➕  Add New Expense", font=FONT_H1,
                 bg=ACCENT, fg="white").pack(side="left", padx=20, pady=10)
        self._btn(header, "← Back", self.show_home_screen, CARD, width=10
                  ).pack(side="right", padx=20, pady=12)

        # Form card
        form = tk.Frame(self.root, bg=CARD, bd=0)
        form.place(relx=0.5, rely=0.52, anchor="center", width=500)

        fields = {}

        def row(label_text, widget_fn, pady_top=14):
            tk.Label(form, text=label_text, font=FONT_BODY,
                     bg=CARD, fg=MUTED).pack(anchor="w", padx=30, pady=(pady_top,2))
            w = widget_fn()
            w.pack(fill="x", padx=30)
            return w

        # Amount
        fields["amount"] = row("Amount (₹) *",
            lambda: tk.Entry(form, font=("Segoe UI", 13), bg=BG, fg=TEXT,
                             insertbackground=TEXT, relief="flat",
                             highlightthickness=1, highlightcolor=ACCENT,
                             highlightbackground=MUTED))

        # Category
        cat_var = tk.StringVar(value=CATEGORIES[0])
        fields["category"] = row("Category *",
            lambda: ttk.Combobox(form, textvariable=cat_var,
                                  values=CATEGORIES, state="readonly",
                                  font=FONT_BODY))

        # Description
        fields["description"] = row("Description",
            lambda: tk.Entry(form, font=FONT_BODY, bg=BG, fg=TEXT,
                             insertbackground=TEXT, relief="flat",
                             highlightthickness=1, highlightcolor=ACCENT,
                             highlightbackground=MUTED))

        # Date
        date_entry = row("Date (YYYY-MM-DD) *",
            lambda: tk.Entry(form, font=FONT_BODY, bg=BG, fg=TEXT,
                             insertbackground=TEXT, relief="flat",
                             highlightthickness=1, highlightcolor=ACCENT,
                             highlightbackground=MUTED))
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        fields["date"] = date_entry

        # Error label
        err_lbl = tk.Label(form, text="", font=FONT_SM, bg=CARD, fg=RED)
        err_lbl.pack(pady=(10,0))

        def save():
            amt_raw = fields["amount"].get().strip()
            date_raw = fields["date"].get().strip()
            desc = fields["description"].get().strip()

            # Validation
            if not amt_raw:
                err_lbl.config(text="⚠  Amount is required.")
                return
            try:
                amt = float(amt_raw)
                if amt <= 0:
                    raise ValueError
            except ValueError:
                err_lbl.config(text="⚠  Enter a valid positive number.")
                return
            try:
                datetime.strptime(date_raw, "%Y-%m-%d")
            except ValueError:
                err_lbl.config(text="⚠  Date must be YYYY-MM-DD.")
                return

            self.expenses.append({
                "amount":      amt,
                "category":    cat_var.get(),
                "description": desc if desc else "—",
                "date":        date_raw,
            })
            save_expenses(self.expenses)
            messagebox.showinfo("Saved", "Expense added successfully! ✅")
            self.show_home_screen()

        self._btn(form, "💾  Save Expense", save, GREEN, width=22,
                  font=("Segoe UI", 12, "bold")).pack(pady=20)

    # ══════════════════════════════════════════════════════════════════════════
    # 3.  VIEW ALL EXPENSES SCREEN
    # ══════════════════════════════════════════════════════════════════════════
    def show_list_screen(self):
        self.clear_screen()

        header = tk.Frame(self.root, bg="#0EA5E9", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="📋  All Expenses", font=FONT_H1,
                 bg="#0EA5E9", fg="white").pack(side="left", padx=20, pady=10)
        self._btn(header, "← Back", self.show_home_screen, CARD, width=10
                  ).pack(side="right", padx=20, pady=12)

        # Filter bar
        filter_frame = tk.Frame(self.root, bg=BG)
        filter_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(filter_frame, text="Filter by category:", font=FONT_BODY,
                 bg=BG, fg=MUTED).pack(side="left")
        cat_var = tk.StringVar(value="All")
        cats = ["All"] + CATEGORIES
        cb = ttk.Combobox(filter_frame, textvariable=cat_var,
                          values=cats, state="readonly", width=14, font=FONT_BODY)
        cb.pack(side="left", padx=8)

        # Table
        style = ttk.Style()
        style.configure("List.Treeview",
                         background=CARD, foreground=TEXT,
                         fieldbackground=CARD, rowheight=30, font=FONT_BODY)
        style.configure("List.Treeview.Heading",
                         background="#0EA5E9", foreground="white",
                         font=("Segoe UI", 10, "bold"))
        style.map("List.Treeview", background=[("selected", ACCENT)])

        frame = tk.Frame(self.root, bg=BG)
        frame.pack(fill="both", expand=True, padx=20, pady=(0,16))

        cols = ("#", "Date", "Category", "Description", "Amount")
        tree = ttk.Treeview(frame, columns=cols, show="headings",
                             style="List.Treeview")
        for col, w in zip(cols, [40, 110, 110, 270, 110]):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center" if col != "Description" else "w")

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        def refresh(event=None):
            tree.delete(*tree.get_children())
            selected = cat_var.get()
            data = self.expenses if selected == "All" else \
                   [e for e in self.expenses if e["category"] == selected]
            for i, exp in enumerate(reversed(data), 1):
                tree.insert("", "end",
                             values=(i, exp["date"], exp["category"],
                                     exp["description"],
                                     f"₹{exp['amount']:,.2f}"))

        cb.bind("<<ComboboxSelected>>", refresh)
        refresh()

        # Delete selected
        def delete_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Please select a row to delete.")
                return
            if not messagebox.askyesno("Delete", "Delete selected expense?"):
                return
            item = tree.item(sel[0])["values"]
            # match by date + amount + description
            for i, e in enumerate(self.expenses):
                if (e["date"] == item[1] and e["category"] == item[2]
                        and f"₹{e['amount']:,.2f}" == item[4]):
                    self.expenses.pop(i)
                    break
            save_expenses(self.expenses)
            refresh()

        self._btn(self.root, "🗑  Delete Selected", delete_selected, RED
                  ).pack(pady=(0,12))

    # ══════════════════════════════════════════════════════════════════════════
    # 4.  CATEGORY SUMMARY SCREEN
    # ══════════════════════════════════════════════════════════════════════════
    def show_summary_screen(self):
        self.clear_screen()

        header = tk.Frame(self.root, bg="#F59E0B", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="📊  Category Summary", font=FONT_H1,
                 bg="#F59E0B", fg="white").pack(side="left", padx=20, pady=10)
        self._btn(header, "← Back", self.show_home_screen, CARD, width=10
                  ).pack(side="right", padx=20, pady=12)

        # Build totals
        totals = {}
        for e in self.expenses:
            totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]
        grand = sum(totals.values()) or 1   # avoid div-by-zero

        canvas_frame = tk.Frame(self.root, bg=BG)
        canvas_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Bar chart (pure Tkinter canvas — no matplotlib needed)
        BAR_W = 660
        BAR_H = 380
        c = tk.Canvas(canvas_frame, width=BAR_W, height=BAR_H,
                      bg=CARD, highlightthickness=0)
        c.pack(side="left")

        colours_list = ["#7C3AED","#22C55E","#EF4444","#F59E0B",
                        "#0EA5E9","#EC4899","#14B8A6","#A78BFA"]

        if totals:
            sorted_cats = sorted(totals.items(), key=lambda x: x[1], reverse=True)
            n = len(sorted_cats)
            bar_height = min(36, (BAR_H - 60) // n - 8)
            y0 = 30

            for i, (cat, total) in enumerate(sorted_cats):
                bar_len = int((total / grand) * (BAR_W - 220))
                y1 = y0 + bar_height
                col = colours_list[i % len(colours_list)]
                c.create_rectangle(130, y0, 130 + bar_len, y1, fill=col, outline="")
                c.create_text(120, (y0+y1)//2, text=cat, anchor="e",
                              font=FONT_BODY, fill=TEXT)
                c.create_text(140 + bar_len, (y0+y1)//2,
                              text=f"₹{total:,.0f}  ({total/grand*100:.1f}%)",
                              anchor="w", font=FONT_SM, fill=TEXT)
                y0 = y1 + 12
        else:
            c.create_text(BAR_W//2, BAR_H//2, text="No expenses yet.",
                          font=FONT_H2, fill=MUTED)

        # Side legend / totals list
        legend = tk.Frame(canvas_frame, bg=BG)
        legend.pack(side="left", fill="y", padx=(20,0))
        tk.Label(legend, text="Total", font=FONT_H2, bg=BG, fg=TEXT).pack(pady=(0,8))
        tk.Label(legend, text=f"₹{grand:,.2f}", font=("Segoe UI", 18, "bold"),
                 bg=BG, fg=GREEN).pack()
        tk.Label(legend, text=f"{len(self.expenses)} entries",
                 font=FONT_SM, bg=BG, fg=MUTED).pack(pady=(4,16))

        for i, (cat, total) in enumerate(sorted(totals.items(),
                                                  key=lambda x: x[1], reverse=True)):
            row_f = tk.Frame(legend, bg=BG)
            row_f.pack(anchor="w", pady=2)
            dot = tk.Canvas(row_f, width=12, height=12, bg=BG, highlightthickness=0)
            dot.create_oval(0,0,12,12, fill=colours_list[i % len(colours_list)], outline="")
            dot.pack(side="left", padx=(0,5))
            tk.Label(row_f, text=f"{cat}: ₹{total:,.0f}",
                     font=FONT_SM, bg=BG, fg=TEXT).pack(side="left")

    # ══════════════════════════════════════════════════════════════════════════
    # Helpers
    # ══════════════════════════════════════════════════════════════════════════
    def _btn(self, parent, text, cmd, colour,
             width=18, font=FONT_BODY):
        return tk.Button(parent, text=text, command=cmd,
                         bg=colour, fg="white", font=font,
                         width=width, relief="flat", cursor="hand2",
                         activebackground=colour, activeforeground="white",
                         padx=8, pady=6)

    def clear_all(self):
        if not self.expenses:
            messagebox.showinfo("Empty", "No expenses to clear.")
            return
        if messagebox.askyesno("Clear All",
                               "Delete ALL expenses permanently?"):
            self.expenses = []
            save_expenses(self.expenses)
            self.show_home_screen()


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = ExpenseApp(root)
    root.mainloop()