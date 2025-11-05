
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, font as tkfont
import pyautogui
import pytesseract
from PIL import Image, ImageTk, ImageGrab
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
from dateutil.relativedelta import relativedelta
import subprocess


LICENSE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1pU57AFYw18ap9I1vSpvR2Z1-FJFz_Pos2MH_4K0_pZM/gviz/tq"
TG_URL = "https://t.me/kost2ya"
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
BG_COLOR = "#0f0f0f"         
SIDEBAR_COLOR = "#1a1a1a"    
MAIN_COLOR = "#151515"       
TEXT_COLOR = "#ffffff"      
SUBTEXT_COLOR = "#b0b0b0"    
ACCENT_COLOR = "#00d4ff"     
HOVER_COLOR = "#00b8e6"
ERROR_COLOR = "#ff4757"   
RECTANGLE_COLOR = "#00d4ff"   
BUTTON_COLOR = "#00d4ff"    
COORDINATES_FILE = "coordinates.json"
sidebar_bg = "#1a1a1a"
border_color = "#00d4ff"
inner_bg = sidebar_bg
SECONDARY_COLOR = "#2a2a2a"
CARD_COLOR = "#1f1f1f"
INPUT_BG = "#0a0a0a"
INPUT_BORDER = "#3a3a3a"
BUTTON_PRIMARY = "#0099b8"
BUTTON_PRIMARY_HOVER = "#007a99"

UPDATE_INFO_URL = "https://drive.google.com/uc?export=download&id=1LKblrIM0HpvZ4JLs_LvreBOwsMlT0mUw"
SCRIPT_PATH = os.path.abspath(sys.argv[0])  
CURRENT_VERSION = "0.0.1" 

FONT_URL = "https://dl.dropboxusercontent.com/s/zgfq5juurf7yvru/fAwesome5.tt-f"
FONT_DIR = os.path.join(os.path.dirname(__file__), "resource", "fonts")
FONT_PATH = os.path.join(FONT_DIR, "fAwesome5.ttf")

def ensure_fa_font():
    os.makedirs(FONT_DIR, exist_ok=True)
    if not os.path.exists(FONT_PATH):
        print("Шрифт не найден. Скачиваю...")
        try:
            r = requests.get(FONT_URL, stream=True, timeout=15)
            r.raise_for_status()
            with open(FONT_PATH, "wb") as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            print("Шрифт успешно скачан!")
        except Exception as e:
            print(f"Ошибка при скачивании шрифта: {e}")
            return False
    try:
        ctypes.windll.gdi32.AddFontResourceW(FONT_PATH)
        print("fAwesome5.ttf зарегистрирован в системе")
        return True
    except Exception as e:
        print(f"Не удалось зарегистрировать шрифт: {e}")
        return False

ensure_fa_font()

def sf_font(size=14, weight="bold"):
    try:
        return ("fAwesome5", size, weight)
    except:
        return ("Segoe UI", size, weight)
        
from PIL import Image, ImageDraw, ImageTk

def round_corners(image, radius):
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)
    result = image.copy()
    result.putalpha(mask)
    return result

def show_custom_message(title: str, message: str, image_path: str = None, msg_type: str = "info"):
    msg_win = ctk.CTkToplevel()
    msg_win.title(title)
    msg_win.overrideredirect(True)
    msg_win.attributes("-topmost", True)
    TRANSPARENT_COLOR = "#2b2b2b"
    msg_win.attributes("-transparentcolor", TRANSPARENT_COLOR)
    msg_win.configure(fg_color=TRANSPARENT_COLOR)

    type_colors = {
        "info": {"bg": CARD_COLOR, "accent": ACCENT_COLOR, "icon": "ℹ️"},
        "error": {"bg": "#2a1a1a", "accent": ERROR_COLOR, "icon": "❌"},
        "warning": {"bg": "#2a281a", "accent": "#ffa500", "icon": "⚠️"},
        "success": {"bg": "#1a2a1a", "accent": "#00ff88", "icon": "✅"}
    }
    colors = type_colors.get(msg_type, type_colors["info"])

    window_width = 500
    window_height = 280
    screen_width = msg_win.winfo_screenwidth()
    screen_height = msg_win.winfo_screenheight()
    x = int((screen_width - window_width) / 2)
    y = int((screen_height - window_height) / 2)
    msg_win.geometry(f"{window_width}x{window_height}+{x}+{y}")

    main_container = ctk.CTkFrame(msg_win, fg_color=colors["bg"], corner_radius=15, border_width=2, border_color=colors["accent"])
    main_container.pack(fill="both", expand=True, padx=0, pady=0)

    header_frame = ctk.CTkFrame(main_container, fg_color="transparent", corner_radius=0)
    header_frame.pack(fill="x", padx=15, pady=(15, 10))

    title_label = ctk.CTkLabel(
        header_frame,
        text=f"{colors['icon']} {title}",
        font=("Segoe UI", 20, "bold"),
        text_color=TEXT_COLOR,
        anchor="w"
    )
    title_label.pack(side="left", fill="x", expand=True)

    close_btn = tk.Label(
        header_frame,
        text="✕",
        font=("Segoe UI", 18, "bold"),
        bg=colors["bg"],
        fg=SUBTEXT_COLOR,
        cursor="hand2",
        width=2,
        height=1
    )
    close_btn.pack(side="right")
    close_btn.bind("<Enter>", lambda e: close_btn.config(fg=ERROR_COLOR, bg=colors["bg"]))
    close_btn.bind("<Leave>", lambda e: close_btn.config(fg=SUBTEXT_COLOR, bg=colors["bg"]))
    close_btn.bind("<Button-1>", lambda e: msg_win.destroy())

    content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
    content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    if image_path and os.path.exists(image_path):
        icon_frame = ctk.CTkFrame(content_frame, fg_color="transparent", width=100)
        icon_frame.pack(side="left", padx=(0, 15))
        
        img = Image.open(image_path)
        img = img.resize((100, 100))
        img = round_corners(img, radius=15)
        img = ImageTk.PhotoImage(img)
        
        label_img = ctk.CTkLabel(icon_frame, image=img, text="")
        label_img.image = img
        label_img.pack(pady=10)
    else:
        icon_frame = ctk.CTkFrame(content_frame, fg_color="transparent", width=100)
        icon_frame.pack(side="left", padx=(0, 15))
        icon_label = ctk.CTkLabel(
            icon_frame,
            text=colors["icon"],
            font=("Segoe UI", 50),
            text_color=colors["accent"]
        )
        icon_label.pack(pady=10)

    text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    text_frame.pack(side="right", fill="both", expand=True)

    date_pattern = r'(\d{2}-\d{2}-\d{4})'
    if re.search(date_pattern, message):
        text_box = ctk.CTkTextbox(
            text_frame,
            width=320,
            height=120,
            wrap="word",
            fg_color="transparent",
            border_width=0,
            font=("Segoe UI", 14),
            text_color=TEXT_COLOR
        )
        text_box.pack(fill="both", expand=True, pady=10)

        parts = re.split(date_pattern, message)
        for part in parts:
            if re.match(date_pattern, part):
                start_pos = text_box.index("end-1c")
                text_box.insert("end", part)
                end_pos = text_box.index("end-1c")
                internal_text = text_box._textbox
                internal_text.tag_add("underlined", start_pos, end_pos)
                internal_text.tag_config("underlined", underline=True, foreground=colors["accent"])
            else:
                text_box.insert("end", part)
        
        text_box.configure(state="disabled")
        text_box.bind("<Button-1>", lambda e: "break")
        text_box.bind("<B1-Motion>", lambda e: "break")
        text_box.bind("<Key>", lambda e: "break")
    else:
        text_label = ctk.CTkLabel(
            text_frame,
            text=message,
            wraplength=320,
            justify="left",
            font=("Segoe UI", 14),
            text_color=TEXT_COLOR,
            anchor="nw"
        )
        text_label.pack(fill="both", expand=True, pady=10)

    button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
    button_frame.pack(fill="x", padx=15, pady=(0, 15))

    ok_btn = ctk.CTkButton(
        button_frame,
        text="OK",
        fg_color=colors["accent"],
        hover_color=HOVER_COLOR if msg_type == "info" else colors["accent"],
        text_color="white",
        corner_radius=10,
        width=150,
        height=40,
        font=("Segoe UI", 14, "bold"),
        border_width=0,
        command=msg_win.destroy
    )
    ok_btn.pack()

    msg_win.grab_set()
    msg_win.focus_set()

    msg_win.bind("<Escape>", lambda e: msg_win.destroy())

    msg_win.update()
    msg_win.deiconify()

    msg_win.wait_window()
    
    return msg_win
    
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
        show_custom_message(
            title="Обновление найдено",
            message=f"\n\nДоступна новая версия: {latest_version}\nТекущая: {CURRENT_VERSION}.",
            msg_type="success"
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

        #messagebox.showinfo("Обновление завершено", "Программа будет перезапущена.")
        restart_script()
       
    except Exception as e:
        show_custom_message(
            title="Ошибка обновления",
            message=f"Произошла ошибка во время проверки или загрузки обновления:\n\n{str(e)}",
            msg_type="error"
        )
        webbrowser.open_new_tab(TG_URL)
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

def check_and_close_extreme_injector():
    process_names_variants = [
        "Extreme Injector",
        "ExtremeInjector",
        "extreme injector",
        "extremeinjector"
        "Injector"
    ]
    
    found_processes = []
    
    try:
        result = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            timeout=5,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                line_lower = line.lower()
                for variant in process_names_variants:
                    if variant.lower() in line_lower:
                        try:
                            parts = line.split('","')
                            if len(parts) > 0:
                                proc = parts[0].strip('"')
                                proc_base = proc.replace('.exe', '').replace('.EXE', '')
                                if proc_base and proc_base not in [p.replace('.exe', '').replace('.EXE', '') for p in found_processes]:
                                    found_processes.append(proc)
                                    break 
                        except:
                            continue
    except Exception as e:
        print(f"Ошибка при проверке процессов: {e}")
        show_custom_message(
            title="Предупреждение",
            message="Не удалось проверить запущенные процессы.\nУбедитесь, что Extreme Injector закрыт!",
            msg_type="warning"
        )
        return
    
    if not found_processes:
        return 
    
    closed_count = 0
    failed_processes = []
    
    for proc_name in found_processes:
        try:
            result = subprocess.run(
                ["taskkill", "/F", "/IM", proc_name],
                capture_output=True,
                text=True,
                timeout=5,
                encoding='utf-8',
                errors='ignore'
            )
            if result.returncode == 0:
                closed_count += 1
            else:
                failed_processes.append(proc_name)
        except Exception as e:
            print(f"Ошибка при закрытии процесса {proc_name}: {e}")
            failed_processes.append(proc_name)
    
    if closed_count < len(found_processes):
        failed_list = ", ".join(failed_processes) if failed_processes else "неизвестный процесс"
        show_custom_message(
            title="Критическая ошибка",
            message=f"Обнаружен запущенный Extreme Injector!\n\nПроцесс: {failed_list}\n\nНе удалось автоматически закрыть процесс.\nПожалуйста, закройте Extreme Injector вручную и перезапустите программу.\n\nВ противном случае Ваша подписка будет деактивирована!",
            msg_type="error"
        )
        webbrowser.open_new_tab(TG_URL)
        sys.exit()
    else:
        show_custom_message(
            title="Внимание",
            message="Обнаружен запущенный Extreme Injector.\n\nПроцесс был автоматически закрыт.\n\nПри повторном использовании - Ваша подписка будет деактивирована!",
            msg_type="warning"
        )

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
                blocked_values = ["да", "+", "передача", "махинации"] 
                if blocked and blocked.lower() in blocked_values:                
                    print("Лицензия заблокирована!")
                    show_custom_message(
                        title="Блокировка лицензии",
                        message=f"Лицензия заблокирована!\nПричина: {blocked}",
                        msg_type="error"
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
                                show_custom_message(
                                    title="Лицензия истекла",
                                    message=f"Ваша лицензия истекла. Срок действия был до {valid_until_date.strftime('%d-%m-%Y')}.\nПожалуйста, обратитесь к владельцу приложения.",
                                    msg_type="error"
                                )    
                                webbrowser.open_new_tab(TG_URL)
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

        def show_license_not_found():
            root = tk.Tk()
            root.withdraw()
            result_var = [False]
            
            def on_ok():
                copy_to_clipboard(str(serial))
                webbrowser.open_new_tab(TG_URL)
                result_var[0] = True
                msg_win.destroy()
            
            msg_win = ctk.CTkToplevel()
            msg_win.title("Лицензия не найдена")
            msg_win.overrideredirect(True)
            msg_win.attributes("-topmost", True)
            TRANSPARENT_COLOR = "#2b2b2b"
            msg_win.attributes("-transparentcolor", TRANSPARENT_COLOR)
            msg_win.configure(fg_color=TRANSPARENT_COLOR)
            
            window_width = 500
            window_height = 320
            screen_width = msg_win.winfo_screenwidth()
            screen_height = msg_win.winfo_screenheight()
            x = int((screen_width - window_width) / 2)
            y = int((screen_height - window_height) / 2)
            msg_win.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            main_container = ctk.CTkFrame(msg_win, fg_color=CARD_COLOR, corner_radius=15, border_width=2, border_color=ERROR_COLOR)
            main_container.pack(fill="both", expand=True, padx=0, pady=0)
            
            header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
            header_frame.pack(fill="x", padx=15, pady=(15, 10))
            
            title_label = ctk.CTkLabel(header_frame, text="❌ Лицензия не найдена", font=("Segoe UI", 20, "bold"), text_color=TEXT_COLOR, anchor="w")
            title_label.pack(side="left", fill="x", expand=True)
            
            close_btn = tk.Label(header_frame, text="✕", font=("Segoe UI", 18, "bold"), bg=CARD_COLOR, fg=SUBTEXT_COLOR, cursor="hand2", width=2, height=1)
            close_btn.pack(side="right")
            close_btn.bind("<Enter>", lambda e: close_btn.config(fg=ERROR_COLOR))
            close_btn.bind("<Leave>", lambda e: close_btn.config(fg=SUBTEXT_COLOR))
            close_btn.bind("<Button-1>", lambda e: msg_win.destroy())
            
            content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
            
            icon_label = ctk.CTkLabel(content_frame, text="❌", font=("Segoe UI", 50), text_color=ERROR_COLOR)
            icon_label.pack(side="left", padx=(0, 15))
            
            text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            text_frame.pack(side="right", fill="both", expand=True)
            
            text_label = ctk.CTkLabel(text_frame, text=f"\nВаш токен: {serial}\nНажмите OK чтобы скопировать токен и передайте его разработчику.", wraplength=320, justify="left", font=("Segoe UI", 14), text_color=TEXT_COLOR, anchor="nw")
            webbrowser.open_new_tab(TG_URL)
            text_label.pack(fill="both", expand=True, pady=10)
            
            button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
            button_frame.pack(fill="x", padx=15, pady=(0, 15))
            
            btn_frame_inner = ctk.CTkFrame(button_frame, fg_color="transparent")
            btn_frame_inner.pack()
            
            ok_btn = ctk.CTkButton(btn_frame_inner, text="OK", command=on_ok, fg_color=ACCENT_COLOR, hover_color=HOVER_COLOR, text_color="white", corner_radius=10, width=120, height=40, font=("Segoe UI", 14, "bold"))
            ok_btn.pack(side="left", padx=5)
            
            cancel_btn = ctk.CTkButton(btn_frame_inner, text="Отмена", command=msg_win.destroy, fg_color=SECONDARY_COLOR, hover_color="#3a3a3a", text_color=TEXT_COLOR, corner_radius=10, width=120, height=40, font=("Segoe UI", 14, "bold"))
            cancel_btn.pack(side="left", padx=5)
            
            msg_win.grab_set()
            msg_win.focus_set()
            msg_win.bind("<Escape>", lambda e: msg_win.destroy())
            msg_win.wait_window()
            root.destroy()
            return result_var[0]
        
        result = show_license_not_found()
        sys.exit()

    except Exception as e:
        show_custom_message(
            title="Ошибка",
            message=f"Произошла ошибка во время проверки лицензии\n\n{str(e)}",
            msg_type="error"
        )
        sys.exit()


class AutoPavilionApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.overrideredirect(True)
        self.attributes("-transparentcolor", "#2b2b2b")
        self.attributes("-topmost", True)

        self.title("Auto Pavilion — Modern Edition")
        self.geometry("740x520")

        self.configure(fg_color="#2b2b2b")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.main_container = ctk.CTkFrame(
            self,
            corner_radius=25,
            fg_color=BG_COLOR,
            border_width=0, 
        )
        self.main_container.pack(fill="both", expand=True, padx=0, pady=0)

        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<B1-Motion>", self.do_move)


        self.is_running = False
        self.selecting_area = False
        self.red_box_coordinates = None
        self.status_text = tk.StringVar(value="\n\n⏸ Скрипт не запущен")
        
        self.cooldown_label_text = tk.StringVar(value="")
        self.delay_before_spam = 1.5
        self.initial_seconds = None
        self.cooldown_timer_active = False
        self.spam_thread = None

        self.license_expiry_date = check_license()
        
        self.sidebar = ctk.CTkFrame(
            self.main_container, 
            width=200, 
            corner_radius=0, 
            fg_color=SIDEBAR_COLOR, 
            border_width=0
        )
        self.sidebar.pack(side="left", fill="y", padx=(0, 5), pady=0)

        logo_container = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
            corner_radius=0
        )
        logo_container.pack(pady=(40, 40), padx=15)

        self.logo_label = ctk.CTkLabel(
            logo_container,
            text="AUTO\n PAVILION",
            font=("Segoe UI", 25, "bold"),
            text_color=ACCENT_COLOR,
            anchor="center"
        )
        self.logo_label.pack(pady=(0, 5))   
        
        self.start_button = ctk.CTkButton(
            self.sidebar, 
            text="▶ Запустить", 
            command=self.toggle_script, 
            corner_radius=10, 
            font=("Segoe UI", 14, "bold"),
            fg_color=BUTTON_PRIMARY,
            hover_color=BUTTON_PRIMARY_HOVER,
            height=45,
            border_width=0
        )
        self.start_button.pack(pady=(0, 12), padx=15, fill="x")
        
        self.select_button = ctk.CTkButton(
            self.sidebar, 
            text="📐 Выбрать область", 
            command=self.start_select_red_box, 
            corner_radius=10, 
            font=("Segoe UI", 13, "bold"),
            fg_color=SECONDARY_COLOR,
            hover_color="#3a3a3a",
            height=40,
            border_width=1,
            border_color=INPUT_BORDER
        )
        self.select_button.pack(pady=(0, 12), padx=15, fill="x")
        
        self.clear_coords_button = ctk.CTkButton(
            self.sidebar,
            text="🗑 Очистить координаты",
            command=self.clear_coordinates,
            fg_color=ERROR_COLOR,
            hover_color="#ff3838",
            corner_radius=10,
            font=("Segoe UI", 13, "bold"),
            height=40,
            border_width=0
        )
        self.clear_coords_button.pack(pady=(0, 20), padx=15, fill="x")

        self.link_label = tk.Label(
            self.sidebar,
            text="Telegram",
            font=("Segoe UI", 11, "underline"),
            fg=TEXT_COLOR,
            bg=SIDEBAR_COLOR,
            cursor="hand2",
        )
        self.link_label.pack(side="bottom", pady=(0, 25))
        self.link_label.bind("<Button-1>", self.open_telegram_link)
        self.link_label.bind("<Enter>", lambda e: self.link_label.config(fg=HOVER_COLOR))
        self.link_label.bind("<Leave>", lambda e: self.link_label.config(fg=ACCENT_COLOR))
        
        self.main_frame = ctk.CTkFrame(
            self.main_container, 
            width=180, 
            corner_radius=0, 
            fg_color=MAIN_COLOR, 
            border_width=0
        )
        self.main_frame.pack(side="right", expand=True, fill="both", padx=(5, 0), pady=0)

        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="⚙️ Панель управления",
            font=("Segoe UI", 20, "bold"),
            text_color=TEXT_COLOR,
            cursor="fleur"
        )
        self.title_label.pack(pady=(25, 15))
        self.title_label.bind("<ButtonPress-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.do_move)
        
        license_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=CARD_COLOR,
            corner_radius=8,
            border_width=1,
            border_color=INPUT_BORDER
        )
        license_frame.pack(pady=(0, 15), padx=20, fill="x")
        
        if self.license_expiry_date:
            self.license_label = ctk.CTkLabel(
                license_frame,  
                text=f"✅ Лицензия до: {self.license_expiry_date.strftime('%d-%m-%Y')}",
                font=("Segoe UI", 11, "bold"),
                text_color=ACCENT_COLOR
            )
        else:
            self.license_label = ctk.CTkLabel(
                license_frame,  
                text="❌ Лицензия не найдена",
                font=("Segoe UI", 11, "bold"),
                text_color=ERROR_COLOR
            )
        self.license_label.pack(pady=8, padx=10)

        self.close_button = tk.Label(
            self.main_container,
            text="✕",
            font=("Segoe UI", 18, "bold"),
            bg=MAIN_COLOR,    
            fg=SUBTEXT_COLOR,
            cursor="hand2",
            width=2,
            height=1
        )
        
        def update_close_button_position(event=None):
            try:
                self.update_idletasks()
                self.close_button.place(
                    x=self.main_container.winfo_width() - 30, 
                    y=8,
                    width=25,
                    height=25
                )
            except:
                pass
        
        try:
            self.after(100, update_close_button_position)
        except:
            pass
        self.main_container.bind("<Configure>", update_close_button_position)
        
        self.close_button.bind("<Enter>", lambda e: self.close_button.config(bg=ERROR_COLOR, fg="white"))
        self.close_button.bind("<Leave>", lambda e: self.close_button.config(bg=MAIN_COLOR, fg=SUBTEXT_COLOR))
        self.close_button.bind("<Button-1>", lambda e: self.on_close())

        status_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=INPUT_BORDER
        )
        status_frame.pack(pady=(0, 15), padx=20, fill="x")
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            textvariable=self.status_text,
            font=("Segoe UI", 15, "bold"),
            text_color=TEXT_COLOR
        )
        self.status_label.pack(pady=12)

        self.cooldown_label = ctk.CTkLabel(
            status_frame, 
            textvariable=self.cooldown_label_text,
            font=("Segoe UI", 13, "bold"),
            text_color=ACCENT_COLOR,
        )
        self.cooldown_label.pack(pady=(0, 12))

        delay_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=INPUT_BORDER
        )
        delay_frame.pack(pady=(0, 15), padx=20, fill="x")
        
        self.delay_label = ctk.CTkLabel(
            delay_frame,
            text="⏱ Задержка перед флудом (1–4 сек):",
            font=("Segoe UI", 12, "bold"),
            text_color=TEXT_COLOR
        )
        self.delay_label.pack(pady=(12, 8))

        def only_numbers(char):
            if char == "":
                return True 
            try:
                float(char)  
                return True
            except ValueError:
                return False
        
        vcmd = self.register(only_numbers)
        
        entry_frame = ctk.CTkFrame(delay_frame, fg_color="transparent")
        entry_frame.pack(pady=(0, 12), padx=15)
        
        self.delay_entry = ctk.CTkEntry(
            entry_frame,
            width=150,
            font=("Segoe UI", 13, "bold"),
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            border_width=2,
            corner_radius=8,
            text_color=TEXT_COLOR,
            validate="key",
            validatecommand=(vcmd, "%P")
        )
        self.delay_entry.insert(0, str(self.delay_before_spam))
        self.delay_entry.pack(side="left", padx=(0, 10))
        
        self.set_delay_button = ctk.CTkButton(
            entry_frame, 
            text="✅ Установить", 
            command=self.set_delay, 
            height=35, 
            width=140,
            font=("Segoe UI", 12, "bold"),
            fg_color=BUTTON_PRIMARY,
            hover_color=BUTTON_PRIMARY_HOVER,
            corner_radius=8,
            border_width=0
        )
        self.set_delay_button.pack(side="left")
        
        log_container = ctk.CTkFrame(
            self.main_frame,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=INPUT_BORDER
        )
        log_container.pack(pady=(0, 10), padx=20, fill="both", expand=True)
        
        log_title = ctk.CTkLabel(
            log_container,
            text="📋 Лог активности",
            font=("Segoe UI", 12, "bold"),
            text_color=TEXT_COLOR
        )
        log_title.pack(pady=(10, 8), anchor="w", padx=15)
        
        self.log_box = ctk.CTkTextbox(
            log_container, 
            width=420, 
            height=250, 
            corner_radius=8, 
            fg_color=INPUT_BG, 
            border_color=INPUT_BORDER,
            border_width=1,
            font=("Consolas", 11),
            text_color="#00ff88",
            wrap="word"
        )
        self.log_box.pack(pady=(0, 10), padx=15, fill="both", expand=True)
        self.log_box.insert("end", "🚀 Готов к работе...\n")
        self.log_box.configure(state="disabled")
        
        self.log_box.bind("<Button-1>", lambda e: "break")  
        self.log_box.bind("<B1-Motion>", lambda e: "break") 
        self.log_box.bind("<Key>", lambda e: "break")  
        self.log_box.bind("<FocusIn>", lambda e: self.focus())  

        canvas_container = ctk.CTkFrame(
            self.main_frame,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=INPUT_BORDER
        )
        canvas_container.pack(pady=(0, 15), padx=20, fill="x")
        
        canvas_title = ctk.CTkLabel(
            canvas_container,
            text="📊 Предпросмотр области",
            font=("Segoe UI", 12, "bold"),
            text_color=TEXT_COLOR
        )
        canvas_title.pack(pady=(8, 5), anchor="w", padx=15)
        
        self.rectangle_canvas = tk.Canvas(
            canvas_container,
            width=520,
            height=100,
            bg=INPUT_BG,
            highlightthickness=1,
            highlightbackground=INPUT_BORDER,
            relief="flat",
            borderwidth=0
        )
        self.rectangle_canvas.pack(pady=(0, 10), padx=15, fill="x")
        
        self.load_coordinates() 
        self.draw_rectangle_preview()
    
    def custom_showinfo(title, message):
        window = ctk.CTkToplevel()
        window.title(title)
        window.geometry("400x200")
        window.resizable(False, False)
        window.configure(fg_color=BG_COLOR)
    
        label = ctk.CTkLabel(
            window, 
            text=message, 
            font=("Segoe UI", 14),
            text_color=TEXT_COLOR,
            wraplength=350
        )
        label.pack(pady=40, padx=20)
    
        ok_button = ctk.CTkButton(
            window, 
            text="OK", 
            command=window.destroy,
            fg_color=ACCENT_COLOR,
            hover_color=HOVER_COLOR,
            width=100
        )
        ok_button.pack(pady=10)
    
        window.grab_set()
        window.focus_set()
        window.wait_window()
        
       
    def open_telegram_link(self, event):
        webbrowser.open(TG_URL)
        
    def add_to_log(self):
        self.log_box.config(state=tk.NORMAL)
        self.log_box.insert(tk.END, "Новое сообщение в лог\n")
        self.log_box.see(tk.END) 
        self.log_box.config(state=tk.DISABLED)        

    def on_close(self):
        self.is_running = False  
        self.destroy()     

    def toggle_script(self):
        if self.is_running:
            self.stop_script()
        else:
            self.start_script()

    def start_script(self):
        if not self.red_box_coordinates:
            show_custom_message(
                title="Ошибка",
                message="\n\n\nПожалуйста, выберите область экрана!",
                msg_type="error"
            )
            return

        self.is_running = True
        self.status_text.set("\n\n✅ Скрипт запущен")
        self.start_button.configure(text="⏹ Остановить", fg_color=ERROR_COLOR, hover_color="#ff3838")
        self.log("🚀 Скрипт запущен...")
        threading.Thread(target=self.run_automation, daemon=True).start()

    def stop_script(self):
        self.is_running = False
        self.start_button.configure(text="▶ Запустить", fg_color=BUTTON_PRIMARY, hover_color=BUTTON_PRIMARY_HOVER)
        self.status_text.set("\n\n❌ Скрипт остановлен")
        self.log("⏸ Работа остановлена пользователем")
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

                #self.log(f"{time_text}")

                match = re.search(r'(\d+(?:\.\d+)?)\s*сек', time_text)
                if match:
                    seconds = float(match.group(1))
                    if self.initial_seconds is None:
                        self.initial_seconds = seconds
                        self.start_timer_and_spam(seconds)
                        self.log(f"⏱ Обнаружено время: {seconds:.2f} сек")
                elif "Вы аренд" in time_text:
                    self.stop_spam()
                    self.stop_script()
                    self.status_text.set("🏠 Павильон арендован!")
                    self.log("🎉 Павильон арендован!")
                    self.initial_seconds = None
                    self.update_cooldown_label("Время вышло")

                time.sleep(0.3)

            except Exception as e:
                self.status_text.set(f"Ошибка: {e}")
                self.log(f"❌ Ошибка: {e}")
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
            self.update_cooldown_label(f"⏳ До слёта: {remaining_time:.1f} сек")
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
            self.log(f"❌ Ошибка во флуде: {e}")
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
        self.overlay = tk.Toplevel(self)
        self.overlay.attributes("-fullscreen", True)
        self.overlay.attributes("-alpha", 0.2)
        self.overlay.attributes("-topmost", True)
        self.overlay.overrideredirect(True)
    
        self.canvas = tk.Canvas(self.overlay, bg="white", highlightthickness=2, highlightbackground="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
    
        rgb = self.overlay.winfo_rgb('#000000')  
        hex_to_rgb = '#%02x%02x%02x' % (rgb[0] // 256, rgb[1] // 256, rgb[2] // 256)
    
        self.info_frame = tk.Frame(self.canvas, bg=hex_to_rgb)
        self.info_frame.place(relx=0.5, rely=0.5, anchor='center')  
    
        self.info_label = tk.Label(self.info_frame,
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
            show_custom_message(
                title="Ошибка",
                message="Слишком малая область! Выберите область побольше.",
                msg_type="error"
            )
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
        self.log(f"📐 Выбрана область: {self.red_box_coordinates}")

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
                self.log(f"❌ Ошибка загрузки координат: {e}") 

    def save_coordinates(self): 
        try:
            data = {"coordinates": list(self.red_box_coordinates)}
            with open(COORDINATES_FILE, "w") as f:
                json.dump(data, f)
            self.log("💾 Координаты сохранены") 
        except Exception as e:
            self.log(f"❌ Ошибка сохранения координат: {e}")

    def clear_coordinates(self): 
        self.red_box_coordinates = None
        #self.status_text.set("Координаты очищены.")
        self.log("🗑 Координаты очищены")
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

                self.rectangle_canvas.create_rectangle(cx1, cy1, cx2, cy2, outline=RECTANGLE_COLOR, width=3, fill="", dash=(5, 5))
        except Exception as e:
            self.log(f"❌ Ошибка предпросмотра: {e}")

    def update_cooldown_label(self, text): 
        self.cooldown_label_text.set(text)

    def set_delay(self): 
        try:
            val = float(self.delay_entry.get())
            if 1 <= val < 4:
                self.delay_before_spam = val
                self.log(f"✅ Задержка установлена: {val:.2f} сек")
            else:
                show_custom_message(
                    title="Ошибка",
                    message="Введите значение от 1 до 4 сек.",
                    msg_type="error"
                )
        except ValueError:
            show_custom_message(
                title="Ошибка",
                message="Введите корректное число.",
                msg_type="error"
            )
            

    def log(self, text: str):
        self.log_box.configure(state="normal")     
        self.log_box.insert("end", f"{text}\n")    
        self.log_box.see("end")                  
        self.log_box.configure(state="disabled")
        
    
        
if __name__ == "__main__":
    temp_root = ctk.CTk()
    temp_root.withdraw()
    temp_root.attributes("-alpha", 0)
    temp_root.update()
    
    root = tk.Tk()
    root.withdraw()
    auto_update()
    
    check_and_close_extreme_injector()
    
    check_license()
    
    try:
        root.update()
        root.update_idletasks()
        root.destroy()
    except Exception as e:
        print(f"Ошибка при уничтожении root: {e}")
    
    try:
        temp_root.update()
        temp_root.update_idletasks()
        time.sleep(0.1)
        temp_root.destroy()
    except Exception as e:
        print(f"Ошибка при уничтожении temp_root: {e}")
    
    app = AutoPavilionApp()
    app.mainloop()

