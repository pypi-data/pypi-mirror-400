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

    # پیدا کردن مسیر موتور داخلی به صورت کاملا دقیق
    base_path = os.path.dirname(os.path.abspath(__file__))
    internal_pyinstaller = os.path.join(base_path, "bin", "pyinstaller.exe")

    # اگر موتور داخلی نبود، از موتور سیستم استفاده کن
    if os.path.exists(internal_pyinstaller):
        executable_cmd = [internal_pyinstaller]
    else:
        executable_cmd = [sys.executable, "-m", "PyInstaller"]

    root = tk.Tk()
    root.withdraw()

    if not messagebox.askyesno("AfterBuild PRO", "برنامه بسته شد. آیا می‌خواهید خروجی EXE بسازید؟"):
        return

    # انتخاب محل ذخیره
    save_path = filedialog.askdirectory(title="محل ذخیره فایل EXE نهایی")
    if not save_path: return

    # استفاده از نام انتخابی کاربر (مثل test)
    clean_name = "test" 

    # دستور ساخت با پارامترهای بسیار دقیق برای رفع خطای تصاویر شما
    cmd = executable_cmd + [
        "--onefile",
        "--noconsole",
        "--clean",
        "--name", clean_name,
        "--distpath", os.path.abspath(save_path),
        "--workpath", os.path.join(os.path.expanduser("~"), "afterbuild_temp"), # انتقال فایل‌های موقت به خارج از پوشه فارسی
        os.path.abspath(main_file)
    ]

    try:
        # اجرا و نمایش لاگ در صورت بروز خطا
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            messagebox.showinfo("Success", f"فایل '{clean_name}.exe' با موفقیت ساخته شد!")
        else:
            # نمایش دلیل فنی دقیق برای رفع مشکل نهایی
            messagebox.showerror("Build Failed", f"موتور بیلد متوقف شد:\n{result.stderr}")
            
    except Exception as e:
        messagebox.showerror("System Error", f"خطای غیرمنتظره: {str(e)}")
