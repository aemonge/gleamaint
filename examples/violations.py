"""Example module with typical Python patterns that violate Gleam principles"""

import logging
from typing import Optional

# Global mutable state
cache = {}
counter = 0


class UserService:
    """Traditional OOP service with inheritance"""

    def __init__(self):
        self.users = []  # Mutable list
        self.config = {"debug": True}  # Mutable dict

    def add_user(self, name: str, age: int):
        """Add user with exception-based error handling"""
        if age < 0:
            raise ValueError("Age cannot be negative")

        user = {"name": name, "age": age, "id": self.generate_id()}
        self.users.append(user)
        return user

    def generate_id(self):
        global counter
        counter += 1
        return counter

    def find_user(self, name: str) -> Optional[dict]:
        """Find user with imperative loop"""
        for user in self.users:
            if user["name"] == name:
                return user
        return None

    def update_config(self, key: str, value):
        """Direct mutation of config"""
        self.config[key] = value
        cache[key] = value  # Global state mutation


def process_data(items):
    """Process items with imperative style"""
    results = []
    for item in items:
        try:
            result = item * 2
            results.append(result)
        except Exception as e:
            logging.error(f"Failed to process {item}: {e}")
            continue
    return results
