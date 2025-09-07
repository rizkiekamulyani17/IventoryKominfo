# controllers/akun_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import user_model  # ✅ pakai user_model

akun_bp = Blueprint('akun', __name__, url_prefix='/akun')

# 📌 Daftar akun
@akun_bp.route('/')
def list_akun():
    user_list = user_model.get_all_users()
    return render_template('akun/akun_list.html', akun_list=user_list)  # ✅ betulin variabel

# 📌 Tambah akun
@akun_bp.route('/tambah', methods=['GET', 'POST'])
def tambah_akun():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'user')
        user_model.create_admin(username, password) if role == "admin" else user_model.user_collection.insert_one({
            "username": username,
            "password_hash": user_model.generate_password_hash(password),
            "role": role
        })
        flash("Akun berhasil ditambahkan!", "success")
        return redirect(url_for('akun.list_akun'))
    return render_template('akun/akun_form.html')

# 📌 Edit akun
@akun_bp.route('/edit/<user_id>', methods=['GET', 'POST'])
def edit_akun(user_id):
    akun = user_model.get_user_by_id(user_id)
    if not akun:
        flash("Akun tidak ditemukan", "danger")
        return redirect(url_for('akun.list_akun'))

    if request.method == 'POST':
        username = request.form['username']
        role = request.form.get('role', 'user')
        user_model.update_user(user_id, {"username": username, "role": role})
        flash("Akun berhasil diperbarui!", "success")
        return redirect(url_for('akun.list_akun'))

    return render_template('akun/akun_form.html', akun=akun)

# 📌 Hapus akun
@akun_bp.route('/hapus/<user_id>', methods=['POST'])
def hapus_akun(user_id):
    user_model.delete_user(user_id)
    flash("Akun berhasil dihapus!", "success")
    return redirect(url_for('akun.list_akun'))

# 📌 Ganti password (user login sendiri)
@akun_bp.route('/ganti_password', methods=['GET', 'POST'])
def ganti_password():
    if 'user_id' not in session:
        flash("Silakan login terlebih dahulu", "danger")
        return redirect(url_for('auth.login'))

    akun = user_model.get_user_by_id(session['user_id'])
    if not akun:
        flash("Akun tidak ditemukan!", "danger")
        return redirect(url_for('akun.ganti_password'))

    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if not user_model.check_password_hash(akun['password_hash'], old_password):
            flash("Password lama salah!", "danger")
        elif new_password != confirm_password:
            flash("Konfirmasi password tidak cocok!", "danger")
        else:
            user_model.update_user(session['user_id'], {
                "password_hash": user_model.generate_password_hash(new_password)
            })
            flash("Password berhasil diganti!", "success")
            return redirect(url_for('akun.ganti_password'))

    return render_template('akun/akun_ganti_password.html')
