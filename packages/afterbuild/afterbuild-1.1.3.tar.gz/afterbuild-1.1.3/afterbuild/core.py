import sys
import os
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog

def gui_build(main_file):
    if getattr(sys, 'frozen', False):
        return

    root = tk.Tk()
    root.title("AfterBuild PRO - Universal Builder")
    root.geometry("500x450")
    root.configure(bg="#f5f5f5")

    settings = {
        "exe_name": tk.StringVar(value=os.path.basename(main_file).split('.')[0]),
        "icon_path": tk.StringVar(),
        "save_path": tk.StringVar(),
        "compress": tk.BooleanVar(value=False)
    }

    # Header
    tk.Label(root, text="🚀 AfterBuild Professional", font=("Segoe UI", 16, "bold"), bg="#f5f5f5", fg="#333").pack(pady=20)

    # Frame for Inputs
    frame = tk.Frame(root, bg="#f5f5f5")
    frame.pack(padx=20, fill="x")

    # Name Entry
    tk.Label(frame, text="Product Name:", bg="#f5f5f5", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")
    tk.Entry(frame, textvariable=settings["exe_name"], width=30).grid(row=0, column=1, pady=10)

    # Icon Picker
    def get_icon():
        path = filedialog.askopenfilename(filetypes=[("Icon", "*.ico")])
        settings["icon_path"].set(path)
    
    tk.Button(frame, text="Select Icon", command=get_icon, width=15).grid(row=1, column=0, pady=10)
    tk.Label(frame, textvariable=settings["icon_path"], font=("Segoe UI", 8), fg="grey").grid(row=1, column=1)

    # Save Path
    def get_save_path():
        path = filedialog.askdirectory()
        settings["save_path"].set(path)

    tk.Button(frame, text="Destination Path", command=get_save_path, width=15).grid(row=2, column=0, pady=10)
    tk.Label(frame, textvariable=settings["save_path"], font=("Segoe UI", 8), fg="blue").grid(row=2, column=1)

    # Compression Option
    tk.Checkbutton(root, text="Enable High Compression (Requires UPX)", variable=settings["compress"], bg="#f5f5f5").pack(pady=10)

    def build():
        if not settings["save_path"].get():
            messagebox.showwarning("Warning", "Please select a destination path!")
            return

        # PyInstaller Command Construction
        command = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--noconsole",
            "--clean",
            "--name", settings["exe_name"].get(),
            "--distpath", settings["save_path"].get(),
            main_file
        ]

        if settings["icon_path"].get():
            command.extend(["--icon", settings["icon_path"].get()])
        
        root.destroy()
        
        try:
            subprocess.run(command, check=True)
            
            # Clean up temporary files (.spec and build folder)
            spec_file = settings["exe_name"].get() + ".spec"
            if os.path.exists(spec_file): os.remove(spec_file)
            if os.path.exists("build"): shutil.rmtree("build")
            
            # Success Alert
            final_win = tk.Tk()
            final_win.withdraw()
            messagebox.showinfo("Success", f"Congratulations!\n'{settings['exe_name'].get()}' is ready in:\n{settings['save_path'].get()}")
        except Exception as e:
            messagebox.showerror("Error", f"Build failed: {str(e)}")

    tk.Button(root, text="GENERATE EXECUTABLE", bg="#0078d7", fg="white", font=("Segoe UI", 12, "bold"), 
              width=25, height=2, command=build).pack(pady=20)

    root.mainloop()
