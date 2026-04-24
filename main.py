import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор случайных паролей")
        self.history = []
        self.load_history()
        self.create_widgets()

    def create_widgets(self):
        # --- Настройки ---
        frame_settings = ttk.LabelFrame(self.root, text="Настройки пароля")
        frame_settings.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Длина пароля
        ttk.Label(frame_settings, text="Длина:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.length_var = tk.IntVar(value=12)
        self.length_slider = ttk.Scale(
            frame_settings,
            from_=4,
            to=32,
            variable=self.length_var,
            orient="horizontal"
        )
        self.length_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Чекбоксы символов
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_special = tk.BooleanVar(value=True)

        ttk.Checkbutton(frame_settings, text="Цифры", variable=self.use_digits).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(frame_settings, text="Буквы", variable=self.use_letters).grid(row=1, column=1, sticky="w")
        ttk.Checkbutton(frame_settings, text="Спецсимволы", variable=self.use_special).grid(row=1, column=2, sticky="w")

        # Кнопка генерации и поле вывода
        self.password_entry = ttk.Entry(self.root, width=40)
        self.password_entry.grid(row=1, column=0, padx=10, pady=5)
        
        ttk.Button(self.root, text="Сгенерировать", command=self.generate_password).grid(row=2, column=0, pady=5)

        # --- История ---
        frame_history = ttk.LabelFrame(self.root, text="История генераций")
        frame_history.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        
        self.tree = ttk.Treeview(frame_history, columns=("password", "length", "options"), show="headings")
        self.tree.heading("password", text="Пароль")
        self.tree.heading("length", text="Длина")
        self.tree.heading("options", text="Набор символов")
        
        self.tree.pack(fill="both", expand=True)
        
        self.update_history_view()

    def generate_password(self):
        length = self.length_var.get()
        
        # Проверка: хотя бы один тип символов должен быть выбран
        if not (self.use_digits.get() or self.use_letters.get() or self.use_special.get()):
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов!")
            return

        # Проверка длины (уже ограничено ползунком, но на всякий случай)
        if length < 4 or length > 32:
            messagebox.showerror("Ошибка", "Длина должна быть от 4 до 32 символов.")
            return

        chars = ""
        if self.use_digits.get():
            chars += string.digits
        if self.use_letters.get():
            chars += string.ascii_letters  # a-zA-Z
        if self.use_special.get():
            chars += string.punctuation

        password = ''.join(random.choices(chars, k=length))
        
        # Сохранение в историю и отображение
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)
        
        options_str = f"Цифры: {self.use_digits.get()}, Буквы: {self.use_letters.get()}, Спецсимволы: {self.use_special.get()}"
        
        self.history.append({
            "password": password,
            "length": length,
            "options": options_str,
            "timestamp": random.randint(1, 99999) # Для уникальности при сортировке (просто пример)
        })
        
        self.save_history()
        self.update_history_view()

    def save_history(self):
        with open('history.json', 'w', encoding='utf-8') as f:
            json.dump(self.history[-10:], f, ensure_ascii=False) # Сохраняем только последние 10 паролей

    def load_history(self):
        try:
            with open('history.json', 'r', encoding='utf-8') as f:
                self.history = json.load(f)
                if not isinstance(self.history, list):
                    self.history = []
                # Обновляем чекбоксы на основе последнего сгенерированного пароля (если есть)
                if self.history:
                    last = self.history[-1]
                    # Простая логика восстановления опций (можно улучшить)
                    self.use_digits.set("Цифры: True" in last["options"])
                    self.use_letters.set("Буквы: True" in last["options"])
                    self.use_special.set("Спецсимволы: True" in last["options"])
                    self.length_var.set(last["length"])
                    self.password_entry.delete(0, tk.END)
                    self.password_entry.insert(0, last["password"])
                                  return True
        except FileNotFoundError:
            return False
    def update_history_view(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        for item in reversed(self.history): # Показываем свежие сверху
            self.tree.insert("", "end", values=(item["password"], item["length"], item["options"]))


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()
