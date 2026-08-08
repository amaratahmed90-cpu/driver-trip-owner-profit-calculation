import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime


DB_NAME = "driver_trip.db"


# ---------------- DATABASE ----------------

def connect_db():
    return sqlite3.connect(DB_NAME)


def create_database():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_date TEXT NOT NULL,
            driver_name TEXT NOT NULL,
            vehicle_no TEXT NOT NULL,
            from_place TEXT NOT NULL,
            to_place TEXT NOT NULL,
            fare REAL NOT NULL,
            expense REAL NOT NULL,
            profit REAL NOT NULL,
            note TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------- FUNCTIONS ----------------

def clear_fields():
    date_entry.delete(0, tk.END)
    date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    driver_entry.delete(0, tk.END)
    vehicle_entry.delete(0, tk.END)
    from_entry.delete(0, tk.END)
    to_entry.delete(0, tk.END)
    fare_entry.delete(0, tk.END)
    expense_entry.delete(0, tk.END)
    note_entry.delete(0, tk.END)


def add_trip():
    trip_date = date_entry.get().strip()
    driver = driver_entry.get().strip()
    vehicle = vehicle_entry.get().strip()
    from_place = from_entry.get().strip()
    to_place = to_entry.get().strip()
    note = note_entry.get().strip()

    try:
        datetime.strptime(trip_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror(
            "Error",
            "Date অবশ্যই YYYY-MM-DD format-এ দিন।"
        )
        return

    if not driver or not vehicle or not from_place or not to_place:
        messagebox.showerror(
            "Error",
            "Driver, Vehicle, From এবং To পূরণ করুন।"
        )
        return

    try:
        fare = float(fare_entry.get())
        expense = float(expense_entry.get())
    except ValueError:
        messagebox.showerror(
            "Error",
            "Fare এবং Expense সংখ্যায় লিখুন।"
        )
        return

    if fare < 0 or expense < 0:
        messagebox.showerror(
            "Error",
            "Fare এবং Expense negative হতে পারবে না।"
        )
        return

    profit = fare - expense

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO trips (
            trip_date,
            driver_name,
            vehicle_no,
            from_place,
            to_place,
            fare,
            expense,
            profit,
            note
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trip_date,
        driver,
        vehicle,
        from_place,
        to_place,
        fare,
        expense,
        profit,
        note
    ))

    conn.commit()
    conn.close()

    messagebox.showinfo(
        "Success",
        f"Trip saved successfully!\n\nProfit: ৳ {profit:,.2f}"
    )

    clear_fields()
    load_trips()


def load_trips():
    for item in tree.get_children():
        tree.delete(item)

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            trip_date,
            driver_name,
            vehicle_no,
            from_place,
            to_place,
            fare,
            expense,
            profit
        FROM trips
        ORDER BY trip_date DESC, id DESC
    """)

    rows = cursor.fetchall()

    total_fare = 0
    total_expense = 0
    total_profit = 0

    for row in rows:
        tree.insert("", tk.END, values=(
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            f"{row[6]:,.2f}",
            f"{row[7]:,.2f}",
            f"{row[8]:,.2f}"
        ))

        total_fare += row[6]
        total_expense += row[7]
        total_profit += row[8]

    conn.close()

    fare_total_label.config(
        text=f"৳ {total_fare:,.2f}"
    )

    expense_total_label.config(
        text=f"৳ {total_expense:,.2f}"
    )

    profit_total_label.config(
        text=f"৳ {total_profit:,.2f}"
    )


def delete_trip():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning(
            "Warning",
            "Delete করার জন্য একটি Trip select করুন।"
        )
        return

    item = tree.item(selected[0])
    trip_id = item["values"][0]

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "আপনি কি এই Trip টি delete করতে চান?"
    )

    if not confirm:
        return

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM trips WHERE id = ?",
        (trip_id,)
    )

    conn.commit()
    conn.close()

    load_trips()


def monthly_report():
    report_window = tk.Toplevel(root)
    report_window.title("Monthly Profit Report")
    report_window.geometry("500x400")
    report_window.resizable(False, False)

    title = tk.Label(
        report_window,
        text="Monthly Profit Report",
        font=("Arial", 18, "bold")
    )
    title.pack(pady=15)

    input_frame = tk.Frame(report_window)
    input_frame.pack(pady=10)

    tk.Label(
        input_frame,
        text="Year:",
        font=("Arial", 11)
    ).grid(row=0, column=0, padx=5)

    year_entry = tk.Entry(
        input_frame,
        width=10
    )
    year_entry.grid(row=0, column=1, padx=5)
    year_entry.insert(0, datetime.now().strftime("%Y"))

    tk.Label(
        input_frame,
        text="Month:",
        font=("Arial", 11)
    ).grid(row=0, column=2, padx=5)

    month_entry = tk.Entry(
        input_frame,
        width=10
    )
    month_entry.grid(row=0, column=3, padx=5)
    month_entry.insert(0, datetime.now().strftime("%m"))

    result_label = tk.Label(
        report_window,
        text="",
        font=("Arial", 13),
        justify="left"
    )
    result_label.pack(pady=20)

    def calculate_report():
        year = year_entry.get().strip()
        month = month_entry.get().strip()

        if not year.isdigit() or not month.isdigit():
            messagebox.showerror(
                "Error",
                "Year এবং Month সঠিকভাবে দিন।"
            )
            return

        month_number = int(month)

        if month_number < 1 or month_number > 12:
            messagebox.showerror(
                "Error",
                "Month 1 থেকে 12 এর মধ্যে হতে হবে।"
            )
            return

        month_text = f"{month_number:02d}"

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*),
                COALESCE(SUM(fare), 0),
                COALESCE(SUM(expense), 0),
                COALESCE(SUM(profit), 0)
            FROM trips
            WHERE substr(trip_date, 1, 4) = ?
              AND substr(trip_date, 6, 2) = ?
        """, (year, month_text))

        result = cursor.fetchone()
        conn.close()

        trips = result[0]
        fare = result[1]
        expense = result[2]
        profit = result[3]

        result_label.config(
            text=(
                f"Month: {year}-{month_text}\n\n"
                f"Total Trips     : {trips}\n"
                f"Total Fare      : ৳ {fare:,.2f}\n"
                f"Total Expense   : ৳ {expense:,.2f}\n"
                f"Owner Profit    : ৳ {profit:,.2f}"
            )
        )

    tk.Button(
        report_window,
        text="Calculate Report",
        command=calculate_report,
        bg="#1f6feb",
        fg="white",
        font=("Arial", 11, "bold"),
        padx=15,
        pady=7
    ).pack()


# ---------------- MAIN WINDOW ----------------

create_database()

root = tk.Tk()
root.title("Driver Trip & Owner Profit Calculation")
root.geometry("1250x720")
root.minsize(1100, 650)

title_label = tk.Label(
    root,
    text="Driver Trip & Owner Profit Calculation",
    font=("Arial", 22, "bold")
)
title_label.pack(pady=15)


# ---------------- INPUT FRAME ----------------

input_frame = tk.LabelFrame(
    root,
    text="Trip Information",
    font=("Arial", 12, "bold"),
    padx=10,
    pady=10
)
input_frame.pack(fill="x", padx=15, pady=5)


tk.Label(input_frame, text="Date").grid(
    row=0, column=0, padx=5, pady=5
)

date_entry = tk.Entry(input_frame, width=18)
date_entry.grid(row=0, column=1, padx=5, pady=5)
date_entry.insert(
    0,
    datetime.now().strftime("%Y-%m-%d")
)


tk.Label(input_frame, text="Driver Name").grid(
    row=0, column=2, padx=5, pady=5
)

driver_entry = tk.Entry(input_frame, width=18)
driver_entry.grid(row=0, column=3, padx=5, pady=5)


tk.Label(input_frame, text="Vehicle No").grid(
    row=0, column=4, padx=5, pady=5
)

vehicle_entry = tk.Entry(input_frame, width=18)
vehicle_entry.grid(row=0, column=5, padx=5, pady=5)


tk.Label(input_frame, text="From").grid(
    row=1, column=0, padx=5, pady=5
)

from_entry = tk.Entry(input_frame, width=18)
from_entry.grid(row=1, column=1, padx=5, pady=5)


tk.Label(input_frame, text="To").grid(
    row=1, column=2, padx=5, pady=5
)

to_entry = tk.Entry(input_frame, width=18)
to_entry.grid(row=1, column=3, padx=5, pady=5)


tk.Label(input_frame, text="Fare").grid(
    row=1, column=4, padx=5, pady=5
)

fare_entry = tk.Entry(input_frame, width=18)
fare_entry.grid(row=1, column=5, padx=5, pady=5)


tk.Label(input_frame, text="Expense").grid(
    row=2, column=0, padx=5, pady=5
)

expense_entry = tk.Entry(input_frame, width=18)
expense_entry.grid(row=2, column=1, padx=5, pady=5)


tk.Label(input_frame, text="Note").grid(
    row=2, column=2, padx=5, pady=5
)

note_entry = tk.Entry(input_frame, width=18)
note_entry.grid(row=2, column=3, padx=5, pady=5)


button_frame = tk.Frame(input_frame)
button_frame.grid(
    row=2,
    column=4,
    columnspan=2,
    padx=5,
    pady=5
)


tk.Button(
    button_frame,
    text="Save Trip",
    command=add_trip,
    bg="#198754",
    fg="white",
    font=("Arial", 10, "bold"),
    padx=12
).pack(side="left", padx=5)


tk.Button(
    button_frame,
    text="Clear",
    command=clear_fields,
    padx=12
).pack(side="left", padx=5)


tk.Button(
    button_frame,
    text="Monthly Report",
    command=monthly_report,
    bg="#6f42c1",
    fg="white",
    font=("Arial", 10, "bold"),
    padx=12
).pack(side="left", padx=5)


# ---------------- TABLE ----------------

table_frame = tk.Frame(root)
table_frame.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=10
)

columns = (
    "ID",
    "Date",
    "Driver",
    "Vehicle",
    "From",
    "To",
    "Fare",
    "Expense",
    "Profit"
)

tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)

for column in columns:
    tree.heading(
        column,
        text=column
    )

    if column in ("From", "To"):
        tree.column(
            column,
            width=120,
            anchor="center"
        )
    else:
        tree.column(
            column,
            width=100,
            anchor="center"
        )

scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=tree.yview
)

tree.configure(
    yscrollcommand=scrollbar.set
)

tree.pack(
    side="left",
    fill="both",
    expand=True
)

scrollbar.pack(
    side="right",
    fill="y"
)


# ---------------- DELETE ----------------

tk.Button(
    root,
    text="Delete Selected Trip",
    command=delete_trip,
    bg="#dc3545",
    fg="white",
    font=("Arial", 10, "bold"),
    padx=15,
    pady=6
).pack(pady=5)


# ---------------- TOTALS ----------------

totals_frame = tk.Frame(root)
totals_frame.pack(
    fill="x",
    padx=15,
    pady=10
)


tk.Label(
    totals_frame,
    text="Total Fare",
    font=("Arial", 12, "bold")
).pack(side="left", padx=10)

fare_total_label = tk.Label(
    totals_frame,
    text="৳ 0.00",
    font=("Arial", 13, "bold")
)
fare_total_label.pack(side="left", padx=10)


tk.Label(
    totals_frame,
    text="Total Expense",
    font=("Arial", 12, "bold")
).pack(side="left", padx=10)

expense_total_label = tk.Label(
    totals_frame,
    text="৳ 0.00",
    font=("Arial", 13, "bold")
)
expense_total_label.pack(side="left", padx=10)


tk.Label(
    totals_frame,
    text="Owner Profit",
    font=("Arial", 12, "bold")
).pack(side="left", padx=10)

profit_total_label = tk.Label(
    totals_frame,
    text="৳ 0.00",
    font=("Arial", 13, "bold")
)
profit_total_label.pack(side="left", padx=10)


load_trips()

root.mainloop()