import sqlite3
import tkinter as tk
from tkinter import messagebox

DB_PATH = "cast_management.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS girls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store TEXT NOT NULL,
                name TEXT NOT NULL,
                age INTEGER,
                note TEXT
            )
            """
        )


def fetch_all():
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT id, store, name, age, note FROM girls ORDER BY store, name"
        ).fetchall()


def insert_girl(store, name, age, note):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO girls (store, name, age, note) VALUES (?, ?, ?, ?)",
            (store, name, age, note),
        )


def update_girl(girl_id, store, name, age, note):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE girls SET store = ?, name = ?, age = ?, note = ? WHERE id = ?",
            (store, name, age, note, girl_id),
        )


def delete_girl(girl_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM girls WHERE id = ?", (girl_id,))


class CastManagementApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("店舗横断キャスト管理")
        self.geometry("820x420")
        self.resizable(False, False)

        self.selected_id = None
        self.listbox = None

        self.store_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.note_var = tk.StringVar()

        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        list_frame = tk.Frame(self, padx=10, pady=10)
        form_frame = tk.Frame(self, padx=10, pady=10)

        list_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        form_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(list_frame, text="登録一覧").pack(anchor="w")
        self.listbox = tk.Listbox(list_frame, width=32, height=18)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        tk.Label(form_frame, text="店舗名").grid(row=0, column=0, sticky="w")
        tk.Entry(form_frame, textvariable=self.store_var, width=30).grid(
            row=0, column=1, pady=4
        )

        tk.Label(form_frame, text="名前").grid(row=1, column=0, sticky="w")
        tk.Entry(form_frame, textvariable=self.name_var, width=30).grid(
            row=1, column=1, pady=4
        )

        tk.Label(form_frame, text="年齢").grid(row=2, column=0, sticky="w")
        tk.Entry(form_frame, textvariable=self.age_var, width=30).grid(
            row=2, column=1, pady=4
        )

        tk.Label(form_frame, text="メモ").grid(row=3, column=0, sticky="nw")
        tk.Entry(form_frame, textvariable=self.note_var, width=30).grid(
            row=3, column=1, pady=4
        )

        button_frame = tk.Frame(form_frame, pady=10)
        button_frame.grid(row=4, column=0, columnspan=2)

        tk.Button(button_frame, text="追加", width=10, command=self.add_record).grid(
            row=0, column=0, padx=5
        )
        tk.Button(button_frame, text="更新", width=10, command=self.update_record).grid(
            row=0, column=1, padx=5
        )
        tk.Button(button_frame, text="削除", width=10, command=self.delete_record).grid(
            row=0, column=2, padx=5
        )
        tk.Button(button_frame, text="クリア", width=10, command=self.clear_form).grid(
            row=0, column=3, padx=5
        )

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for girl_id, store, name, age, note in fetch_all():
            display = f"{store} | {name}"
            if age:
                display += f" ({age})"
            self.listbox.insert(tk.END, display)
            self.listbox.itemconfig(tk.END, {'fg': 'black'})
            self.listbox.insert(tk.END, f"  メモ: {note or ''}")
            self.listbox.insert(tk.END, "")
            self.listbox.itemconfig(tk.END, {'fg': 'gray'})
        self.listbox.yview_moveto(0)

    def on_select(self, _event):
        selection = self.listbox.curselection()
        if not selection:
            return

        index = selection[0]
        items = fetch_all()
        record_index = index // 3
        if record_index >= len(items):
            return

        girl_id, store, name, age, note = items[record_index]
        self.selected_id = girl_id
        self.store_var.set(store)
        self.name_var.set(name)
        self.age_var.set(str(age) if age else "")
        self.note_var.set(note or "")

    def add_record(self):
        store = self.store_var.get().strip()
        name = self.name_var.get().strip()
        age_value = self.age_var.get().strip()
        note = self.note_var.get().strip()

        if not store or not name:
            messagebox.showwarning("入力不足", "店舗名と名前は必須です。")
            return

        age = int(age_value) if age_value.isdigit() else None
        insert_girl(store, name, age, note)
        self.clear_form()
        self.refresh_list()

    def update_record(self):
        if not self.selected_id:
            messagebox.showinfo("未選択", "更新するレコードを選択してください。")
            return

        store = self.store_var.get().strip()
        name = self.name_var.get().strip()
        age_value = self.age_var.get().strip()
        note = self.note_var.get().strip()

        if not store or not name:
            messagebox.showwarning("入力不足", "店舗名と名前は必須です。")
            return

        age = int(age_value) if age_value.isdigit() else None
        update_girl(self.selected_id, store, name, age, note)
        self.refresh_list()

    def delete_record(self):
        if not self.selected_id:
            messagebox.showinfo("未選択", "削除するレコードを選択してください。")
            return

        if not messagebox.askyesno("確認", "選択したレコードを削除しますか？"):
            return

        delete_girl(self.selected_id)
        self.clear_form()
        self.refresh_list()

    def clear_form(self):
        self.selected_id = None
        self.store_var.set("")
        self.name_var.set("")
        self.age_var.set("")
        self.note_var.set("")
        self.listbox.selection_clear(0, tk.END)


def main():
    init_db()
    app = CastManagementApp()
    app.mainloop()


if __name__ == "__main__":
    main()
