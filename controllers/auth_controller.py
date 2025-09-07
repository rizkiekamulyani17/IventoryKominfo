from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user_model import verify_login

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        akun = verify_login(username, password)

        if akun:
            session['user_id'] = str(akun['_id'])   # simpan user_id
            session['username'] = akun['username']  # simpan username juga
            flash("Login berhasil!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Login gagal", "danger")
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))
