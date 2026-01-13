import sys
import os
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog

def is_exported():
    """جلوگیری از اجرای مجدد در فایل ساخته شده"""
    return getattr(sys, 'frozen', False)

def gui_build(main_file):
    if is_exported():
        return

    # پیدا کردن مسیر ابزار داخلی در پوشه bin
    base_path = os.path.dirname(__file__)
    internal_pyinstaller = os.path.join(base_path, "bin", "pyinstaller.exe")

    # بررسی وجود ابزار داخلی؛ اگر نبود از نسخه سیستم استفاده می‌کند
    if os.path.exists(internal_pyinstaller):
        executable_cmd = [internal_pyinstaller]
    else:
        executable_cmd = [sys.executable, "-m", "PyInstaller"]

    root = tk.Tk()
    root.title("AfterBuild PRO - Standalone Edition")
    root.geometry("500x550")
    root.configure(bg="#f4f4f4")

    # متغیرهای تنظیمات
    settings = {
        "exe_name": tk.StringVar(value=os.path.basename(main_file).split('.')[0]),
        "icon_path": tk.StringVar(),
        "save_path": tk.StringVar(),
        "onefile": tk.BooleanVar(value=True),
        "noconsole": tk.BooleanVar(value=True)
    }

    # رابط کاربری
    tk.Label(root, text="🛠 AfterBuild Universal Builder", font=("Arial", 16, "bold"), bg="#f4f4f4").pack(pady=20)

    # بخش تنظیمات
    frame = tk.Frame(root, bg="#f4f4f4")
    frame.pack(padx=30, fill="x")

    tk.Label(frame, text="Project Name:", bg="#f4f4f4").pack(anchor="w")
    tk.Entry(frame, textvariable=settings["exe_name"], width=40).pack(pady=5)

    def select_icon():
        path = filedialog.askopenfilename(filetypes=[("Icon", "*.ico")])
        if path: settings["icon_path"].set(path)
    
    tk.Button(frame, text="Choose Icon (.ico)", command=select_icon).pack(pady=10)
    
    def select_save():
        path = filedialog.askdirectory()
        if path: settings["save_path"].set(path)
        
    tk.Button(frame, text="Select Output Folder", command=select_save, bg="#ddd").pack(pady=5)
    tk.Label(frame, textvariable=settings["save_path"], fg="blue", font=("Arial", 8)).pack()

    tk.Checkbutton(frame, text="Single File (--onefile)", variable=settings["onefile"], bg="#f4f4f4").pack(anchor="w", pady=5)
    tk.Checkbutton(frame, text="Hide Console (No-Window)", variable=settings["noconsole"], bg="#f4f4f4").pack(anchor="w")

    def run_build():
        if not settings["save_path"].get():
            messagebox.showwarning("Error", "Please select a save location!")
            return

        # دستور نهایی با استفاده از فایل داخلی
        cmd = executable_cmd + [
            "--clean",
            "--name", settings["exe_name"].get(),
            "--distpath", settings["save_path"].get(),
            main_file
        ]

        if settings["onefile"].get(): cmd.append("--onefile")
        if settings["noconsole"].get(): cmd.append("--noconsole")
        if settings["icon_path"].get(): cmd += ["--icon", settings["icon_path"].get()]

        root.destroy()

        try:
            # اجرای فرآیند ساخت
            subprocess.run(cmd, check=True)
            
            # تمیزکاری فایل‌های اضافی
            spec_file = settings["exe_name"].get() + ".spec"
            if os.path.exists(spec_file): os.remove(spec_file)
            if os.path.exists("build"): shutil.rmtree("build")

            # اعلام موفقیت
            msg_box = tk.Tk()
            msg_box.withdraw()
            messagebox.showinfo("Done!", "EXE created successfully without any external dependencies!")
        except Exception as e:
            messagebox.showerror("Error", f"Build failed: {e}")

    tk.Button(root, text="🚀 BUILD EXE NOW", bg="#2ecc71", fg="white", font=("Arial", 12, "bold"), 
              height=2, width=20, command=run_build).pack(pady=30)

    root.mainloop()
