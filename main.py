import tkinter as tk
from app import VenueCheckerApp

if __name__ == "__main__":
    root = tk.Tk()
    app = VenueCheckerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_exit)
    root.mainloop()
