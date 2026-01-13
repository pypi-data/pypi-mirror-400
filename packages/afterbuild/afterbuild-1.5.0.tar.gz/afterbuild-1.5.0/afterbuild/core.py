import sys
import os
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog

def gui_build(main_file):
    # جلوگیری از اجرا در حالت EXE
    if getattr(sys, 'frozen', False):
        return

    # پیدا کردن مسیر ابزار داخلی که در عکس کپی کردی
    base_path = os.path.dirname(os.path.abspath(__file__))
    internal_tool = os.path.join(base_path, "bin", "pyinstaller.exe")

    # انتخاب بهترین موتور بیلد
    if os.path.exists(internal_tool):
        executable = [internal_tool]
    else:
        executable = [sys.executable, "-m", "PyInstaller"]

    root = tk.Tk()
    root.withdraw()

    if not messagebox.askyesno("AfterBuild PRO", "آیا می‌خواهید از این برنامه خروجی EXE بگیرید؟"):
        return

    save_path = filedialog.askdirectory(title="محل ذخیره فایل EXE")
    if not save_path: return

    # دستور ساخت با پارامترهای تمیزکاری
    command = executable + [
        "--onefile",
        "--noconsole",
        "--clean",
        "--distpath", os.path.abspath(save_path),
        os.path.abspath(main_file)
    ]

    try:
        # اجرا و دریافت گزارش کامل خطا
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            messagebox.showinfo("موفقیت", "فایل EXE با موفقیت ساخته شد!")
        else:
            # نمایش دلیل دقیق خطا برای عیب‌یابی
            messagebox.showerror("خطا در بیلد", f"موتور بیلد متوقف شد:\n{result.stderr}")
            
    except Exception as e:
        messagebox.showerror("خطای سیستمی", str(e))
