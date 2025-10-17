from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.pengaturan_model import get_pengaturan, update_pengaturan
from utils.auth import login_or_token_required 

pengaturan_bp = Blueprint("pengaturan", __name__)

@pengaturan_bp.route("/pengaturan", methods=["GET", "POST"])
@login_or_token_required
def pengaturan():
    if request.method == "POST":
        update_pengaturan(
            request.form["nama_pengguna"],
            request.form["nip_pengguna"],
            request.form["nama_pengurus"],
            request.form["nip_pengurus"]
        )
        flash("Pengaturan berhasil diperbarui", "success")
        return redirect(url_for("pengaturan.pengaturan"))

    data = get_pengaturan()
    return render_template("pengaturan/form.html", data=data)
