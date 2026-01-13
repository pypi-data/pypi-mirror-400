import sys
import os
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog

def is_exported():
    return getattr(sys, 'frozen', False)

def gui_build(main_file):
    if is_exported(): return

    # پیدا کردن مسیر دقیق ابزار داخلی که در عکس کپی کردی
    base_path = os.path.dirname(os.path.abspath(__file__))
    internal_tool = os.path.join(base_path, "bin", "pyinstaller.exe")

    if os.path.exists(internal_tool):
        executable = [internal_tool]
    else:
        executable = [sys.executable, "-m", "PyInstaller"]

    root = tk.Tk()
    root.withdraw()

    if not messagebox.askyesno("AfterBuild PRO", "برنامه بسته شد. آیا می‌خواهید نسخه EXE بسازید؟"):
        return

    save_path = filedialog.askdirectory(title="محل ذخیره فایل EXE نهایی")
    if not save_path: return

    # اصلاح هوشمندانه نام پروژه (حل مشکل نام فایل در تصویر شما)
    original_name = os.path.basename(main_file).split('.')[0]
    # اگر نام فایل نامعتبر (مثل ;) یا خیلی کوتاه بود، نام پیش‌فرض بگذار
    clean_name = original_name if len(original_name) > 1 and original_name.isalnum() else "MyApp"

    # دستور ساخت با پارامترهای تمیزکاری
    command = executable + [
        "--onefile",
        "--noconsole",
        "--clean",
        "--name", clean_name,
        "--distpath", os.path.abspath(save_path),
        os.path.abspath(main_file)
    ]

    try:
        # اجرا و نمایش لاگ کامل در صورت بروز خطا
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            messagebox.showinfo("Success", f"فایل '{clean_name}.exe' با موفقیت ساخته شد!")
        else:
            # نمایش دقیق خطا برای کاربر
            messagebox.showerror("Build Failed", f"موتور بیلد متوقف شد. دلیل:\n{result.stderr}")
            
    except Exception as e:
        messagebox.showerror("System Error", f"خطای غیرمنتظره: {str(e)}")
