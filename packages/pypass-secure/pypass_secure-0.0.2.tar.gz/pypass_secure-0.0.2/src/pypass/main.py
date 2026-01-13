import customtkinter as ctk
from pypass.ui import PyPassapp
import os
import sys
import subprocess

def main():
    if sys.platform == "win32" and not os.environ.get("PYPASS_NO_HIDE_CONSOLE"):
        try:
            subprocess.Popen(
                [sys.executable, "-c", f"import os; os.environ['PYPASS_NO_HIDE_CONSOLE']='1'; from pypass import main; main()"],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            sys.exit(0)
        except:
            pass

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme('blue')

    app = PyPassapp()
    app.mainloop()

if __name__ == "__main__":
    main()
