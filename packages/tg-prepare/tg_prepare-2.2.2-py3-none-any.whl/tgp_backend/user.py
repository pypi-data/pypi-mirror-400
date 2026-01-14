# -*- coding: utf-8 -*-
# Copyright (C) 2023-2025 TU-Dresden (ZIH)
# ralf.klammer@tu-dresden.de
# moritz.wilhelm@tu-dresden.de

import logging

import os
import json
import hashlib

from flask_login import UserMixin  # type: ignore

from .config import MAIN_PATH

log = logging.getLogger(__name__)


class User(UserMixin):
    def __init__(
        self,
        username,
        password_hash=None,
        email=None,
        role="user",
        is_active=True,
    ):
        self.id = username
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.role = role
        self._is_active = is_active  # Underscore prefix for internal attribute
        self.last_login = None

    @property
    def is_active(self):
        """Return True if the user is active."""
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        """Set the active status of the user."""
        self._is_active = value

    def check_password(self, password):
        """Verify password against stored hash"""
        hashed = hashlib.sha256(password.encode()).hexdigest()
        return hashed == self.password_hash

    def to_dict(self):
        """Converts User to dictionary for JSON storage"""
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "email": self.email,
            "role": self.role,
            "is_active": self._is_active,  # Use internal attribute
            "last_login": self.last_login,
        }

    @staticmethod
    def from_dict(data):
        """Creates User object from dictionary"""
        user = User(
            username=data["username"],
            password_hash=data["password_hash"],
            email=data.get("email"),
            role=data.get("role", "user"),
            is_active=data.get("is_active", True),
        )
        user.last_login = data.get("last_login")
        return user


class UserManager:
    def __init__(self):
        self.users_file = os.path.join(MAIN_PATH, "users.json")
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        self.load_users()

    def load_users(self):
        """Loads users from JSON file"""
        self.users = {}
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, "r") as f:
                    users_data = json.load(f)
                    for username, data in users_data.items():
                        self.users[username] = User.from_dict(data)
                        self.initialize_user_folder(
                            username
                        )  # Initialisiere Benutzerordner
            except Exception as e:
                print(f"Error loading users: {e}")
                self.create_default_admin()
        else:
            self.create_default_admin()

    def save_users(self):
        """Saves users to JSON file"""
        users_data = {
            username: user.to_dict() for username, user in self.users.items()
        }
        with open(self.users_file, "w") as f:
            json.dump(users_data, f, indent=2)

    def get_user(self, username):
        """Returns user by username"""
        return self.users.get(username)

    def create_user(self, username, password, email=None, role="user"):
        """Creates new user"""
        if username in self.users:
            return False, "Username already taken"

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = User(username, password_hash, email, role)
        self.users[username] = user
        self.save_users()
        self.initialize_user_folder(username)  # Initialisiere Benutzerordner
        return True, "User created successfully"

    def create_default_admin(self):
        """Creates default admin user"""
        self.create_user("admin", "admin123", role="admin")
        print("Default admin user created (admin/admin123)")

    def initialize_user_folder(self, username):
        """Initialisiert den Benutzer-spezifischen Ordner"""
        user_folder = os.path.join(MAIN_PATH, username)
        os.makedirs(user_folder, exist_ok=True)
        log.info(f"Benutzerordner initialisiert: {user_folder}")

    def get_user_folder(self, username):
        """Gibt den Pfad des Benutzerordners zurück"""
        return os.path.join(MAIN_PATH, username)
