import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Файл для хранения данных
        self.data_file = "trainings.json"
        
        # Список тренировок
        self.trainings = []
        
        # Загрузка данных из файла
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление таблицы
        self.refresh_table()
    
    def create_widgets(self):
        # Фрейм для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавление тренировки", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Поле для даты
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Поле для типа тренировки
        ttk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.type_entry = ttk.Combobox(input_frame, values=["Бег", "Плавание", "Велоспорт", "Силовая", "Йога", "Другое"], width=20)
        self.type_entry.grid(row=0, column=3, padx=5, pady=5)
        self.type_entry.set("Бег")
        
        # Поле для длительности
        ttk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        self.duration_entry = ttk.Entry(input_frame, width=15)
        self.duration_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопка добавления
        self.add_btn = ttk.Button(input_frame, text="Добавить тренировку", command=self.add_training)
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Фильтр по типу
        ttk.Label(filter_frame, text="Фильтр по типу:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.filter_type = ttk.Combobox(filter_frame, values=["Все", "Бег", "Плавание", "Велоспорт", "Силовая", "Йога", "Другое"], width=20)
        self.filter_type.grid(row=0, column=1, padx=5, pady=5)
        self.filter_type.set("Все")
        self.filter_type.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())
        
        # Фильтр по дате
        ttk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.filter_date = ttk.Entry(filter_frame, width=20)
        self.filter_date.grid(row=0, column=3, padx=5, pady=5)
        
        # Кнопки для фильтрации
        self.apply_filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.refresh_table)
        self.apply_filter_btn.grid(row=0, column=4, padx=5, pady=5)
        
        self.reset_filter_btn = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filters)
        self.reset_filter_btn.grid(row=0, column=5, padx=5, pady=5)
        
        # Таблица для отображения тренировок
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Создание таблицы
        columns = ("date", "type", "duration")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Настройка колонок
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип тренировки")
        self.tree.heading("duration", text="Длительность (мин)")
        
        self.tree.column("date", width=150)
        self.tree.column("type", width=200)
        self.tree.column("duration", width=150)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.delete_btn = ttk.Button(control_frame, text="Удалить выбранную", command=self.delete_training)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_btn = ttk.Button(control_frame, text="Редактировать выбранную", command=self.edit_training)
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(control_frame, text="Сохранить в JSON", command=self.save_data)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # Статус бар
        self.status_bar = ttk.Label(self.root, text="Готов", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def validate_date(self, date_string):
        """Проверка корректности формата даты"""
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def validate_duration(self, duration_string):
        """Проверка корректности длительности"""
        try:
            duration = float(duration_string)
            return duration > 0
        except ValueError:
            return False
    
    def add_training(self):
        """Добавление новой тренировки"""
        date = self.date_entry.get().strip()
        training_type = self.type_entry.get().strip()
        duration = self.duration_entry.get().strip()
        
        # Проверка ввода
        if not date:
            messagebox.showerror("Ошибка", "Введите дату!")
            return
        
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return
        
        if not training_type:
            messagebox.showerror("Ошибка", "Введите тип тренировки!")
            return
        
        if not duration:
            messagebox.showerror("Ошибка", "Введите длительность!")
            return
        
        if not self.validate_duration(duration):
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!")
            return
        
        # Добавление тренировки
        training = {
            "date": date,
            "type": training_type,
            "duration": float(duration)
        }
        
        self.trainings.append(training)
        self.save_data()
        self.refresh_table()
        
        # Очистка поля длительности
        self.duration_entry.delete(0, tk.END)
        
        self.status_bar.config(text=f"Добавлена тренировка: {date} - {training_type} - {duration} мин")
    
    def delete_training(self):
        """Удаление выбранной тренировки"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для удаления!")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту тренировку?"):
            # Получение индекса выбранной записи
            item = self.tree.item(selected[0])
            values = item['values']
            
            # Поиск и удаление тренировки
            for i, training in enumerate(self.trainings):
                if (training['date'] == values[0] and 
                    training['type'] == values[1] and 
                    training['duration'] == values[2]):
                    del self.trainings[i]
                    break
            
            self.save_data()
            self.refresh_table()
            self.status_bar.config(text="Тренировка удалена")
    
    def edit_training(self):
        """Редактирование выбранной тренировки"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для редактирования!")
            return
        
        # Получение данных выбранной тренировки
        item = self.tree.item(selected[0])
        values = item['values']
        
        # Создание окна редактирования
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактирование тренировки")
        edit_window.geometry("400x250")
        edit_window.resizable(False, False)
        
        # Поля для редактирования
        ttk.Label(edit_window, text="Дата (ГГГГ-ММ-ДД):").pack(pady=5)
        date_entry = ttk.Entry(edit_window, width=30)
        date_entry.insert(0, values[0])
        date_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Тип тренировки:").pack(pady=5)
        type_entry = ttk.Combobox(edit_window, values=["Бег", "Плавание", "Велоспорт", "Силовая", "Йога", "Другое"], width=27)
        type_entry.set(values[1])
        type_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Длительность (мин):").pack(pady=5)
        duration_entry = ttk.Entry(edit_window, width=30)
        duration_entry.insert(0, values[2])
        duration_entry.pack(pady=5)
        
        def save_edit():
            new_date = date_entry.get().strip()
            new_type = type_entry.get().strip()
            new_duration = duration_entry.get().strip()
            
            # Проверка ввода
            if not new_date or not self.validate_date(new_date):
                messagebox.showerror("Ошибка", "Неверный формат даты!")
                return
            
            if not new_type:
                messagebox.showerror("Ошибка", "Введите тип тренировки!")
                return
            
            if not new_duration or not self.validate_duration(new_duration):
                messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!")
                return
            
            # Обновление данных
            for training in self.trainings:
                if (training['date'] == values[0] and 
                    training['type'] == values[1] and 
                    training['duration'] == values[2]):
                    training['date'] = new_date
                    training['type'] = new_type
                    training['duration'] = float(new_duration)
                    break
            
            self.save_data()
            self.refresh_table()
            edit_window.destroy()
            self.status_bar.config(text="Тренировка обновлена")
        
        ttk.Button(edit_window, text="Сохранить", command=save_edit).pack(pady=10)
    
    def refresh_table(self):
        """Обновление таблицы с учетом фильтров"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Применение фильтров
        filtered_trainings = self.trainings.copy()
        
        # Фильтр по типу
        filter_type_value = self.filter_type.get()
        if filter_type_value != "Все":
            filtered_trainings = [t for t in filtered_trainings if t['type'] == filter_type_value]
        
        # Фильтр по дате
        filter_date_value = self.filter_date.get().strip()
        if filter_date_value:
            if self.validate_date(filter_date_value):
                filtered_trainings = [t for t in filtered_trainings if t['date'] == filter_date_value]
            elif filter_date_value:
                messagebox.showwarning("Предупреждение", "Неверный формат даты в фильтре!")
        
        # Сортировка по дате
        filtered_trainings.sort(key=lambda x: x['date'])
        
        # Добавление в таблицу
        for training in filtered_trainings:
            self.tree.insert("", tk.END, values=(
                training['date'],
                training['type'],
                training['duration']
            ))
        
        self.status_bar.config(text=f"Показано тренировок: {len(filtered_trainings)} из {len(self.trainings)}")
    
    def reset_filters(self):
        """Сброс фильтров"""
        self.filter_type.set("Все")
        self.filter_date.delete(0, tk.END)
        self.refresh_table()
    
    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.trainings = json.load(f)
                self.status_bar.config(text=f"Загружено {len(self.trainings)} тренировок")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки данных: {str(e)}")
                self.trainings = []
        else:
            # Создание файла с примером данных
            self.trainings = [
                {"date": "2024-01-15", "type": "Бег", "duration": 30},
                {"date": "2024-01-16", "type": "Плавание", "duration": 45},
                {"date": "2024-01-17", "type": "Силовая", "duration": 60}
            ]
            self.save_data()
    
    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения данных: {str(e)}")
            return False

def main():
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()