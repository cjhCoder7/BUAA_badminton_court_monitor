import tkinter as tk
from tkinter import messagebox
from threading import Thread
import datetime
from playwright_runner import PlaywrightRunner


class VenueCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Venue Availability Checker")
        self.root.geometry("600x600")

        self.stop_threads = False
        self.playwright_runner = PlaywrightRunner(
            self
        )  # 传递 app 的引用给 PlaywrightRunner

        # 登录框界面
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=20)

        tk.Label(
            self.login_frame, text="Username:", font=("Helvetica", 12, "bold")
        ).grid(row=0, column=0, padx=10, pady=10)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1)

        tk.Label(
            self.login_frame, text="Password:", font=("Helvetica", 12, "bold")
        ).grid(row=1, column=0, padx=10, pady=10)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1)

        self.login_button = tk.Button(
            self.login_frame,
            text="Login",
            command=self.login,
            bg="#4CAF50",  # 背景颜色
            fg="white",  # 字体颜色
            font=("Helvetica", 12, "bold"),  # 字体样式
            relief="raised",  # 按钮立体感
            bd=3,  # 边框宽度
        )
        self.login_button.grid(row=2, columnspan=2, pady=10)

        # 场馆空闲信息显示框
        self.venue_frame = tk.Frame(self.root)
        self.venue_text = tk.Text(
            self.venue_frame,
            height=100,
            width=100,
            state=tk.DISABLED,
            font=("Helvetica", 12, "bold"),
            bg="#c2e9fb",
            fg="white",
        )

        # 退出界面按钮
        self.exit_button = tk.Button(
            self.venue_frame,
            text="Exit",
            command=self.on_exit,
            bg="#4CAF50",  # 背景颜色
            fg="white",  # 字体颜色
            font=("Helvetica", 12, "bold"),  # 字体样式
            relief="raised",  # 按钮立体感
            bd=3,  # 边框宽度
        )
        self.exit_button.pack(pady=10)

        self.venue_text.pack(pady=10)
        self.venue_frame.pack_forget()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        self.playwright_runner.run_playwright_in_thread(username, password)

    def show_venue_frame(self):
        self.login_frame.pack_forget()
        self.venue_frame.pack(pady=20)

    def update_venue_info(self, site_list):
        # 弹出警告窗口
        messagebox.showwarning(
            "Update Notification", "The venue list has been updated!"
        )

        self.venue_text.config(
            state=tk.NORMAL, font=("Helvetica", 12, "bold"), bg="#c2e9fb", fg="white"
        )  # 允许编辑
        self.venue_text.delete(1.0, tk.END)

        self.venue_text.insert(tk.END, "=" * 50 + "\n")
        self.venue_text.insert(
            tk.END,
            f"Updated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        )
        self.venue_text.insert(tk.END, "=" * 50 + "\n\n")

        for date, venues in site_list.items():
            self.venue_text.insert(tk.END, f"Date: {date}\n")
            self.venue_text.insert(tk.END, "-" * 50 + "\n")
            for venue, times in venues.items():
                self.venue_text.insert(tk.END, f"Venue: {venue}\n")
                self.venue_text.insert(
                    tk.END, f"Availability Times: {', '.join(times)}\n\n"
                )
            self.venue_text.insert(tk.END, "-" * 50 + "\n\n")

        self.venue_text.config(
            state=tk.DISABLED,
            font=("Helvetica", 12, "bold"),
            bg="#c2e9fb",
            fg="white",
        )  # 禁止编辑

    def on_exit(self):
        self.playwright_runner.stop_playwright_thread()
        self.root.destroy()
