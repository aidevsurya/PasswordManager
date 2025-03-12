import customtkinter as ctk
import base64
import json
import os
from tkinter import messagebox, simpledialog
from pathlib import Path
from cryptography.fernet import Fernet

# Initialize the customtkinter theme
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("dark-blue")

# Define color palette
PRIMARY_COLOR = "#1E90FF"
TEXT_COLOR = "#000000"

# Define fixed file path
USER_PROFILE = Path(os.getenv("USERPROFILE"))
DOCUMENTS_PATH = USER_PROFILE / "Documents" / "PasswordManager"
DOCUMENTS_PATH.mkdir(parents=True, exist_ok=True)
DATA_FILE = DOCUMENTS_PATH / "passwords.json"

# Generate a key for encryption
def generate_key():
    return Fernet.generate_key()

# Save or load the key from file
def save_key(key):
    with open(DOCUMENTS_PATH / "secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    try:
        with open(DOCUMENTS_PATH / "secret.key", "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        return None

# Encrypt and decrypt functions
def encrypt_master_password(password, key):
    fernet = Fernet(key)
    encrypted = fernet.encrypt(password.encode())
    # Convert encrypted bytes to base64 string before saving to JSON
    return base64.b64encode(encrypted).decode()

def decrypt_master_password(encrypted_password, key):
    fernet = Fernet(key)
    # Decode base64 string to get the original encrypted bytes
    encrypted_bytes = base64.b64decode(encrypted_password.encode())
    decrypted = fernet.decrypt(encrypted_bytes).decode()
    return decrypted

# Load or initialize data with error handling
def load_data():
    try:
        with DATA_FILE.open("r") as data_file:
            return json.load(data_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"passwords": {}}  # Return an empty structure if file is missing or corrupt

# Initialize the password data
password_data = load_data()

# Save data to the file
def save_data():
    with DATA_FILE.open("w") as data_file:
        json.dump(password_data, data_file)

# First-time setup to create master password
def setup_master_password():
    while True:
        master_password = simpledialog.askstring(
            "Setup Master Password",
            "Create a master password:",
            show="*"
        )
        if master_password is None:
            return  # If the user cancels, exit the setup

        confirm_password = simpledialog.askstring(
            "Confirm Master Password",
            "Re-enter the master password to confirm:",
            show="*"
        )

        if not master_password or not confirm_password:
            messagebox.showerror("Error", "Master password cannot be empty!")
        elif master_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match! Try again.")
        else:
            key = generate_key()
            save_key(key)
            encrypted_password = encrypt_master_password(master_password, key)
            password_data["master_password"] = encrypted_password
            save_data()
            messagebox.showinfo("Success", "Master password created successfully!")
            break

# Check master password on subsequent runs
def verify_master_password_input():
    while True:
        entered_password = simpledialog.askstring(
            "Master Password",
            "Enter your master password:",
            show="*"
        )

        if entered_password is None:
            messagebox.showinfo("Exit", "Exiting the application.")  # Display a message when canceled
            exit()  # Exit the application

        key = load_key()
        if key:
            encrypted_master_password = password_data.get("master_password")
            if encrypted_master_password:
                try:
                    decrypted_password = decrypt_master_password(encrypted_master_password, key)
                    if entered_password == decrypted_password:
                        return entered_password
                except:
                    pass
        messagebox.showerror("Error", "Incorrect master password! Try again.")

# Encrypt and decrypt passwords using the master password
def encrypt_password(password, master_password):
    # Encrypt password with master password and convert it to base64
    return base64.b64encode(f"{master_password}{password}".encode()).decode()

def decrypt_password(encrypted_password, master_password):
    decoded = base64.b64decode(encrypted_password).decode()
    if decoded.startswith(master_password):
        return decoded[len(master_password):]
    raise ValueError("Incorrect master password!")

# GUI functions
def save_password(master_password):
    service = service_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    if not service or not username or not password:
        messagebox.showerror("Error", "All fields are required!")
        return

    if service not in password_data["passwords"]:
        password_data["passwords"][service] = {}

    if username in password_data["passwords"][service]:
        overwrite = messagebox.askyesno(
            "Confirmation",
            f"A password for '{username}' under service '{service}' already exists. Overwrite?"
        )
        if not overwrite:
            return

    encrypted_password = encrypt_password(password, master_password)
    password_data["passwords"][service][username] = encrypted_password
    save_data()
    messagebox.showinfo("Success", "Password saved successfully!")
    service_entry.delete(0, ctk.END)
    username_entry.delete(0, ctk.END)
    password_entry.delete(0, ctk.END)

def retrieve_password(master_password):
    selected_service = service_dropdown.get()
    selected_username = username_dropdown.get()

    if not selected_service or selected_service == "Select a service":
        messagebox.showerror("Error", "Please select a service!")
        return

    if not selected_username or selected_username == "Select a username":
        messagebox.showerror("Error", "Please select a username!")
        return

    encrypted_password = password_data["passwords"][selected_service][selected_username]
    try:
        decrypted_password = decrypt_password(encrypted_password, master_password)
        messagebox.showinfo("Retrieved Password", f"Service: {selected_service}\nUsername: {selected_username}\nPassword: {decrypted_password}")
    except ValueError:
        messagebox.showerror("Error", "Failed to decrypt password. Master password may be incorrect!")

# Open save window
def open_save_window():
    master_password = verify_master_password_input()

    save_window = ctk.CTkToplevel()
    save_window.title("Save Password")
    save_window.geometry("400x400")

    ctk.CTkLabel(save_window, text="Save Password", font=("Arial", 22, "bold"), text_color=PRIMARY_COLOR).pack(pady=20)
    global service_entry, username_entry, password_entry

    ctk.CTkLabel(save_window, text="Service:", font=("Arial", 14), text_color=TEXT_COLOR).pack(pady=(10, 5))
    service_entry = ctk.CTkEntry(save_window, width=300, placeholder_text="Enter the service name")
    service_entry.pack(pady=(5, 15))

    ctk.CTkLabel(save_window, text="Username:", font=("Arial", 14), text_color=TEXT_COLOR).pack(pady=(10, 5))
    username_entry = ctk.CTkEntry(save_window, width=300, placeholder_text="Enter the username")
    username_entry.pack(pady=(5, 15))

    ctk.CTkLabel(save_window, text="Password:", font=("Arial", 14), text_color=TEXT_COLOR).pack(pady=(10, 5))
    password_entry = ctk.CTkEntry(save_window, width=300, placeholder_text="Enter the password", show="*")
    password_entry.pack(pady=(5, 20))

    ctk.CTkButton(save_window, text="Save Password", command=lambda: save_password(master_password), fg_color=PRIMARY_COLOR).pack(pady=10)

# Open retrieve window
def open_retrieve_window():
    master_password = verify_master_password_input()
    retrieve_window = ctk.CTkToplevel()
    retrieve_window.title("Retrieve Password")
    retrieve_window.geometry("400x400")

    ctk.CTkLabel(retrieve_window, text="Retrieve Password", font=("Arial", 22, "bold"), text_color=PRIMARY_COLOR).pack(pady=20)
    global service_dropdown, username_dropdown

    ctk.CTkLabel(retrieve_window, text="Service:", font=("Arial", 14), text_color=TEXT_COLOR).pack(pady=(10, 5))
    service_dropdown = ctk.CTkOptionMenu(
        retrieve_window,
        values=["Select a service"] + list(password_data["passwords"].keys()),
        command=lambda selected_service: update_usernames(master_password, selected_service)
    )
    service_dropdown.set("Select a service")
    service_dropdown.pack(pady=(5, 15))

    ctk.CTkLabel(retrieve_window, text="Username:", font=("Arial", 14), text_color=TEXT_COLOR).pack(pady=(10, 5))
    username_dropdown = ctk.CTkOptionMenu(retrieve_window, values=["Select a service first"])
    username_dropdown.set("Select a service first")
    username_dropdown.pack(pady=(5, 15))

    ctk.CTkButton(retrieve_window, text="Retrieve Password", command=lambda: retrieve_password(master_password), fg_color=PRIMARY_COLOR).pack(pady=10)

def update_usernames(master_password, selected_service):
    if selected_service == "Select a service":
        username_dropdown.configure(values=["Select a service first"])
        username_dropdown.set("Select a service first")
    else:
        usernames = list(password_data["passwords"][selected_service].keys())
        if usernames:
            username_dropdown.configure(values=usernames)
            username_dropdown.set(usernames[0])
        else:
            username_dropdown.configure(values=["No usernames found"])
            username_dropdown.set("No usernames found")

# Main menu
def main_menu():
    menu = ctk.CTk()
    menu.title("Password Manager Menu")
    menu.geometry("300x200")

    
    ctk.CTkLabel(menu, text="Choose an Action", font=("Arial", 18, "bold"), text_color=PRIMARY_COLOR).pack(pady=30)
    ctk.CTkButton(menu, text="Save Password", command=open_save_window, fg_color=PRIMARY_COLOR).pack(pady=10)
    ctk.CTkButton(menu, text="Retrieve Password", command=open_retrieve_window, fg_color=PRIMARY_COLOR).pack(pady=10)

    menu.mainloop()

# # Initialize and check master password
if "master_password" not in password_data:
    setup_master_password()
else:
    main_menu()
