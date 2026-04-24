import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Дневник погоды")
        self.root.geometry("800x500")

        # Основной контейнер для всех виджетов
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Список для хранения записей (в памяти)
        self.records = []
        self.displayed_records = []  # Для отображения с учетом фильтров

        # --- Создание виджетов ---
        self.create_widgets()

    def create_widgets(self):
        # 1. Фрейм ввода данных (Входные поля)
        input_frame = ttk.LabelFrame(self.main_frame, text="Добавить новую запись", padding="5")
        input_frame.grid(row=0, column=0, sticky="ew", pady=5)

        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        # Температура
        ttk.Label(input_frame, text="Температура (°C):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.temp_entry = ttk.Entry(input_frame, width=15)
        self.temp_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        # Описание
        ttk.Label(input_frame, text="Описание:").grid(row=2, column=0, sticky="nw", padx=5, pady=2)
        self.desc_entry = tk.Text(input_frame, height=3, width=20)
        self.desc_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        # Осадки (Чекбокс)
        self.rain_var = tk.BooleanVar()
        ttk.Checkbutton(input_frame, text="Осадки", variable=self.rain_var).grid(row=3, column=0, columnspan=2, pady=5)

        # Кнопка "Добавить"
        ttk.Button(input_frame, text="Добавить запись", command=self.add_record).grid(row=4, column=0, columnspan=2, pady=10)


        # 2. Фрейм фильтрации и управления файлами
        control_frame = ttk.Frame(self.main_frame)
        control_frame.grid(row=1, column=0, sticky="ew", pady=5)

        # Фильтр по дате
        ttk.Label(control_frame, text="Фильтр по дате:").grid(row=0, column=0, padx=5)
        self.filter_date_entry = ttk.Entry(control_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5)
        
        # Фильтр по температуре (выше чем)
        ttk.Label(control_frame, text="Температура >").grid(row=0, column=2, padx=5)
        self.filter_temp_entry = ttk.Entry(control_frame, width=8)
        self.filter_temp_entry.grid(row=0, column=3, padx=5)
        
        # Кнопка "Применить фильтр"
        ttk.Button(control_frame, text="Фильтровать", command=self.apply_filter).grid(row=0, column=4, padx=5)
        
        # Кнопка "Очистить фильтр"
        ttk.Button(control_frame, text="Очистить фильтр", command=self.clear_filter).grid(row=0, column=5, padx=5)


        # Кнопки управления файлами JSON
        file_frame = ttk.Frame(self.main_frame)
        file_frame.grid(row=2, column=0, sticky="ew", pady=5)

        ttk.Button(file_frame, text="Сохранить в JSON", command=self.save_to_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Загрузить из JSON", command=self.load_from_json).pack(side=tk.LEFT, padx=5)


        # 3. Таблица для отображения записей (Treeview)
        columns = ("date", "temp", "desc", "rain")
        
        self.tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        
        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("rain", text="Осадки")
        
        self.tree.column("date", width=120)
        self.tree.column("temp", width=100)
        self.tree.column("desc", width=350)
        self.tree.column("rain", width=80)
        
        # Полосы прокрутки
        yscroll = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        xscroll = ttk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscroll=yscroll.set, xscroll=xscroll.set)
        
        self.tree.grid(row=3, column=0, sticky="nsew")
        yscroll.grid(row=3, column=1, sticky="ns")
        xscroll.grid(row=4, column=0, sticky="ew")

        # Настройка сетки для изменения размеров окна
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)


    # --- Логика приложения ---

    def add_record(self):
        """Добавляет новую запись после валидации."""
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        desc = self.desc_entry.get("1.0", tk.END).strip()

        # Валидация даты
        try:
            datetime.strptime(date, '%Y-%m-%d')
            if not date:
                raise ValueError("Поле не должно быть пустым")
            for rec in self.records:
                if rec['date'] == date:
                    raise ValueError("Запись на эту дату уже существует")
            valid_date = date
        except ValueError as e:
            messagebox.showerror("Ошибка даты", str(e) or "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return

        # Валидация температуры
        try:
            if not temp:
                raise ValueError("Поле не должно быть пустым")
            valid_temp = float(temp)
            if valid_temp < -100 or valid_temp > 100: # Здравый смысл
                raise ValueError("Температура вне диапазона -100..100 °C")
            valid_temp = round(valid_temp, 1) # Округляем до 1 знака
            temp = str(valid_temp) # Обновляем отображение в поле ввода
            self.temp_entry.delete(0, tk.END)
            self.temp_entry.insert(0, temp)
            
            if valid_temp > 45 or valid_temp < -45:
                messagebox.showwarning("Экстремальная температура!", f"Температура {valid_temp}°C выходит за пределы нормы.")
                
            if valid_temp > 37:
                messagebox.showinfo("Тепло!", "Сегодня жарковато!")
                
            if valid_temp < 0:
                messagebox.showinfo("Холодно!", "Не забудьте шапку!")
