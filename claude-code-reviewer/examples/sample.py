"""
Sample Python file with intentional issues — use this to demo the reviewer.

Run:
    python -m reviewer.cli review examples/sample.py
"""

import os
import json
import requests


# ⚠️  Issue 1: Hardcoded API key (Critical — Security)
API_KEY = "sk-abc123supersecretkey"
BASE_URL = "https://api.example.com"


# ⚠️  Issue 2: Mutable default argument (Medium — Bug)
def fetch_users(limit=10, results=[]):
    """Fetch users from the API and append to results."""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(f"{BASE_URL}/users?limit={limit}", headers=headers)

    # ⚠️  Issue 3: No status-code check before .json() (High — Bug)
    data = response.json()
    results.extend(data.get("users", []))
    return results


# ⚠️  Issue 4: Bare except clause swallows all errors (High — Error Handling)
def load_config(path):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return {}


# ⚠️  Issue 5: SQL injection risk (Critical — Security)
def get_user_by_name(conn, username):
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE name = '{username}'"
    cursor.execute(query)
    return cursor.fetchone()


# ⚠️  Issue 6: Missing type hints and docstring (Low — Style)
def calculate_discount(price, pct):
    if pct > 1:
        pct = pct / 100
    return price * (1 - pct)


# ✅  Good: context manager used correctly
def save_report(data: dict, filepath: str) -> None:
    """Save a report dict to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    users = fetch_users(limit=5)
    print(f"Fetched {len(users)} users")
