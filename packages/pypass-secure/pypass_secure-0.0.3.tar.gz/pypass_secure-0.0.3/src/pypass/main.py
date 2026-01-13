import customtkinter as ctk
from pypass.ui import PyPassapp
import sys

def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme('blue')

    app = PyPassapp()
    app.mainloop()

if __name__ == "__main__":
    main()
