import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from bcrypt import hashpw, gensalt, checkpw

class AuthenticationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Authentication App")

        self.tabControl = ttk.Notebook(root)

        # Вкладка "Увійти"
        self.login_frame = ttk.Frame(self.tabControl)
        self.tabControl.add(self.login_frame, text="Увійти")
        self.login_ui()

        # Вкладка "Зареєструватися"
        self.register_frame = ttk.Frame(self.tabControl)
        self.tabControl.add(self.register_frame, text="Зареєструватися")
        self.register_ui()

        self.tabControl.pack(expand=1, fill="both")

        # Підключення до бази даних
        self.conn = sqlite3.connect("users.db")
        self.cursor = self.conn.cursor()

        # Створення таблиці користувачів, якщо вона не існує
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def login_ui(self):
        ttk.Label(self.login_frame, text="Логін:").grid(row=0, column=0, padx=5, pady=5)
        self.login_username_var = tk.StringVar()
        login_username_entry = ttk.Entry(self.login_frame, textvariable=self.login_username_var)
        login_username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.login_frame, text="Пароль:").grid(row=1, column=0, padx=5, pady=5)
        self.login_password_var = tk.StringVar()
        login_password_entry = ttk.Entry(self.login_frame, textvariable=self.login_password_var, show="*")
        login_password_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self.login_frame, text="Увійти", command=self.login).grid(row=2, column=0, columnspan=2, pady=10)

    def register_ui(self):
        ttk.Label(self.register_frame, text="Логін:").grid(row=0, column=0, padx=5, pady=5)
        self.register_username_var = tk.StringVar()
        register_username_entry = ttk.Entry(self.register_frame, textvariable=self.register_username_var)
        register_username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.register_frame, text="Пароль:").grid(row=1, column=0, padx=5, pady=5)
        self.register_password_var = tk.StringVar()
        register_password_entry = ttk.Entry(self.register_frame, textvariable=self.register_password_var, show="*")
        register_password_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self.register_frame, text="Зареєструватися", command=self.register).grid(row=2, column=0, columnspan=2, pady=10)

    def login(self):
        username = self.login_username_var.get()
        password = self.login_password_var.get()

        if not username or not password:
            messagebox.showinfo("Помилка", "Будь ласка, введіть логін і пароль.")
            return

        user_data = self.cursor.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

        if user_data and checkpw(password.encode("utf-8"), user_data[2]):
            self.root.destroy()  # Закриємо вікно аутентифікації
            app = TransportApp(tk.Tk())  # Створимо новий екземпляр TransportApp
            app.root.mainloop()
        else:
            messagebox.showinfo("Помилка", "Невірний логін або пароль.")

    def register(self):
        username = self.register_username_var.get()
        password = self.register_password_var.get()

        if not username or not password:
            messagebox.showinfo("Помилка", "Будь ласка, введіть логін і пароль.")
            return

        hashed_password = hashpw(password.encode("utf-8"), gensalt())

        try:
            self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            self.conn.commit()
            messagebox.showinfo("Успіх", "Реєстрація пройшла успішно. Тепер ви можете увійти.")
        except sqlite3.IntegrityError:
            messagebox.showinfo("Помилка", "Користувач з таким логіном вже існує.")


class TransportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Розклад руху автотранспорту")

        # Підключення до бази даних SQLite
        self.conn = sqlite3.connect('transport_schedule.db')
        self.create_tables()

        # Створення інтерфейсу
        self.create_widgets()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT,
                model TEXT,
                year INTEGER,
                registration_number TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_name TEXT,
                first_name TEXT,
                birthdate TEXT,
                experience INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cargo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER,
                driver_id INTEGER,
                cargo_type TEXT,
                departure_point TEXT,
                destination_point TEXT,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
                FOREIGN KEY (driver_id) REFERENCES drivers(id)
            )
        ''')

        self.conn.commit()

    def create_widgets(self):
        # Перегляд вантажівок
        ttk.Button(self.root, text="Переглянути вантажівки", command=self.view_vehicles).pack(pady=10)

        # Перегляд водіїв
        ttk.Button(self.root, text="Переглянути водіїв", command=self.view_drivers).pack(pady=10)

        # Перегляд вантажів
        ttk.Button(self.root, text="Переглянути вантажі", command=self.view_cargo).pack(pady=10)

    def view_vehicles(self):
        view_window = tk.Toplevel(self.root)
        view_window.title("Вантажівки")

        # Створення таблиці для виведення даних
        tree = ttk.Treeview(view_window, columns=(1, 2, 3, 4, 5), show="headings", height=10)
        tree.pack()

        # Визначення назв стовбців
        tree.heading(1, text="ID")
        tree.heading(2, text="Марка")
        tree.heading(3, text="Модель")
        tree.heading(4, text="Рік випуску")
        tree.heading(5, text="Номер реєстрації")

        # Отримання даних з бази даних та виведення їх у таблицю
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM vehicles')
        data = cursor.fetchall()
        for row in data:
            tree.insert('', 'end', values=row)

        # Додавання кнопок для додавання, редагування та видалення
        btn_add = ttk.Button(view_window, text="Додати вантажівку", command=lambda: self.add_vehicle(view_window, tree))
        btn_edit = ttk.Button(view_window, text="Редагувати", command=lambda: self.edit_vehicle(tree))
        btn_delete = ttk.Button(view_window, text="Видалити", command=lambda: self.delete_vehicle(tree))

        btn_add.pack(pady=10)
        btn_edit.pack(pady=10)
        btn_delete.pack(pady=10)

    def add_vehicle(self, view_window, tree):
        add_window = tk.Toplevel(self.root)
        add_window.title("Додати вантажівку")

        # Створення полів для введення даних
        fields = ["Марка:", "Модель:", "Рік випуску:", "Номер реєстрації:"]
        entry_vars = []
        for field in fields:
            frame = ttk.Frame(add_window)
            frame.pack(fill=tk.X, pady=5)
            label = ttk.Label(frame, text=field)
            label.pack(side=tk.LEFT)
            entry_var = tk.StringVar()
            entry = ttk.Entry(frame, textvariable=entry_var)
            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            entry_vars.append(entry_var)

        # Кнопка для збереження вантажівки в базі даних
        ttk.Button(add_window, text="Зберегти", command=lambda: self.save_vehicle(entry_vars, add_window, tree)).pack(pady=10)

    def save_vehicle(self, entry_vars, add_window, tree):
        data = [var.get() for var in entry_vars]
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO vehicles (brand, model, year, registration_number)
            VALUES (?, ?, ?, ?)
        ''', data)
        self.conn.commit()

        # Оновлення таблиці
        self.load_data_into_table("vehicles", tree)

        add_window.destroy()

    def edit_vehicle(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Попередження", "Будь ласка, виберіть вантажівку для редагування.")
            return

        selected_item_id = tree.item(selected_item, "values")[0]

        # Отримання даних вибраної вантажівки
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM vehicles WHERE id=?', (selected_item_id,))
        vehicle_data = cursor.fetchone()

        # Створення вікна редагування
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редагувати вантажівку")

        # Створення полів для введення даних
        fields = ["Марка:", "Модель:", "Рік випуску:", "Номер реєстрації:"]
        entry_vars = []
        for field, value in zip(fields, vehicle_data[1:]):  # Починаємо з 1-го елемента, оскільки 0 - це ID
            frame = ttk.Frame(edit_window)
            frame.pack(fill=tk.X, pady=5)
            label = ttk.Label(frame, text=field)
            label.pack(side=tk.LEFT)
            entry_var = tk.StringVar(value=value)
            entry = ttk.Entry(frame, textvariable=entry_var)
            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            entry_vars.append(entry_var)

        # Кнопка для збереження змін вантажівки
        ttk.Button(edit_window, text="Зберегти", command=lambda: self.save_edited_vehicle(selected_item_id, entry_vars, edit_window, tree)).pack(pady=10)

    def delete_vehicle(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Попередження", "Будь ласка, виберіть вантажівку для видалення.")
            return

        result = messagebox.askquestion("Підтвердження", "Ви впевнені, що хочете видалити вибрану вантажівку?")
        if result == 'yes':
            selected_item_id = tree.item(selected_item, "values")[0]
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM vehicles WHERE id=?", (selected_item_id,))
            self.conn.commit()
            tree.delete(selected_item)

            # Оновлення таблиці
            self.load_data_into_table("vehicles", tree)

    def save_edited_vehicle(self, selected_item_id, entry_vars, edit_window, tree):
        data = [var.get() for var in entry_vars]
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE vehicles 
            SET brand=?, model=?, year=?, registration_number=?
            WHERE id=?
        ''', data + [selected_item_id])
        self.conn.commit()
        edit_window.destroy()

        # Оновлення таблиці
        self.load_data_into_table("vehicles", tree)

    def view_drivers(self):
        view_window = tk.Toplevel(self.root)
        view_window.title("Водії")

        # Створення таблиці для виведення даних
        tree = ttk.Treeview(view_window, columns=(1, 2, 3, 4, 5), show="headings", height=10)
        tree.pack()

        # Визначення назв стовбців
        tree.heading(1, text="ID")
        tree.heading(2, text="Прізвище")
        tree.heading(3, text="Ім'я")
        tree.heading(4, text="Дата народження")
        tree.heading(5, text="Стаж")

        # Отримання даних з бази даних та виведення їх у таблицю
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM drivers')
        data = cursor.fetchall()
        for row in data:
            tree.insert('', 'end', values=row)

        # Додавання кнопок для додавання, редагування та видалення
        btn_add = ttk.Button(view_window, text="Додати водія", command=lambda: self.add_driver(view_window, tree))
        btn_edit = ttk.Button(view_window, text="Редагувати", command=lambda: self.edit_driver(tree))
        btn_delete = ttk.Button(view_window, text="Видалити", command=lambda: self.delete_driver(tree))

        btn_add.pack(pady=10)
        btn_edit.pack(pady=10)
        btn_delete.pack(pady=10)

    def add_driver(self, view_window, tree):
        add_window = tk.Toplevel(self.root)
        add_window.title("Додати водія")

        # Створення полів для введення даних
        fields = ["Прізвище:", "Ім'я:", "Дата народження:", "Стаж:"]
        entry_vars = []
        for field in fields:
            frame = ttk.Frame(add_window)
            frame.pack(fill=tk.X, pady=5)
            label = ttk.Label(frame, text=field)
            label.pack(side=tk.LEFT)
            entry_var = tk.StringVar()
            entry = ttk.Entry(frame, textvariable=entry_var)
            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            entry_vars.append(entry_var)

        # Кнопка для збереження водія в базі даних
        ttk.Button(add_window, text="Зберегти", command=lambda: self.save_driver(entry_vars, add_window, tree)).pack(
            pady=10)

    def save_driver(self, entry_vars, add_window, tree):
        data = [var.get() for var in entry_vars]
        cursor = self.conn.cursor()
        cursor.execute('''
                INSERT INTO drivers (last_name, first_name, birthdate, experience)
                VALUES (?, ?, ?, ?)
            ''', data)
        self.conn.commit()

        # Оновлення таблиці
        self.load_data_into_table("drivers", tree)

        add_window.destroy()

    def edit_driver(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Попередження", "Будь ласка, виберіть водія для редагування.")
            return

        selected_item_id = tree.item(selected_item, "values")[0]

        # Отримання даних вибраного водія
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM drivers WHERE id=?', (selected_item_id,))
        driver_data = cursor.fetchone()

        # Створення вікна редагування
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редагувати водія")

        # Створення полів для введення даних
        fields = ["Прізвище:", "Ім'я:", "Дата народження:", "Стаж:"]
        entry_vars = []
        for field, value in zip(fields, driver_data[1:]):  # Починаємо з 1-го елемента, оскільки 0 - це ID
            frame = ttk.Frame(edit_window)
            frame.pack(fill=tk.X, pady=5)
            label = ttk.Label(frame, text=field)
            label.pack(side=tk.LEFT)
            entry_var = tk.StringVar(value=value)
            entry = ttk.Entry(frame, textvariable=entry_var)
            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            entry_vars.append(entry_var)

        # Кнопка для збереження змін водія
        ttk.Button(edit_window, text="Зберегти",
                   command=lambda: self.save_edited_driver(selected_item_id, entry_vars, edit_window, tree)).pack(
            pady=10)

    def delete_driver(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Попередження", "Будь ласка, виберіть водія для видалення.")
            return

        result = messagebox.askquestion("Підтвердження", "Ви впевнені, що хочете видалити вибраного водія?")
        if result == 'yes':
            selected_item_id = tree.item(selected_item, "values")[0]
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM drivers WHERE id=?", (selected_item_id,))
            self.conn.commit()
            tree.delete(selected_item)

            # Оновлення таблиці
            self.load_data_into_table("drivers", tree)

    def save_edited_driver(self, selected_item_id, entry_vars, edit_window, tree):
        data = [var.get() for var in entry_vars]
        cursor = self.conn.cursor()
        cursor.execute('''
                UPDATE drivers 
                SET last_name=?, first_name=?, birthdate=?, experience=?
                WHERE id=?
            ''', data + [selected_item_id])
        self.conn.commit()
        edit_window.destroy()

        # Оновлення таблиці
        self.load_data_into_table("drivers", tree)

    def view_cargo(self):
        view_window = tk.Toplevel(self.root)
        view_window.title("Вантаж")

        # Створення таблиці для виведення даних
        tree = ttk.Treeview(view_window, columns=(1, 2, 3, 4, 5, 6), show="headings", height=10)
        tree.pack()

        # Визначення назв стовбців
        tree.heading(1, text="ID")
        tree.heading(2, text="Вантажівка ID")
        tree.heading(3, text="Водій ID")
        tree.heading(4, text="Вантаж")
        tree.heading(5, text="Пункт відправлення")
        tree.heading(6, text="Пункт призначення")

        # Отримання даних з бази даних та виведення їх у таблицю
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM cargo')
        data = cursor.fetchall()
        for row in data:
            tree.insert('', 'end', values=row)

        # Додавання кнопок для додавання, редагування та видалення
        btn_add = ttk.Button(view_window, text="Додати вантаж", command=lambda: self.add_cargo(view_window, tree))
        btn_edit = ttk.Button(view_window, text="Редагувати", command=lambda: self.edit_cargo(tree))
        btn_delete = ttk.Button(view_window, text="Видалити", command=lambda: self.delete_cargo(tree))

        btn_add.pack(pady=10)
        btn_edit.pack(pady=10)
        btn_delete.pack(pady=10)

    def add_cargo(self, view_window, tree):
        add_window = tk.Toplevel(self.root)
        add_window.title("Додати вантаж")

        # Створення полів для введення даних
        fields = ["Вантажівка ID:", "Водій ID:", "Вантаж:", "Пункт відправлення:", "Пункт призначення:"]
        entry_vars = []
        for field in fields:
            frame = ttk.Frame(add_window)
            frame.pack(fill=tk.X, pady=5)
            label = ttk.Label(frame, text=field)
            label.pack(side=tk.LEFT)
            entry_var = tk.StringVar()
            entry = ttk.Entry(frame, textvariable=entry_var)
            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            entry_vars.append(entry_var)

        # Кнопка для збереження вантажу в базі даних
        ttk.Button(add_window, text="Зберегти", command=lambda: self.save_cargo(entry_vars, add_window, tree)).pack(
            pady=10)

    def save_cargo(self, entry_vars, add_window, tree):
        data = [var.get() for var in entry_vars]
        cursor = self.conn.cursor()
        cursor.execute('''
                INSERT INTO cargo (vehicle_id, driver_id, cargo_type, departure_point, destination_point)
                VALUES (?, ?, ?, ?, ?)
            ''', data)
        self.conn.commit()

        # Оновлення таблиці
        self.load_data_into_table("cargo", tree)

        add_window.destroy()

    def edit_cargo(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Попередження", "Будь ласка, виберіть вантаж для редагування.")
            return

        selected_item_id = tree.item(selected_item, "values")[0]

        # Отримання даних вибраного вантажу
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM cargo WHERE id=?', (selected_item_id,))
        cargo_data = cursor.fetchone()

        # Створення вікна редагування
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редагувати вантаж")

        # Створення полів для введення даних
        fields = ["Вантажівка ID:", "Водій ID:", "Вантаж:", "Пункт відправлення:", "Пункт призначення:"]
        entry_vars = []
        for field, value in zip(fields, cargo_data[1:]):  # Починаємо з 1-го елемента, оскільки 0 - це ID
            frame = ttk.Frame(edit_window)
            frame.pack(fill=tk.X, pady=5)
            label = ttk.Label(frame, text=field)
            label.pack(side=tk.LEFT)
            entry_var = tk.StringVar(value=value)
            entry = ttk.Entry(frame, textvariable=entry_var)
            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            entry_vars.append(entry_var)

        # Кнопка для збереження змін вантажу
        ttk.Button(edit_window, text="Зберегти",
                   command=lambda: self.save_edited_cargo(selected_item_id, entry_vars, edit_window, tree)).pack(
            pady=10)

    def delete_cargo(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Попередження", "Будь ласка, виберіть вантаж для видалення.")
            return

        result = messagebox.askquestion("Підтвердження", "Ви впевнені, що хочете видалити вибраний вантаж?")
        if result == 'yes':selected_item_id = tree.item(selected_item, "values")[0]
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM cargo WHERE id=?", (selected_item_id,))
        self.conn.commit()
        tree.delete(selected_item)

        # Оновлення таблиці
        self.load_data_into_table("cargo", tree)

    def save_edited_cargo(self, selected_item_id, entry_vars, edit_window, tree):
        data = [var.get() for var in entry_vars]
        cursor = self.conn.cursor()
        cursor.execute('''
                UPDATE cargo 
                SET vehicle_id=?, driver_id=?, cargo_type=?, departure_point=?, destination_point=?
                WHERE id=?
            ''', data + [selected_item_id])
        self.conn.commit()
        edit_window.destroy()

        # Оновлення таблиці
        self.load_data_into_table("cargo", tree)

    def load_data_into_table(self, table_name, tree):
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name}')
        data = cursor.fetchall()

        # Очистка таблиці
        for item in tree.get_children():
            tree.delete(item)

        # Заповнення таблиці новими даними
        for row in data:
            tree.insert('', 'end', values=row)

if __name__ == "__main__":
    root = tk.Tk()
    app = AuthenticationApp(root)
    root.mainloop()
