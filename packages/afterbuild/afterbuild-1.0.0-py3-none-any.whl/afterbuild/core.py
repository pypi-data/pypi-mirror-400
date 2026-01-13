import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog

def gui_build(main_file):
    root = tk.Tk()
    root.withdraw()

    if not messagebox.askyesno(
        "AfterBuild",
        "آیا می‌خواهید خروجی اجرایی ساخته شود؟"
    ):
        return

    name = simple_input("نام خروجی (اختیاری):")
    onefile = messagebox.askyesno(
        "AfterBuild",
        "خروجی تک‌فایل باشد؟"
    )

    icon = filedialog.askopenfilename(
        title="انتخاب آیکن (اختیاری)",
        filetypes=[("Icon files", "*.ico *.icns")]
    )

    out_dir = filedialog.askdirectory(
        title="انتخاب مسیر خروجی"
    )

    cmd = [sys.executable, "-m", "PyInstaller", main_file]

    if onefile:
        cmd.append("--onefile")
    if name:
        cmd += ["--name", name]
    if icon:
        cmd += ["--icon", icon]
    if out_dir:
        cmd += ["--distpath", out_dir]

    messagebox.showinfo("AfterBuild", "ساخت خروجی شروع شد")
    subprocess.run(cmd)
    messagebox.showinfo("AfterBuild", "✅ خروجی ساخته شد")


def simple_input(title):
    win = tk.Tk()
    win.title("AfterBuild")
    value = tk.StringVar()

    tk.Label(win, text=title).pack(padx=10, pady=5)
    entry = tk.Entry(win, textvariable=value)
    entry.pack(padx=10)
    entry.focus()

    def submit():
        win.destroy()

    tk.Button(win, text="تأیید", command=submit).pack(pady=10)
    win.mainloop()

    return value.get().strip()