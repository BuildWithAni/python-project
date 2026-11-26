"""Tkinter GUI for the Student Report Card System.

Demonstrates: windows, labels, entry fields, buttons, dialogs, menus,
treeview, frames/notebooks, event bindings and embedded matplotlib charts
(Practical 30), plus everything the other modules cover.
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from .analytics import summarize, to_dataframe
from .charts import build_figure
from .models import SUBJECTS, Student
from .sample_data import sample_students
from .storage import StudentRepository


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "students.csv"

TABLE_COLUMNS = ["Roll No", "Name", *SUBJECTS, "Total", "Average", "Grade", "Result"]
COLUMN_WIDTHS = {
    "Roll No": 105,
    "Name": 120,
    **{subject: 66 for subject in SUBJECTS},
    "Total": 66,
    "Average": 72,
    "Grade": 60,
    "Result": 68,
}

class ReportCardApp(tk.Tk):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Student Report Card System  |  Anirudh - BTech CSE")
        self.geometry("1180x720")
        self.minsize(1020, 620)

        self.repository = StudentRepository(DATA_FILE)
        self.students: list[Student] = []

        # GUI variables
        self.var_name = tk.StringVar()
        self.var_roll = tk.StringVar()
        self.var_marks = {subject: tk.StringVar(value="0") for subject in SUBJECTS}
        self.var_search = tk.StringVar()
        self.var_status = tk.StringVar(value="Ready")
        self.var_count = tk.StringVar(value="0")
        self.var_average = tk.StringVar(value="-")
        self.var_topper = tk.StringVar(value="-")
        self.var_pass = tk.StringVar(value="-")

        # Chart widgets are replaced on every refresh.
        self.figure = None
        self.canvas = None
        self.canvas_widget = None
        self.toolbar = None

        self._build_menu()
        self._build_status_bar()
        self._build_tabs()
        self.refresh_all()

    # ------------------------------------------------------------------ UI
    def _build_menu(self) -> None:
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load Sample Data", command=self.on_load_sample)
        file_menu.add_separator()
        file_menu.add_command(label="Export CSV As...", command=self.on_export_csv)
        file_menu.add_command(label="Save Chart As PNG...", command=self.on_save_chart)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(
            label="Manage Students", command=lambda: self.notebook.select(self.manage_tab)
        )
        view_menu.add_command(
            label="Dashboard", command=lambda: self.notebook.select(self.dashboard_tab)
        )
        menubar.add_cascade(label="View", menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.on_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

    def _build_status_bar(self) -> None:
        ttk.Label(
            self, textvariable=self.var_status, anchor="w", relief="sunken", padding=(6, 2)
        ).pack(side="bottom", fill="x")

    def _build_tabs(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(8, 4))

        self.manage_tab = ttk.Frame(self.notebook)
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.manage_tab, text="  Manage Students  ")
        self.notebook.add(self.dashboard_tab, text="  Dashboard  ")

        self._build_manage_tab()
        self._build_dashboard_tab()

    def _build_manage_tab(self) -> None:
        # ---- Left side: input form ----
        left = ttk.Frame(self.manage_tab)
        left.pack(side="left", fill="y", padx=(4, 8), pady=4)

        form = ttk.LabelFrame(left, text="Student Details", padding=12)
        form.pack(fill="y")

        ttk.Label(form, text="Name:").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.var_name, width=22).grid(row=0, column=1, pady=4)

        ttk.Label(form, text="Roll No:").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.var_roll, width=22).grid(row=1, column=1, pady=4)

        ttk.Label(
            form, text="Marks (0-100):", font=("Segoe UI", 9, "bold")
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(12, 2))

        for row, subject in enumerate(SUBJECTS, start=3):
            ttk.Label(form, text=f"{subject}:").grid(row=row, column=0, sticky="w", pady=3)
            ttk.Spinbox(
                form, from_=0, to=100, textvariable=self.var_marks[subject], width=20
            ).grid(row=row, column=1, pady=3)

        buttons = ttk.Frame(form)
        buttons.grid(row=3 + len(SUBJECTS), column=0, columnspan=2, pady=(16, 0))
        ttk.Button(buttons, text="Add / Update", command=self.on_add_update, width=13).grid(
            row=0, column=0, padx=3, pady=3
        )
        ttk.Button(buttons, text="Clear Form", command=self.clear_form, width=13).grid(
            row=0, column=1, padx=3, pady=3
        )
        ttk.Button(buttons, text="Delete", command=self.on_delete, width=13).grid(
            row=1, column=0, padx=3, pady=3
        )
        ttk.Button(buttons, text="Clear All", command=self.on_clear_all, width=13).grid(
            row=1, column=1, padx=3, pady=3
        )

        # ---- Right side: search + table ----
        right = ttk.Frame(self.manage_tab)
        right.pack(side="left", fill="both", expand=True, padx=(0, 4), pady=4)

        search_bar = ttk.Frame(right)
        search_bar.pack(fill="x", pady=(0, 6))
        ttk.Label(search_bar, text="Search:").pack(side="left")
        ttk.Entry(search_bar, textvariable=self.var_search, width=26).pack(
            side="left", padx=6, fill="x", expand=True
        )
        ttk.Button(search_bar, text="Find", command=self.on_search).pack(side="left")
        ttk.Button(search_bar, text="Show All", command=self.on_show_all).pack(
            side="left", padx=4
        )
        self.var_search.trace_add("write", lambda *_: self.on_search())

        table = ttk.Frame(right)
        table.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            table, columns=TABLE_COLUMNS, show="headings", height=17, selectmode="browse"
        )
        for column in TABLE_COLUMNS:
            self.tree.heading(column, text=column)
            anchor = tk.W if column in ("Roll No", "Name") else tk.CENTER
            self.tree.column(column, width=COLUMN_WIDTHS[column], anchor=anchor)
        self.tree.tag_configure("Pass", foreground="#187a3a")
        self.tree.tag_configure("Fail", foreground="#c0392b")

        yscroll = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(table, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        yscroll.pack(side="right", fill="y")
        xscroll.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.on_select)

        ttk.Label(
            right,
            text="Tip: double-click a row to edit it. Roll No is the unique key.",
            foreground="#666666",
        ).pack(anchor="w", pady=(6, 0))

    def _build_dashboard_tab(self) -> None:
        cards = ttk.Frame(self.dashboard_tab)
        cards.pack(fill="x", padx=6, pady=8)
        for column in range(4):
            cards.columnconfigure(column, weight=1)

        self._make_card(cards, "Students", self.var_count, 0, font_size=18)
        self._make_card(cards, "Class Average", self.var_average, 1, font_size=18)
        self._make_card(cards, "Topper", self.var_topper, 2, font_size=12)
        self._make_card(cards, "Pass Percentage", self.var_pass, 3, font_size=18)

        chart_box = ttk.LabelFrame(
            self.dashboard_tab, text="Class Analytics  (Pandas + Matplotlib)", padding=6
        )
        chart_box.pack(fill="both", expand=True, padx=6, pady=(0, 8))

        controls = ttk.Frame(chart_box)
        controls.pack(side="bottom", fill="x", pady=(4, 0))
        ttk.Button(controls, text="Refresh Charts", command=self.refresh_dashboard).pack(
            side="left"
        )
        ttk.Button(controls, text="Save Chart As PNG...", command=self.on_save_chart).pack(
            side="left", padx=6
        )
        self.chart_frame = ttk.Frame(chart_box)
        self.chart_frame.pack(fill="both", expand=True)

    @staticmethod
    def _make_card(parent, title, variable, column, font_size) -> None:
        card = ttk.LabelFrame(parent, text=title, padding=10)
        card.grid(row=0, column=column, sticky="nsew", padx=6)
        tk.Label(
            card, textvariable=variable, font=("Segoe UI", font_size, "bold"),
            foreground="#2b5d8a",
        ).pack()

    # ------------------------------------------------------------ data flow
    def refresh_all(self) -> None:
        """Reload from CSV and repaint both tabs."""
        self.students = self.repository.load()
        self.refresh_table()
        self.refresh_dashboard()

    def refresh_table(self) -> None:
        """Fill the treeview, optionally filtered by the search box."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        query = self.var_search.get().strip().lower()
        visible = [
            student
            for student in self.students
            if query in student.roll_no.lower() or query in student.name.lower()
        ]

        for student in visible:
            row = student.to_row()
            values = []
            for column in TABLE_COLUMNS:
                value = row[column]
                values.append(f"{value:.1f}" if isinstance(value, float) else str(value))
            self.tree.insert("", tk.END, values=values, tags=(student.result,))

        self.var_status.set(f"Showing {len(visible)} of {len(self.students)} students")

    def refresh_dashboard(self) -> None:
        """Recalculate statistics and redraw the embedded charts."""
        df = to_dataframe(self.students)
        stats = summarize(df)
        self.var_count.set(str(stats["count"]))
        self.var_average.set(
            f"{stats['average']:.1f}" if stats["count"] else "-"
        )
        self.var_topper.set(stats["topper"])
        self.var_pass.set(f"{stats['pass_percent']:.0f}%" if stats["count"] else "-")

        # Destroy the previous canvas/toolbar before drawing a new figure.
        if self.canvas_widget is not None:
            self.canvas_widget.destroy()
        if self.toolbar is not None:
            self.toolbar.destroy()

        self.figure = build_figure(df)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.chart_frame)
        self.toolbar.update()
        self.canvas.draw()

    def clear_form(self) -> None:
        self.var_name.set("")
        self.var_roll.set("")
        for variable in self.var_marks.values():
            variable.set("0")
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def read_form(self) -> Student:
        """Read the form into a validated Student object."""
        name = self.var_name.get().strip()
        roll = self.var_roll.get().strip()
        marks = {}
        for subject, variable in self.var_marks.items():
            text = variable.get().strip()
            if not text:
                raise ValueError(f"Enter marks for {subject}.")
            try:
                marks[subject] = float(text)
            except ValueError as exc:
                raise ValueError(f"{subject} marks must be a number.") from exc

        student = Student(roll, name, marks)
        student.validate()
        return student

    # --------------------------------------------------------------- events
    def on_add_update(self) -> None:
        try:
            student = self.read_form()
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc), parent=self)
            return

        index = next(
            (
                i
                for i, existing in enumerate(self.students)
                if existing.roll_no.lower() == student.roll_no.lower()
            ),
            None,
        )
        if index is None:
            self.students.append(student)
            action = "Added"
        else:
            self.students[index] = student
            action = "Updated"

        self.repository.save(self.students)
        self.clear_form()
        self.refresh_all()
        self.var_status.set(f"{action}: {student.name} ({student.roll_no})")

    def on_select(self, _event=None) -> None:
        """Load the double-clicked/selected row back into the form."""
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0], "values")
        row = dict(zip(TABLE_COLUMNS, values))
        self.var_roll.set(row["Roll No"])
        self.var_name.set(row["Name"])
        for subject in SUBJECTS:
            self.var_marks[subject].set(row[subject])

    def on_delete(self) -> None:
        selection = self.tree.selection()
        roll = (
            self.tree.item(selection[0], "values")[0]
            if selection
            else self.var_roll.get().strip()
        )
        if not roll:
            messagebox.showwarning("Delete", "Select a student first.", parent=self)
            return
        if not messagebox.askyesno(
            "Confirm delete", f"Delete student with Roll No {roll}?", parent=self
        ):
            return

        before = len(self.students)
        self.students = [
            student
            for student in self.students
            if student.roll_no.lower() != roll.lower()
        ]
        self.repository.save(self.students)
        self.clear_form()
        self.refresh_all()
        self.var_status.set(f"Deleted {before - len(self.students)} record(s)")

    def on_clear_all(self) -> None:
        if not messagebox.askyesno(
            "Confirm", "Delete ALL student records? This cannot be undone.", parent=self
        ):
            return
        self.repository.save([])
        self.clear_form()
        self.refresh_all()
        self.var_status.set("All records cleared")

    def on_search(self) -> None:
        self.refresh_table()

    def on_show_all(self) -> None:
        self.var_search.set("")
        self.refresh_table()

    def on_load_sample(self) -> None:
        if not messagebox.askyesno(
            "Sample data", "Replace the current records with 12 sample students?",
            parent=self,
        ):
            return
        self.students = sample_students()
        self.repository.save(self.students)
        self.clear_form()
        self.var_search.set("")
        self.refresh_all()
        self.var_status.set("Loaded 12 sample students")

    def on_export_csv(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export report as CSV",
            defaultextension=".csv",
            initialfile="students_report.csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            parent=self,
        )
        if path:
            self.repository.save(self.students, path)
            self.var_status.set(f"Exported {len(self.students)} records to {path}")

    def on_save_chart(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save dashboard chart",
            defaultextension=".png",
            initialfile="class_analytics.png",
            filetypes=[("PNG images", "*.png"), ("All files", "*.*")],
            parent=self,
        )
        if path and self.figure is not None:
            self.figure.savefig(path, dpi=150, bbox_inches="tight")
            self.var_status.set(f"Chart saved to {path}")

    @staticmethod
    def on_about() -> None:
        messagebox.showinfo(
            "About",
            "Student Report Card System\n\n"
            "A Python GUI mini-project by Anirudh (BTech CSE).\n"
            "Built with Tkinter, CSV, pandas and matplotlib.\n\n"
            "Features: add/update/delete students, auto grading, search,\n"
            "CSV export and an analytics dashboard with charts.",
        )
