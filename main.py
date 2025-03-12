import customtkinter as ctk
import base64
import json
import os
from tkinter import messagebox
from pathlib import Path

# Initialize the customtkinter theme
ctk.set_appearance_mode("Light")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue", "green", "dark-blue"

# Define color palette
PRIMARY_COLOR = "#1E90FF"  # DodgerBlue
SECONDARY_COLOR = "#F0F0F0"  # Light Gray
TEXT_COLOR = "#000000"  # Black

# Define fixed file path for C:/Users/<YourUserName>/Documents/PasswordManager
# Modify the path to explicitly reference the "C:" drive Documents folder
USER_PROFILE = Path(os.getenv("USERPROFILE"))  # This retrieves the user's profile path
DOCUMENTS_PATH = USER_PROFILE / "Documents" / "PasswordManager"
DOCUMENTS_PATH.mkdir(parents=True, exist_ok=True)  # Create folder if it doesn't exist
DATA_FILE = DOCUMENTS_PATH / "passwords.json"

# Load saved passwords if the file exists
if not DATA_FILE.exists():
    with DATA_FILE.open("w") as data_file:
        json.dump({}, data_file)

with DATA_FILE.open("r") as data_file:
    password_data = json.load(data_file)

# Save passwords to the file
def save_passwords():
    with DATA_FILE.open("w") as data_file:
        json.dump(password_data, data_file)

# GUI functions
def save_password():
    name = name_entry.get()
    password = password_entry.get()

    if not name or not password:
        messagebox.showerror("Error", "Both fields are required!")
        return

    # Encode the password in base64
    encoded_password = base64.b64encode(password.encode()).decode()
    password_data[name] = encoded_password
    save_passwords()
    messagebox.showinfo("Success", f"Password saved successfully in {DATA_FILE}!")
    name_entry.delete(0, ctk.END)
    password_entry.delete(0, ctk.END)

def retrieve_password():
    name = name_entry.get()

    if not name:
        messagebox.showerror("Error", "Name field is required to retrieve a password!")
        return

    encoded_password = password_data.get(name)
    if encoded_password:
        # Decode the password from base64
        decoded_password = base64.b64decode(encoded_password.encode()).decode()
        messagebox.showinfo("Retrieved Password", f"The password for '{name}' is: {decoded_password}")
    else:
        messagebox.showerror("Error", f"No password found for '{name}'!")

# Create the main window
app = ctk.CTk()
app.title("Professional Password Manager")
app.geometry("450x350")

# Set background colors (use darker or lighter variants for contrast)
app.configure(bg=SECONDARY_COLOR)

# Add a title label with primary color
title_label = ctk.CTkLabel(app, text="Password Manager", font=("Arial", 26, "bold"), text_color=PRIMARY_COLOR)
title_label.pack(pady=20)

# Name entry
name_label = ctk.CTkLabel(app, text="Name:", font=("Arial", 14), text_color=TEXT_COLOR)
name_label.pack(pady=(10, 5))
name_entry = ctk.CTkEntry(app, width=350, placeholder_text="Enter the name")
name_entry.pack(pady=(5, 15))

# Password entry
password_label = ctk.CTkLabel(app, text="Password:", font=("Arial", 14), text_color=TEXT_COLOR)
password_label.pack(pady=(10, 5))
password_entry = ctk.CTkEntry(app, width=350, placeholder_text="Enter the password", show="*")
password_entry.pack(pady=(5, 20))

# Buttons (with primary color and hover effects)
button_frame = ctk.CTkFrame(app, fg_color=SECONDARY_COLOR)
button_frame.pack(pady=20)

save_button = ctk.CTkButton(button_frame, text="Save Password", command=save_password, fg_color=PRIMARY_COLOR, hover_color="#1C86EE")
save_button.grid(row=0, column=0, padx=10)

retrieve_button = ctk.CTkButton(button_frame, text="Retrieve Password", command=retrieve_password, fg_color=PRIMARY_COLOR, hover_color="#1C86EE")
retrieve_button.grid(row=0, column=1, padx=10)

# Footer with file save location
footer_label = ctk.CTkLabel(app, text=f"Passwords saved at: {DOCUMENTS_PATH}", font=("Arial", 10), text_color=TEXT_COLOR, wraplength=400)
footer_label.pack(side="bottom", pady=10)

# Run the application
app.mainloop()
