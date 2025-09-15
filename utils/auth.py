# utils/auth.py
from flask import request, session, abort,redirect, url_for
from config import PUBLIC_TOKENS

def login_or_token_required(func):
    def wrapper(*args, **kwargs):
        # Jika sudah login
        if 'username' in session:
            return func(*args, **kwargs)

        # Jika pakai token
        token = request.args.get("token")
        if token and token in PUBLIC_TOKENS:
            return func(*args, **kwargs)

        # Kalau gak lolos
        return redirect(url_for("auth.login"))
    wrapper.__name__ = func.__name__
    return wrapper
