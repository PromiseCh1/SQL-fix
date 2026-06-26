import os
import shutil
import subprocess
import datetime
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ============================================================
#  XAMPP MariaDB Repair Utility
#  Created by Promise
# ============================================================

class RepairApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MariaDB Repair Tool")
        self.root.geometry("620x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#f5f6fa")

        # Variables
        self.xampp_path = tk.StringVar(value="")
        self.status_text = tk.StringVar(value="Ready")
        self.backup_root = os.path.join(os.path.expanduser("~"), "Desktop", "MariaDB_Backups")
        self.log_file = "repair_log.txt"

        self._build_ui()
        self.root.after(500, self.auto_detect)

    def _build_ui(self):
        # ----- Header (blue) -----
        header = tk.Frame(self.root, bg="#2c3e50", height=80)
        header.pack(fill=tk.X, pady=(0, 15))
        header.pack_propagate(False)

        title = tk.Label(header, text="MariaDB Repair Utility",
                         font=("Segoe UI", 18, "bold"), fg="white", bg="#2c3e50")
        title.pack(pady=(12, 0))

        author = tk.Label(header, text="Created by Promise",
                          font=("Segoe UI", 10), fg="#b0bec5", bg="#2c3e50")
        author.pack()

        # ----- Main content -----
        main = tk.Frame(self.root, bg="#f5f6fa")
        main.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        # Step 1: XAMPP path
        step1 = tk.Label(main, text="Step 1: Locate your XAMPP folder",
                         font=("Segoe UI", 11, "bold"), bg="#f5f6fa", fg="#2c3e50")
        step1.pack(anchor=tk.W, pady=(0, 5))

        path_frame = tk.Frame(main, bg="#f5f6fa")
        path_frame.pack(fill=tk.X, pady=(0, 15))

        entry = tk.Entry(path_frame, textvariable=self.xampp_path,
                         font=("Segoe UI", 10), bg="white", fg="#333",
                         relief=tk.SOLID, bd=1)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), ipady=5)

        btn_browse = tk.Button(path_frame, text="Browse", command=self.browse_xampp,
                               bg="#3498db", fg="white", font=("Segoe UI", 9, "bold"),
                               padx=12, cursor="hand2", relief=tk.FLAT)
        btn_browse.pack(side=tk.LEFT, padx=(0, 5))

        btn_detect = tk.Button(path_frame, text="Auto-Detect", command=self.auto_detect,
                               bg="#95a5a6", fg="white", font=("Segoe UI", 9, "bold"),
                               padx=12, cursor="hand2", relief=tk.FLAT)
        btn_detect.pack(side=tk.LEFT)

        # Step 2: Repair
        step2 = tk.Label(main, text="Step 2: Start the repair process",
                         font=("Segoe UI", 11, "bold"), bg="#f5f6fa", fg="#2c3e50")
        step2.pack(anchor=tk.W, pady=(10, 5))

        btn_repair = tk.Button(main, text="Start Automatic Repair",
                               command=self.start_repair,
                               bg="#27ae60", fg="white", font=("Segoe UI", 12, "bold"),
                               padx=30, pady=12, cursor="hand2", relief=tk.FLAT)
        btn_repair.pack(pady=(0, 15))

        # Progress bar
        self.progress = ttk.Progressbar(main, orient=tk.HORIZONTAL, length=500, mode='determinate')
        self.progress.pack(pady=(5, 10), fill=tk.X)

        # Status label
        self.status_label = tk.Label(main, textvariable=self.status_text,
                                     font=("Segoe UI", 10), bg="#f5f6fa", fg="#2c3e50")
        self.status_label.pack(pady=(0, 15))

        # Info box (how‑to)
        info_frame = tk.Frame(main, bg="#ecf0f1", relief=tk.GROOVE, bd=1)
        info_frame.pack(fill=tk.X, pady=(5, 0))

        info_text = (
            "How it works:\n"
            "1. The tool backs up your current mysql\\data folder to your Desktop.\n"
            "2. It restores the system databases from mysql\\backup\\mysql.\n"
            "3. Your data is safe – the backup is always saved before changes."
        )
        info_label = tk.Label(info_frame, text=info_text, font=("Segoe UI", 9),
                              bg="#ecf0f1", fg="#34495e", justify=tk.LEFT, padx=10, pady=10)
        info_label.pack(anchor=tk.W)

        # Bottom buttons (small)
        bottom = tk.Frame(self.root, bg="#f5f6fa")
        bottom.pack(fill=tk.X, padx=30, pady=(0, 15))

        btn_log = tk.Button(bottom, text="Open Log", command=self.open_log,
                            bg="#bdc3c7", fg="#2c3e50", font=("Segoe UI", 8),
                            padx=10, cursor="hand2", relief=tk.FLAT)
        btn_log.pack(side=tk.LEFT, padx=(0, 10))

        btn_backup = tk.Button(bottom, text="View Backups", command=self.view_backups,
                               bg="#bdc3c7", fg="#2c3e50", font=("Segoe UI", 8),
                               padx=10, cursor="hand2", relief=tk.FLAT)
        btn_backup.pack(side=tk.LEFT)

    # ============================================================
    #  Core logic (same reliable engine)
    # ============================================================

    def update_status(self, msg, is_error=False):
        self.status_text.set(msg)
        self.root.update_idletasks()
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")

    def auto_detect(self):
        self.update_status("Scanning for XAMPP...")
        drives = [f"{d}:\\" for d in "CDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
        for drive in drives:
            test_path = os.path.join(drive, "xampp")
            if os.path.exists(test_path):
                mysqld = os.path.join(test_path, "mysql", "bin", "mysqld.exe")
                if os.path.exists(mysqld):
                    self.xampp_path.set(test_path)
                    self.update_status(f"XAMPP found at: {test_path}")
                    return
        self.update_status("XAMPP not found. Please browse manually.", is_error=True)

    def browse_xampp(self):
        path = filedialog.askdirectory(title="Select XAMPP root folder")
        if path:
            if os.path.exists(os.path.join(path, "mysql", "bin", "mysqld.exe")):
                self.xampp_path.set(path)
                self.update_status(f"XAMPP set to: {path}")
            else:
                messagebox.showerror("Invalid Folder", "Not a valid XAMPP folder.\nMissing mysql\\bin\\mysqld.exe")
                self.update_status("Invalid folder selected.", is_error=True)

    def stop_mysql(self):
        self.update_status("Stopping MariaDB/MySQL service...")
        try:
            subprocess.run(["net", "stop", "mysql"], capture_output=True, shell=True)
            subprocess.run(["net", "stop", "MariaDB"], capture_output=True, shell=True)
        except:
            pass
        self.update_status("Service stopped (or already stopped).")

    def start_mysql(self):
        self.update_status("Restarting service...")
        try:
            subprocess.run(["net", "start", "mysql"], capture_output=True, shell=True)
        except:
            pass
    def perform_repair(self, xampp_path):
        try:
            self.update_status("Checking required folders...")
            required = {
                "mysql\\data": os.path.join(xampp_path, "mysql", "data"),
                "mysql\\backup\\mysql": os.path.join(xampp_path, "mysql", "backup", "mysql"),
                "mysql\\bin\\mysqld.exe": os.path.join(xampp_path, "mysql", "bin", "mysqld.exe")
            }
            for name, path in required.items():
                if not os.path.exists(path):
                    self.root.after(0, lambda: messagebox.showerror("Error 101", f"Missing: {name}"))
                    self.update_status(f"ERROR: Missing {name}", is_error=True)
                    self.root.after(0, self.reset_ui)
                    return

            # Check if backup folder has contents
            backup_mysql = required["mysql\\backup\\mysql"]
            backup_items = os.listdir(backup_mysql)
            if not backup_items:
                self.root.after(0, lambda: messagebox.showerror("Error", "Backup folder is empty! Cannot repair."))
                self.update_status("ERROR: Backup folder is empty.", is_error=True)
                self.root.after(0, self.reset_ui)
                return
            self.update_status(f"Backup contains {len(backup_items)} items.")

            self.stop_mysql()

            # Backup
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_dir = os.path.join(self.backup_root, timestamp)
            os.makedirs(backup_dir, exist_ok=True)
            self.update_status(f"Backing up data to Desktop...")

            data_src = required["mysql\\data"]
            items = os.listdir(data_src)
            for i, item in enumerate(items):
                src = os.path.join(data_src, item)
                dst = os.path.join(backup_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, ignore_dangling_symlinks=True)
                else:
                    shutil.copy2(src, dst)
                progress_val = ((i + 1) / len(items)) * 100 if items else 100
                self.root.after(0, lambda v=progress_val: self.progress.config(value=v))

            self.update_status("Backup completed.")

            # Clear data folder
            self.update_status("Clearing data folder...")
            for item in os.listdir(data_src):
                item_path = os.path.join(data_src, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                else:
                    os.remove(item_path)

            # Copy backup into data
            self.update_status("Restoring system databases from backup...")
            for item in backup_items:
                src = os.path.join(backup_mysql, item)
                dst = os.path.join(data_src, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)

            self.update_status(f"Restored {len(backup_items)} items.")

            # Log success
            log_entry = f"""
====================================
Repair SUCCESS
Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
XAMPP: {xampp_path}
Backup: {backup_dir}
====================================
"""
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)

            self.root.after(0, lambda: self.repair_done(backup_dir))

        except Exception as e:
            self.update_status(f"CRITICAL ERROR: {e}", is_error=True)
            messagebox.showerror("Critical Error", str(e))
            self.root.after(0, self.reset_ui)
        try:
            # Safety checks
            self.update_status("Checking required folders...")
            required = {
                "mysql\\data": os.path.join(xampp_path, "mysql", "data"),
                "mysql\\backup\\mysql": os.path.join(xampp_path, "mysql", "backup", "mysql"),
                "mysql\\bin\\mysqld.exe": os.path.join(xampp_path, "mysql", "bin", "mysqld.exe")
            }
            for name, path in required.items():
                if not os.path.exists(path):
                    self.root.after(0, lambda: messagebox.showerror("Error 101", f"Missing: {name}"))
                    self.update_status(f"ERROR: Missing {name}", is_error=True)
                    self.root.after(0, self.reset_ui)
                    return

            self.stop_mysql()

            # Backup
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_dir = os.path.join(self.backup_root, timestamp)
            os.makedirs(backup_dir, exist_ok=True)
            self.update_status(f"Backing up data to Desktop...")

            data_src = os.path.join(xampp_path, "mysql", "data")
            items = os.listdir(data_src)
            for i, item in enumerate(items):
                src = os.path.join(data_src, item)
                dst = os.path.join(backup_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, ignore_dangling_symlinks=True)
                else:
                    shutil.copy2(src, dst)
                progress_val = ((i + 1) / len(items)) * 100
                self.root.after(0, lambda v=progress_val: self.progress.config(value=v))

            self.update_status("Backup completed.")

            # Restore system databases
            self.update_status("Restoring system databases from backup...")
            backup_mysql = os.path.join(xampp_path, "mysql", "backup", "mysql")

            # Clean data folder
            for item in os.listdir(data_src):
                item_path = os.path.join(data_src, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                else:
                    os.remove(item_path)

            # Copy backup into data
            for item in os.listdir(backup_mysql):
                src = os.path.join(backup_mysql, item)
                dst = os.path.join(data_src, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)

            self.update_status("System databases restored.")

            # Log success
            log_entry = f"""
====================================
Repair SUCCESS
Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
XAMPP: {xampp_path}
Backup: {backup_dir}
====================================
"""
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)

            self.root.after(0, lambda: self.repair_done(backup_dir))

        except Exception as e:
            self.update_status(f"CRITICAL ERROR: {e}", is_error=True)
            messagebox.showerror("Critical Error", str(e))
            self.root.after(0, self.reset_ui)

    def repair_done(self, backup_dir):
        self.update_status("Repair completed successfully!")
        self.progress.config(value=100)
        messagebox.showinfo("Success", f"Repair completed!\nBackup saved to:\n{backup_dir}\n\nStart MySQL from XAMPP.")
        self.start_mysql()
        self.reset_ui()

    def reset_ui(self):
        self.progress.config(value=0)
        self.root.config(cursor="")

    def start_repair(self):
        path = self.xampp_path.get().strip()
        if not path or not os.path.exists(path):
            messagebox.showerror("Error", "Please select a valid XAMPP folder first.")
            return

        if not messagebox.askyesno("Confirm", f"Repair MariaDB at:\n{path}\n\nA backup will be created on your Desktop.\nProceed?"):
            return

        self.update_status("Repair in progress...")
        self.root.config(cursor="watch")
        self.progress.config(value=0)

        thread = threading.Thread(target=self.perform_repair, args=(path,), daemon=True)
        thread.start()

    def open_log(self):
        if os.path.exists(self.log_file):
            os.startfile(self.log_file)
        else:
            messagebox.showinfo("No Log", "No log file found yet.")

    def view_backups(self):
        if os.path.exists(self.backup_root):
            os.startfile(self.backup_root)
        else:
            messagebox.showinfo("No Backups", "No backups folder found on Desktop.")

# ---- Run the app ----
if __name__ == "__main__":
    root = tk.Tk()
    app = RepairApp(root)
    root.mainloop()