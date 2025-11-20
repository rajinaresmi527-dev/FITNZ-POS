# File: FITNZ/admin_ui.py
import tkinter as tk
from tkinter import ttk
from ttkbootstrap.dialogs import Messagebox
import ttkbootstrap as bs
from . import database as db
# --- REMOVED the circular import: from .main_app_ui import MainAppPage ---

class AdminPage(bs.Toplevel):
    def _init_(self, parent, logged_in_user):
        super()._init_(parent)
        self.logged_in_user = logged_in_user
        self.title("Admin Panel - User Management")
        self.geometry("700x500")

        # Header
        ttk.Label(self, text="Staff Management", font=("Helvetica", 16, "bold"), bootstyle="inverse-secondary").pack(fill="x", pady=(0,10), ipady=10)

        # Main Layout
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(expand=True, fill="both")

        # User List (Treeview)
        tree_frame = ttk.Labelframe(main_frame, text="Current Users", padding=10, bootstyle="info")
        tree_frame.pack(side="left", fill="both", expand=True)

        cols = ("ID", "Role", "Name", "Username")
        self.user_tree = ttk.Treeview(tree_frame, columns=cols, show="headings", bootstyle="primary")
        for col in cols:
            self.user_tree.heading(col, text=col)
            self.user_tree.column(col, width=80)
        
        self.user_tree.pack(side="left", fill="both", expand=True)
        
        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.user_tree.yview)
        scroll.pack(side="right", fill="y")
        self.user_tree.configure(yscrollcommand=scroll.set)
        
        self.load_users()

        # Side Actions (Add/Delete)
        action_frame = ttk.Frame(main_frame, padding=(10, 0))
        action_frame.pack(side="right", fill="y")

        ttk.Button(action_frame, text="Refresh List", command=self.load_users, bootstyle="secondary-outline").pack(fill="x", pady=5)
        ttk.Separator(action_frame).pack(fill="x", pady=10)
        
        ttk.Button(action_frame, text="Add New User", command=self.open_add_user, bootstyle="success").pack(fill="x", pady=5)
        ttk.Button(action_frame, text="Delete Selected", command=self.delete_user, bootstyle="danger").pack(fill="x", pady=5)
        
        ttk.Button(action_frame, text="Close", command=self.destroy, bootstyle="dark-outline").pack(side="bottom", fill="x", pady=5)

    def load_users(self):
        for i in self.user_tree.get_children():
            self.user_tree.delete(i)
        
        for user in db.get_all_users():
            # Handle different ID attributes for Customer vs Employee
            uid = getattr(user, 'employee_id', getattr(user, '_customer_id', 'N/A'))
            name = getattr(user, 'name', getattr(user, '_name', 'N/A'))
            
            self.user_tree.insert("", "end", values=(uid, user.role, name, user.username))

    def delete_user(self):
        selected = self.user_tree.focus()
        if not selected: return
        
        values = self.user_tree.item(selected, "values")
        user_id = values[0]
        role = values[1]
        
        if user_id == "E001": # Protect the main developer account
            Messagebox.show_error("Cannot delete the main Developer account.", "Action Denied", parent=self)
            return

        if Messagebox.yesno(f"Permanently delete {role} '{values[2]}'?", "Confirm Delete", parent=self):
            if db.delete_user_by_id(user_id):
                Messagebox.show_info("User deleted.", "Success", parent=self)
                self.load_users()
            else:
                Messagebox.show_error("Could not delete user.", "Error", parent=self)

    def open_add_user(self):
        AddUserDialog(self)


class AddUserDialog(bs.Toplevel):
    def _init_(self, parent):
        super()._init_(parent)
        self.parent = parent
        self.title("Add User")
        self.geometry("400x450")
        
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Full Name:").pack(anchor="w")
        self.name_entry = ttk.Entry(frame); self.name_entry.pack(fill="x", pady=5)
        
        ttk.Label(frame, text="Contact (Email/Phone):").pack(anchor="w")
        self.contact_entry = ttk.Entry(frame); self.contact_entry.pack(fill="x", pady=5)
        
        ttk.Label(frame, text="Username:").pack(anchor="w")
        self.user_entry = ttk.Entry(frame); self.user_entry.pack(fill="x", pady=5)

        ttk.Label(frame, text="Password:").pack(anchor="w")
        self.pass_entry = ttk.Entry(frame); self.pass_entry.pack(fill="x", pady=5)
        
        ttk.Label(frame, text="Role:").pack(anchor="w")
        self.role_combo = ttk.Combobox(frame, values=["Employee", "Manager", "Customer"], state="readonly")
        self.role_combo.set("Employee")
        self.role_combo.pack(fill="x", pady=5)
        
        ttk.Button(frame, text="Save User", command=self.save, bootstyle="success").pack(fill="x", pady=20)

    def save(self):
        name = self.name_entry.get()
        contact = self.contact_entry.get()
        username = self.user_entry.get()
        password = self.pass_entry.get()
        role = self.role_combo.get()
        
        if not all([name, username, password, role]):
            Messagebox.show_error("All fields are required.", "Error", parent=self)
            return

        if db.add_user(name, contact, username, password, role, "N/A"):
            Messagebox.show_info(f"{role} added successfully!", "Success", parent=self)
            self.parent.load_users()
            self.destroy()
        else:
            Messagebox.show_error("Username likely already exists.", "Database Error", parent=self

