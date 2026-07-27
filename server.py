# FastAPI server
import base64
import hmac
import hashlib
import json
import os
from dotenv import load_dotenv
from typing import Optional

from fastapi import FastAPI, Cookie, Body
from fastapi.responses import Response


app = FastAPI()

load_dotenv()
SECRET_KEY = str(os.getenv("SECRET_KEY"))
PASSWORD_SALT = str(os.getenv("PASSWORD_SALT"))


def sign_data(data: str) -> str:
    """Возвращает подписанные данные дата"""
    return (hmac.new
        (
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256
        ).hexdigest().upper())

def get_username_from_signed_string(username_signed: str) -> Optional[str]:
    username_base64, sign = username_signed.split(".")
    username = base64.b64decode(username_base64.encode()).decode()
    valid_sing = sign_data(username)
    if hmac.compare_digest(valid_sing, sign):
        return username
    return None


def verify_password(username: str, password: str) -> bool:
    password_hash = hashlib.sha256( (password + PASSWORD_SALT).encode() ).hexdigest().lower()
    stored_password_hash = users[username]['password'].lower()
    return  stored_password_hash == password_hash



with open("users.json", "r") as db:
    users = json.load(db)



@app.get("/")
def index_page(username: Optional[str] = Cookie(default=None)):
    with open('templates/login.html') as f:
        login_page = f.read()
    if not username:
        return Response(login_page, media_type="text/html")
    valid_username = get_username_from_signed_string(username)
    if not valid_username:
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key="username")
        return response
    try:
        user = users[valid_username]
    except KeyError:
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key="username")
        return response
    return Response(f"Привет, {user['name']}", media_type="text/html")



@app.post("/login")
def process_login_page(data: dict = Body(..., media_type="text/plain")):
    print('Ваша data', data)
    username = data['username']
    password = data['password']
    user = users.get(username)
    if not user or not verify_password(username, password):
        return Response(
            json.dumps({
                    "success": False,
                    "message": "Ты кто такой?!"
            }),
            media_type="text/json")

    response = Response(
        json.dumps({
            "success": True,
            "message": f"Ваше имя: {user['name']}<br />Ваш баланс: {user['balance']}",
        }),
        media_type="text/json")

    username_signed = base64.b64encode(username.encode()).decode() + '.' + sign_data(username)
    response.set_cookie(key="username", value=username_signed)
    return response
