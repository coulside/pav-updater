
import customtkinter
import tkinter as tk
from tkinter import messagebox
import pyautogui
import pytesseract
from PIL import ImageGrab
import webbrowser  
import time
import threading
import json
import os
import pydirectinput
import tkinter.simpledialog
import re
import requests
import ctypes
import shutil
import sys
import datetime
import datetime
from dateutil.relativedelta import relativedelta


LICENSE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1pU57AFYw18ap9I1vSpvR2Z1-FJFz_Pos2MH_4K0_pZM/gviz/tq"
TG_URL = "https://t.me/kost2ya"
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
BG_COLOR = "#1e1e1e"         
SIDEBAR_COLOR = "#2a2a2a"    
MAIN_COLOR = "#252525"       
TEXT_COLOR = "#f0f0f0"      
SUBTEXT_COLOR = "#aaaaaa"    
ACCENT_COLOR = "#4CAF50"     
HOVER_COLOR = "#5FD469"
ERROR_COLOR = "#E74C3C"   
RECTANGLE_COLOR = "#E74C3C"   
BUTTON_COLOR = "#4CAF50"    
COORDINATES_FILE = "coordinates.json"


UPDATE_INFO_URL = "https://drive.google.com/uc?export=download&id=1LKblrIM0HpvZ4JLs_LvreBOwsMlT0mUw"
SCRIPT_PATH = os.path.abspath(sys.argv[0])  
CURRENT_VERSION = "1.0.0" 

def auto_update():
    try:
        print("Проверяю обновления...")

        response = requests.get(UPDATE_INFO_URL, timeout=10)
        if response.status_code != 200:
            print("Ошибка загрузки JSON об обновлении.")
            return

        data = json.loads(response.text)
        latest_version = data.get("latest")
        update_url = data.get("updateurl")

        if not latest_version or not update_url:
            print("Некорректный JSON. Нет полей 'latest' или 'updateurl'.")
            return

        if latest_version == CURRENT_VERSION:
            print(f"У вас актуальная версия ({CURRENT_VERSION}).")
            return

        print(f"Найдена новая версия: {latest_version}")
        messagebox.showinfo(
            "Обновление найдено",
            f"Доступна новая версия: {latest_version}\nТекущая: {CURRENT_VERSION}\nСкачиваю обновление..."
        )

        new_file_path = SCRIPT_PATH + ".new"
        r = requests.get(update_url, stream=True, timeout=20)
        total = int(r.headers.get("content-length", 0))
        downloaded = 0

        with open(new_file_path, "wb") as f:
            for chunk in r.iter_content(1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    percent = int(downloaded * 100 / total) if total else 0
                    sys.stdout.write(f"\rЗагрузка: {percent}%")
                    sys.stdout.flush()

        print("\nЗагрузка завершена!")

        backup_path = SCRIPT_PATH + ".bak"
        shutil.copyfile(SCRIPT_PATH, backup_path)
        print(f"Старая версия сохранена как {backup_path}")

        os.replace(new_file_path, SCRIPT_PATH)
        print("Обновление установлено!")

        messagebox.showinfo("Обновление завершено", "Программа будет перезапущена.")
        restart_script()

    except Exception as e:
        messagebox.showerror("Ошибка обновления", str(e))
        print("Ошибка автообновления:", e)

def restart_script():
    python = sys.executable
    os.execl(python, python, *sys.argv)
   

def get_disk_serial():
    serial_number = ctypes.c_ulong()
    ctypes.windll.kernel32.GetVolumeInformationW(
        ctypes.c_wchar_p("C:\\"),
        None,
        0,
        ctypes.byref(serial_number),
        None,
        None,
        None,
        0
    )
    return serial_number.value

def copy_to_clipboard(text):
    command = f'echo {text.strip()}| clip'
    os.system(command)

def check_license():
    serial = get_disk_serial()
    try:
        r = requests.get(LICENSE_SHEET_URL, timeout=10)
        if r.status_code != 200:
            raise Exception("Ошибка запроса к Google Sheets")

        match = re.search(r"google\.visualization\.Query\.setResponse\((.*)\);", r.text, re.DOTALL)
        if not match:
            raise Exception("Не удалось извлечь JSON из ответа")

        data = json.loads(match.group(1))
        rows = data.get("table", {}).get("rows", [])

        for row in rows:
            cells = row.get("c", [])
            sheet_serial = int(cells[0]["v"]) if len(cells) > 0 and cells[0] else None
            valid_days = int(cells[1]["v"]) if len(cells) > 1 and cells[1] else None
            start_date_str = cells[2]["v"] if len(cells) > 2 and cells[2] else None
            blocked = cells[3]["v"] if len(cells) > 3 and cells[3] else None

            if sheet_serial == serial:
                blocked_values = ["да", "+", "передача", "махинации"]  # все варианты блокировки
                if blocked and blocked.lower() in blocked_values:                
                    print("Лицензия заблокирована!")
                    messagebox.showerror(
                        "Лицензия заблокирована",
                        f"Лицензия заблокирована!\nПричина: {blocked}"
                    )
                    sys.exit()  
                
                if valid_days and start_date_str:
                    try:
                        match_date = re.match(r"Date\((\d{4}),(\d{1,2}),(\d{1,2})\)", start_date_str)
                        if match_date:
                            year = int(match_date.group(1))
                            month = int(match_date.group(2))
                            day = int(match_date.group(3))

                            start_date = datetime.date(year, month, day)
                            
                            valid_until_date = start_date + datetime.timedelta(days=valid_days)
                            print(f"Дата окончания лицензии: {valid_until_date.strftime('%d-%m-%Y')}")
                            
                            current_date_today = datetime.date.today()
                            if current_date_today > valid_until_date:
                                messagebox.showerror(
                                    "Лицензия истекла",
                                    f"Ваша лицензия истекла. Срок действия был до {valid_until_date.strftime('%d-%m-%Y')}.\nПожалуйста, обратитесь к владельцу приложения."
                                )
                                sys.exit()
                            return valid_until_date
                        else:
                            print(f"Не удалось распарсить дату: {start_date_str}")
                            return None
                    except ValueError as e:
                        print(f"Ошибка при парсинге даты: {start_date_str}. Ошибка: {e}")
                        return None
                else:
                    print("Количество дней или дата начала лицензии не указаны!")
                    return None

        root = tkinter.Tk()
        root.withdraw()
        result = messagebox.askokcancel(
            "Лицензия не найдена",
            f"Не обнаружена лицензия.\nВаш токен: {serial}\nПередайте его создателю: t.me/kost2ya\nНажмите OK чтобы скопировать токен."
        )
        if result:
            copy_to_clipboard(str(serial))
            webbrowser.open_new_tab(TG_URL)  
        sys.exit()

    except Exception as e:
        messagebox.showerror("Ошибка проверки лицензии", str(e))
        sys.exit()


class AutoPavilionApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        self.overrideredirect(True)
        self.attributes("-transparentcolor", "#2b2b2b")
        
        self.attributes("-topmost", True)

        self.title("Auto Pavilion — Modern Edition")
        self.geometry("740x460")
        
        self.configure(fg_color=BG_COLOR) 
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<B1-Motion>", self.do_move)

        self.is_running = False
        self.selecting_area = False
        self.red_box_coordinates = None
        self.status_text = tkinter.StringVar(value="\n\nСкрипт не запущен")
        
        self.cooldown_label_text = tkinter.StringVar(value="")
        self.delay_before_spam = 1.5
        self.initial_seconds = None
        self.cooldown_timer_active = False
        self.spam_thread = None

        self.license_expiry_date = check_license()

        self.sidebar = customtkinter.CTkFrame(self, width=180, corner_radius=15, fg_color="#333333")
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)

        self.logo_label = customtkinter.CTkLabel(
            self.sidebar, text=" Auto Pavilion", font=("Segoe UI", 18, "bold"), text_color="#FFFFFF"
        )
        self.logo_label.pack(pady=(30, 20))

        self.start_button = customtkinter.CTkButton(
            self.sidebar, text="▶ Запустить", command=self.toggle_script, corner_radius=10
        )
        self.start_button.pack(pady=10, padx=20, fill="x")
        
        self.select_button = customtkinter.CTkButton(
            self.sidebar, text=" Выбрать область", command=self.start_select_red_box, corner_radius=10
        )
        self.select_button.pack(pady=10, padx=20, fill="x")
        
        self.clear_coords_button = customtkinter.CTkButton(
            self.sidebar,
            text="Очистить координаты",
            command=self.clear_coordinates,
            fg_color="#a83232",
            corner_radius=10
        )
        self.clear_coords_button.pack(pady=(10, 20), padx=20, fill="x")

        self.link_label = customtkinter.CTkLabel(
            self.sidebar,
            text="Telegram\n",
            font=("Segoe UI", 12, "underline"),  
            text_color="#888",
        )
        self.link_label.pack(side="bottom", pady=20)
        
        self.link_label.bind("<Button-1>", self.open_telegram_link)
        
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=15, fg_color="#1c1c1c")
        self.main_frame.pack(side="right", expand=True, fill="both", padx=0, pady=0)

        self.title_label = customtkinter.CTkLabel(
            self.main_frame,
            text="",
            font=("Segoe UI", 22, "bold"),
            text_color="#FFFFFF"
        )
        self.title_label.pack(pady=(20, 10))
        
        if self.license_expiry_date:
            self.license_label = customtkinter.CTkLabel(
                self.main_frame,  
                text=f"Лицензия до: {self.license_expiry_date.strftime('%d-%m-%Y')}",
                font=("Segoe UI", 12),
                text_color="#FFFFFF"
            )
        else:
            self.license_label = customtkinter.CTkLabel(
                self.main_frame,  
                text="Лицензия не найдена",
                font=("Segoe UI", 12),
                text_color="#FF0000"
            )
        
       
        self.license_label.place(
            x=self.main_frame.winfo_width() - self.license_label.winfo_width() - -360,  
            y=10 
        )
        
        self.close_button = tk.Label(
            self,
            text="✖",
            font=("Segoe UI", 14, "bold"),
            bg="#1e1e1e",    
            fg="#ffffff",
            cursor="hand2"
        )
         
        self.update_idletasks()  
        self.close_button.place(
            x=self.winfo_width() - -500, 
            y=10,
            width=30,
            height=30
        )
        
        self.close_button.bind("<Enter>", lambda e: self.close_button.config(bg="#E74C3C"))
        self.close_button.bind("<Leave>", lambda e: self.close_button.config(bg="#aaaaaa"))
        
        self.close_button.bind("<Button-1>", lambda e: self.destroy())
        self.status_label = customtkinter.CTkLabel(
            self.main_frame,
            textvariable=self.status_text,
            font=("Segoe UI", 16),
        )
        self.status_label.pack(pady=(20, 10))

        self.cooldown_label = customtkinter.CTkLabel(
            self.main_frame, textvariable=self.cooldown_label_text,
            font=("Segoe UI", 14),
            text_color=ACCENT_COLOR,
        )
        self.cooldown_label.pack(pady=(0, 10))

        self.delay_label = customtkinter.CTkLabel(
            self.main_frame,
            text="Задержка перед флудом (1–4 сек):",
            font=("Segoe UI", 13),
            text_color="#FFFFFF"
        )
        self.delay_label.pack(pady=(5, 2))

        self.delay_entry = customtkinter.CTkEntry(self.main_frame, width=120)
        self.delay_entry.insert(0, str(self.delay_before_spam))
        self.delay_entry.bind("<B1-Motion>", lambda e: "break") 
        self.delay_entry.pack(pady=(0, 10))

        self.set_delay_button = customtkinter.CTkButton(
            self.main_frame, text="✅ Установить задержку", command=self.set_delay, height=40
        )
        self.set_delay_button.pack(pady=(0, 15))

        self.log_box = customtkinter.CTkTextbox(
            self.main_frame, width=420, height=220, corner_radius=15, fg_color="#2a2a2a"
        )
        self.log_box.pack(pady=10)
        self.log_box.insert("end", "Готов к работе...\n")
        self.log_box.configure(state="disabled")
        
        self.log_box.bind("<Button-1>", lambda e: "break")  
        self.log_box.bind("<B1-Motion>", lambda e: "break") 
        self.log_box.bind("<Key>", lambda e: "break")  
        self.log_box.bind("<FocusIn>", lambda e: self.focus())  

        self.rectangle_canvas = tkinter.Canvas(
            self.main_frame,
            width=520,
            height=140,
            bg="#0e1113",
            highlightthickness=1,
            highlightbackground="#333",
        )
        self.rectangle_canvas.pack(pady=(10, 10))
        
        self.load_coordinates() 
        self.draw_rectangle_preview() 
        
       
    def open_telegram_link(self, event):
        webbrowser.open(TG_URL)
        
    def add_to_log(self):
        self.log_box.config(state=tk.NORMAL)
        self.log_box.insert(tk.END, "Новое сообщение в лог\n")
        self.log_box.see(tk.END) 
        self.log_box.config(state=tk.DISABLED)        

    def on_close(self):
        if tkinter.simpledialog.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.is_running = False  
            self.destroy()     

    def toggle_script(self):
        if self.is_running:
            self.stop_script()
        else:
            self.start_script()

    def start_script(self):
        if not self.red_box_coordinates:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите область экрана!")
            return

        self.is_running = True
        self.status_text.set("\n\nСкрипт запущен ✅")
        self.start_button.configure(text="⏹ Остановить", fg_color=ACCENT_COLOR)
        self.log("Скрипт запущен...")
        threading.Thread(target=self.run_automation, daemon=True).start()

    def stop_script(self):
        self.is_running = False
        self.start_button.configure(text="▶ Запустить", fg_color="#3498db")
        self.status_text.set("\n\nСкрипт остановлен ❌")
        self.log("Работа остановлена пользователем")
        self.stop_spam()
        self.initial_seconds = None
        self.cooldown_timer_active = False
        self.update_cooldown_label("")

    def run_automation(self):
        while self.is_running:
            try:
                if not self.red_box_coordinates:
                    self.status_text.set("Ожидание выбора области...")
                    time.sleep(1)
                    continue

                x1, y1, x2, y2 = self.red_box_coordinates
                screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                time_text = pytesseract.image_to_string(screenshot, config='--psm 6', lang='rus').strip()

                self.log(f"{time_text}")

                match = re.search(r'(\d+(?:\.\d+)?)\s*сек', time_text)
                if match:
                    seconds = float(match.group(1))
                    if self.initial_seconds is None:
                        self.initial_seconds = seconds
                        self.start_timer_and_spam(seconds)
                        self.log(f"Обнаружено время: {seconds:.2f} сек")
                elif "Вы аренд" in time_text:
                    self.stop_spam()
                    self.stop_script()
                    self.status_text.set("Павильон арендован! 🏠")
                    self.log("Павильон арендован!")
                    self.initial_seconds = None
                    self.update_cooldown_label("Время вышло")

                time.sleep(0.3)

            except Exception as e:
                self.status_text.set(f"Ошибка: {e}")
                self.log(f"Ошибка: {e}")
                self.stop_script()

    def start_timer_and_spam(self, seconds):
        if self.cooldown_timer_active:return
        self.cooldown_timer_active = True
        threading.Thread(target=self.timer_and_spam, args=(seconds,), daemon=True).start()

    def timer_and_spam(self, seconds):
        start_time = time.time()
        time_to_spam = seconds - self.delay_before_spam
        if time_to_spam < 0:
            time_to_spam = 0

        while time.time() - start_time < time_to_spam and self.is_running:
            remaining_time = time_to_spam - (time.time() - start_time)
            self.update_cooldown_label(f"До слёта: {remaining_time:.1f} сек")
            time.sleep(0.1)

        if self.is_running:
            self.status_text.set("Время вышло!")
            start_spam_time = time.time()
            while time.time() - start_spam_time < 2 and self.is_running:
                self.spam_e_enter()
                time.sleep(0.1)

        self.stop_spam()
        self.cooldown_timer_active = False
        self.initial_seconds = None
        self.update_cooldown_label("Время вышло!")

    def spam_e_enter(self):
        try:
            pydirectinput.press("e")
            pydirectinput.press("enter")
            pydirectinput.PAUSE = 0.02
        except Exception as e:
            self.log(f"Ошибка во флуде: {e}")
            self.stop_spam()
            self.stop_script()

    def start_spam(self):
        self.spam_thread = threading.Thread(target=self.spam_e_enter, daemon=True)
        self.spam_thread.start()

    def stop_spam(self):
        if self.spam_thread and self.spam_thread.is_alive():
            self.spam_thread.join(timeout=0.5)
        self.spam_thread = None

    def start_select_red_box(self):
        self.create_overlay()

    def create_overlay(self): 
        self.selecting_area = True
        self.overlay = tkinter.Toplevel(self)
        self.overlay.attributes("-fullscreen", True)
        self.overlay.attributes("-alpha", 0.2)
        self.overlay.attributes("-topmost", True)
        self.overlay.overrideredirect(True)
    
        self.canvas = tkinter.Canvas(self.overlay, bg="white", highlightthickness=2, highlightbackground="black")
        self.canvas.pack(fill=tkinter.BOTH, expand=True)
    
        rgb = self.overlay.winfo_rgb('#000000')  
        hex_to_rgb = '#%02x%02x%02x' % (rgb[0] // 256, rgb[1] // 256, rgb[2] // 256)
    
        self.info_frame = tkinter.Frame(self.canvas, bg=hex_to_rgb)
        self.info_frame.place(relx=0.5, rely=0.5, anchor='center')  
    
        self.info_label = tkinter.Label(self.info_frame,
                                        text="Как выбрать область сканирования:\n1. Зажмите левую кнопку мыши\n2. Перетащите курсор, чтобы выбрать область\n3. Отпустите кнопку мыши для сохранения\n• Нажмите ESC для отмены",
                                        fg='white', bg=hex_to_rgb, justify='left', font=("Segoe UI", 12))
        self.info_label.pack(padx=20, pady=25)
    
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.overlay.bind("<Escape>", self.on_overlay_close)
    
        self.overlay.bind("<ButtonPress-1>", self.start_move_overlay)
        self.overlay.bind("<B1-Motion>", self.do_move_overlay)
    
   
    def start_move_overlay(self, event): 
        self.x = event.x_root
        self.y = event.y_root

    def do_move_overlay(self, event): 
        deltax = event.x_root - self.x
        deltay = event.y_root - self.y

        self.overlay.geometry(f'+{self.overlay.winfo_x() + deltax}+{self.overlay.winfo_y() + deltay}')

        self.x = event.x_root
        self.y = event.y_root

    def start_move(self, event):
        self.x = event.x_root
        self.y = event.y_root

    def do_move(self, event):
        deltax = event.x_root - self.x
        deltay = event.y_root - self.y

        self.geometry(f'+{self.winfo_x() + deltax}+{self.winfo_y() + deltay}')

        self.x = event.x_root
        self.y = event.y_root


    def on_press(self, event):
        if not self.selecting_area:
            return
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.selection_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline=RECTANGLE_COLOR, width=3
        )

    def on_drag(self, event): 
        if not self.selecting_area:
            return
        cur_x, cur_y = event.x_root, event.y_root
        self.canvas.coords(self.selection_rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event): 
        if not self.selecting_area:
            return
        end_x, end_y = event.x_root, event.y_root
        if abs(end_x - self.start_x) < 5 or abs(end_y - self.start_y) < 5:
            messagebox.showerror("Ошибка", "Слишком малая область!")
            self.on_overlay_close()
            return

        self.red_box_coordinates = (
            min(self.start_x, end_x),
            min(self.start_y, end_y),
            max(self.start_x, end_x),
            max(self.start_y, end_y),
        )
        self.save_coordinates()
        self.on_overlay_close()
        self.draw_rectangle_preview()
        self.log(f"Выбрана область: {self.red_box_coordinates}")

    def on_overlay_close(self, event=None):
        self.selecting_area = False
        if hasattr(self, "overlay") and self.overlay:
            self.overlay.destroy()
        self.overlay = None

    def load_coordinates(self):
        if os.path.exists(COORDINATES_FILE):
            try:
                with open(COORDINATES_FILE, "r") as f:
                    data = json.load(f)
                    self.red_box_coordinates = tuple(data.get("coordinates", []))
                    if self.red_box_coordinates:
                        print("Координаты загружены:", self.red_box_coordinates)
            except Exception as e:
                print(f"Ошибка загрузки координат: {e}")
                self.log(f"Ошибка загрузки координат: {e}") 

    def save_coordinates(self): 
        try:
            data = {"coordinates": list(self.red_box_coordinates)}
            with open(COORDINATES_FILE, "w") as f:
                json.dump(data, f)
            self.log("Координаты сохранены") 
        except Exception as e:
            self.log(f"Ошибка сохранения координат: {e}")

    def clear_coordinates(self): 
        self.red_box_coordinates = None
        #self.status_text.set("Координаты очищены.")
        self.log("Координаты очищены")
       # self.rectangle_canvas.delete("all")
        self.draw_rectangle_preview()
       # self.save_coordinates()

    def draw_rectangle_preview(self):
        try:
            self.rectangle_canvas.delete("all")
            if self.red_box_coordinates:
                x1, y1, x2, y2 = self.red_box_coordinates
                screen_w, screen_h = pyautogui.size()
                canvas_w = int(self.rectangle_canvas.winfo_width() or 520)
                canvas_h = int(self.rectangle_canvas.winfo_height() or 140)

                scale_x = canvas_w / screen_w
                scale_y = canvas_h / screen_h
                cx1, cy1 = int(x1 * scale_x), int(y1 * scale_y)
                cx2, cy2 = int(x2 * scale_x), int(y2 * scale_y)

                self.rectangle_canvas.create_rectangle(cx1, cy1, cx2, cy2, outline=RECTANGLE_COLOR, width=2)
        except Exception as e:
            self.log(f"Ошибка предпросмотра: {e}")

    def update_cooldown_label(self, text): 
        self.cooldown_label_text.set(text)

    def set_delay(self): 
        try:
            val = float(self.delay_entry.get())
            if 1 <= val < 4:
                self.delay_before_spam = val
                self.log(f"Задержка установлена: {val:.1f} сек")
            else:
                messagebox.showerror("Ошибка", "Введите значение от 1 до 4 сек.")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите число.")

    def log(self, text: str):
        self.log_box.configure(state="normal")     
        self.log_box.insert("end", f"{text}\n")    
        self.log_box.see("end")                  
        self.log_box.configure(state="disabled")
        
    def on_close(self):
        self.is_running = False
        self.destroy()
        
if __name__ == "__main__":
    root = tkinter.Tk()
    root.withdraw()
    auto_update()
    check_license()  
    root.destroy() 

    app = AutoPavilionApp()
    app.mainloop()
