import json
import os
import hashlib
import getpass
from dotenv import load_dotenv

load_dotenv()

PASSWORD_SALT = os.getenv("PASSWORD_SALT")
if not PASSWORD_SALT:
    print("Ошибка: PASSWORD_SALT не найден в .env")
    exit(1)

def hash_password(password: str) -> str:
    return hashlib.sha256((password + PASSWORD_SALT).encode()).hexdigest().lower()

def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def main():
    users = load_users()
    print("Добавление нового пользователя")
    username = input("Логин (username): ").strip()
    if not username:
        print("Логин не может быть пустым")
        return
    if username in users:
        print(f"Пользователь с логином '{username}' уже существует")
        return

    display_name = input("Отображаемое имя: ").strip()
    if not display_name:
        display_name = username

    password = getpass.getpass("Пароль: ")
    password_confirm = getpass.getpass("Повторите пароль: ")
    if password != password_confirm:
        print("Пароли не совпадают")
        return
    if not password:
        print("Пароль не может быть пустым")
        return

    balance_input = input("Баланс (число, по умолчанию 0): ").strip()
    try:
        balance = int(balance_input) if balance_input else 0
    except ValueError:
        print("Баланс должен быть числом, установлено 0")
        balance = 0

    password_hash = hash_password(password)
    users[username] = {
        "name": display_name,
        "password": password_hash,
        "balance": balance
    }
    save_users(users)
    print(f"Пользователь '{username}' успешно добавлен!")

if __name__ == "__main__":
    main()
