from flask import Blueprint, render_template, redirect, url_for, flash
from models.histori_ruangan_model import get_semua_histori, get_histori_by_id
from utils.auth import login_or_token_required
from models.histori_ruangan_model import get_semua_histori, get_histori_by_id, hapus_histori as hapus_histori_model

histori_ruangan_bp = Blueprint("histori_ruangan", __name__, url_prefix="/histori_ruangan")

@histori_ruangan_bp.route("/")
@login_or_token_required
def index():
    data = get_semua_histori()
    return render_template("histori_ruangan.html", histori=data)

@histori_ruangan_bp.route("/hapus/<histori_id>", methods=["POST", "GET"])
@login_or_token_required
def hapus_histori(histori_id):
    if hapus_histori_model(histori_id):  # ✅ panggil fungsi dari model
        flash("Histori ruangan berhasil dihapus permanen", "success")
    else:
        flash("Gagal menghapus histori ruangan", "danger")
    return redirect(url_for("histori_ruangan.index"))

