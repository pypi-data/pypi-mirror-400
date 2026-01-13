from PIL import Image
import customtkinter as ctk
from pypass.login import is_first_start, reg_get
from pypass.login import setup as create_account
from pypass.login import login as login_account
from pypass.vault import VaultDB
from pypass.encryption import derive_key
import os







class PyPassapp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PyPass by rewind | V0.0.2 ~ Beta")
        self.geometry("800x500")


        self.salt = None

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.eye_icon = ctk.CTkImage(
            Image.open(os.path.join(os.path.dirname(__file__), "icons", "eye.png")),
            size=(20, 20)
        )


        if is_first_start():
            self.show_create_password_screen()
        else:
            self.show_login_screen()


    


    def clear_screen(self):
        for widget in self.container.winfo_children():
            widget.destroy()


    # Start menu (im not using chatgpt can we please normalize comments in code again?)


    def show_create_password_screen(self):
        self.clear_screen()

        ctk.CTkLabel(self.container, text="Welcome to PyPass", font=("Arial", 24)).pack(pady=30)
        ctk.CTkLabel(self.container, text="Please create your master password", font=("Arial", 14)).pack(pady=10)

        self.create_entry = ctk.CTkEntry(self.container, show="*")
        self.create_entry.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.container, text="")
        self.status_label.pack(pady=10)

        ctk.CTkButton(self.container, text="Create Password", command=self.create_account_clicked).pack(pady=10)




    def create_account_clicked(self):
        password = self.create_entry.get()

        if not password:
            self.status_label.configure(text="Password cannot be empty", text_color="red")
            return
        


        self.salt = create_account(password)

        self.status_label.configure(
            text="Password created successfully",
            text_color="green"
            )
        self.after(600, self.show_login_screen)




    def show_login_screen(self):
        self.clear_screen()

        if self.salt is None:
            self.salt = reg_get("salt")

        ctk.CTkLabel(self.container, text="Login", font=("Arial", 24)).pack(pady=30)

        self.login_entry = ctk.CTkEntry(self.container, show="*")
        self.login_entry.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.container, text="")
        self.status_label.pack(pady=10)
      
        ctk.CTkButton(self.container, text="Login", command=self.login_clicked).pack(pady=10)




    def login_clicked(self):
        password = self.login_entry.get()

        if not self.salt:
            self.status_label.configure(
                text="Missing salt to cook..! (this is not your fault try restart the script!)",
                text_color="red"
            )

        if login_account(password):
            self.status_label.configure(text="Login successful. Loading...", text_color="green")
            self.after(5000, self.show_vault_screen)
            self.key = derive_key(password, self.salt)
            self.vault = VaultDB(self.key)
        else:
            self.status_label.configure(text="Wrong password", text_color="red")


    # Vault (please stop hoping..)


    def show_vault_screen(self):
        self.clear_screen()

        ctk.CTkLabel(
            self.container,
            text="Your Password Vault",
            font=("Arial", 26, "bold")
        ).pack(pady=(20, 10))

        
        table_container = ctk.CTkFrame(self.container)
        table_container.pack(fill="both", expand=True, padx=20, pady=10)

        
        header = ctk.CTkFrame(table_container, fg_color="#2a2a2a")
        header.pack(fill="x")

        headers = ["ID", "Website", "Username", "Password"]
        widths = [60, 200, 180, 200]

        for i, (text, width) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(
                header,
                text=text,
                width=width,
                anchor="w",
                font=("Arial", 13, "bold")
            ).grid(row=0, column=i, padx=8, pady=8)

        
        self.vault_frame = ctk.CTkScrollableFrame(
            table_container,
            fg_color="transparent"
        )
        self.vault_frame.pack(fill="both", expand=True)

        entries = self.vault.get_entries()

        for row_index, entry in enumerate(entries):
            self.create_vault_row(
                row_index,
                entry["id"],
                entry["site"],
                entry["username"],
                entry["password"]
            )

        
        btn_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="+ Add Entry",
            command=self.show_add_entry_popup
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="- Remove Entry",
            fg_color="#8b1e1e",
            hover_color="#a82424",
            command=self.show_delete_entry_popup
        ).pack(side="left", padx=10)




    def create_vault_row(self, row, entry_id, site, username, password):
        bg = "#1f1f1f" if row % 2 == 0 else "#252525"

        frame = ctk.CTkFrame(
            self.vault_frame,
            fg_color=bg,
            corner_radius=8
        )
        frame.pack(fill="x", pady=4, padx=4)

        widths = [60, 200, 180]

        for i, value in enumerate([entry_id, site, username]):
            ctk.CTkLabel(
                frame,
                text=value,
                width=widths[i],
                anchor="w"
            ).grid(row=0, column=i, padx=8, pady=6)

        pw_frame = ctk.CTkFrame(frame, fg_color="transparent")
        pw_frame.grid(row=0, column=3, padx=8, pady=6, sticky="w")

        pw_label = ctk.CTkLabel(
            pw_frame,
            text="********",
            width=160,
            anchor="w"
        )
        pw_label.pack(side="left")
        pw_label.real_password = password
        pw_label.hidden = True

        eye_btn = ctk.CTkButton(
            pw_frame,
            image=self.eye_icon,
            text="",
            width=32,
            height=28,
            fg_color="transparent",
            hover_color="#333333",
            command=lambda l=pw_label: self.toggle_password(l)
        )
        eye_btn.pack(side="left", padx=6)

    def toggle_password(self, label):
        if label.hidden:
            label.configure(text=label.real_password)
        else:
            label.configure(text="*********")

        label.hidden = not label.hidden




    def show_delete_entry_popup(self):
        self.popup = ctk.CTkToplevel(self)
        self.popup.title("Remove entry")
        self.popup.geometry("400x350")
        self.popup.grab_set()

        remove_entryid = ctk.CTkEntry(self.popup, placeholder_text='Enter here the id from the entry you want to delete!')
        remove_entryid.pack(pady=10)



        ctk.CTkButton(
            self.popup,
            text="Delete",
            command=lambda: self.remove_entry(remove_entryid.get())

        ).pack(pady=20)

    def show_add_entry_popup(self):
        self.popup = ctk.CTkToplevel(self)
        self.popup.title("Add Entry")
        self.popup.geometry("400x350")
        self.popup.grab_set()

        site_entry = ctk.CTkEntry(self.popup, placeholder_text="Website")
        site_entry.pack(pady=10)

        username_entry = ctk.CTkEntry(self.popup, placeholder_text="Name")
        username_entry.pack(pady=10)

        password_entry = ctk.CTkEntry(self.popup, show="*", placeholder_text="Password")
        password_entry.pack(pady=10)

        ctk.CTkButton(
            self.popup,
            text="Save",
            command=lambda: self.save_entry(
                site_entry.get(),
                username_entry.get(),
                password_entry.get()
            )
        ).pack(pady=20)


    def remove_entry(self, entry_id):
        if not id:
            return
        
        self.vault.delete_entry(
            entry_id
            )

        self.popup.destroy()
        self.popup = None
        self.show_vault_screen()


    def save_entry(self, site, username, password):
        if not site or not password:
            return

        self.vault.add_entry(
            site,
            username,
            password
        )

        self.popup.destroy()
        self.popup = None
        self.show_vault_screen()


if __name__ == "__main__":
    app = PyPassapp()
    app.mainloop()
