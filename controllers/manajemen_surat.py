import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from bson import ObjectId
from utils.auth import login_or_token_required
manajemen_surat_bp = Blueprint("manajemen_surat_bp", __name__, url_prefix="/manajemen-surat")


# =========================
# 🗂️ Halaman Manajemen Surat
# =========================

@manajemen_surat_bp.route("/", methods=["GET", "POST"])
@login_or_token_required
def manajemen_surat():
    db = current_app.config.get("db")

    if request.method == "POST":
        file = request.files.get("file")
        nama_surat = request.form.get("nama_surat")
        keterangan = request.form.get("keterangan")
        tanggal = request.form.get("tanggal")

        if not file:
            flash("File tidak boleh kosong!", "danger")
            return redirect(url_for("manajemen_surat_bp.manajemen_surat"))

        filename = secure_filename(file.filename)
        upload_dir = os.path.join(current_app.root_path, "static/uploads/")
        os.makedirs(upload_dir, exist_ok=True)
        upload_path = os.path.join(upload_dir, filename)
        print("📂 Simpan ke:", upload_path) 
        file.save(upload_path)

        db.surat.insert_one({
            "nama_surat": nama_surat,
            "filename": filename,
            "keterangan": keterangan,
            "tanggal": tanggal
        })

        flash("Surat berhasil diupload!", "success")
        return redirect(url_for("manajemen_surat_bp.manajemen_surat"))

    items = list(db.surat.find())
    return render_template("lelang/manajemen_surat.html", items=items)


# =========================
# 🗑️ Hapus Surat
# =========================

@manajemen_surat_bp.route("/hapus/<item_id>", methods=["POST"])
@login_or_token_required
def hapus_surat(item_id):
    db = current_app.config.get("db")
    surat = db.surat.find_one({"_id": ObjectId(item_id)})

    if surat and surat.get("filename"):
        file_path = os.path.join(current_app.root_path, "static/uploads", surat["filename"])
        if os.path.exists(file_path):
            os.remove(file_path)

    db.surat.delete_one({"_id": ObjectId(item_id)})
    flash("Surat berhasil dihapus!", "success")
    return redirect(url_for("manajemen_surat_bp.manajemen_surat"))


# =========================
# ✏️ Edit Surat
# =========================

@manajemen_surat_bp.route("/edit/<item_id>", methods=["POST"])
@login_or_token_required
def edit_surat(item_id):
    db = current_app.config.get("db")

    nama_surat = request.form.get("nama_surat")
    keterangan = request.form.get("keterangan")
    tanggal = request.form.get("tanggal")
    file = request.files.get("file")

    update_data = {
        "nama_surat": nama_surat,
        "keterangan": keterangan,
        "tanggal": tanggal
    }

    if file and file.filename:
        filename = secure_filename(file.filename)
        upload_dir = os.path.join(current_app.root_path, "static/uploads")
        os.makedirs(upload_dir, exist_ok=True)
        upload_path = os.path.join(upload_dir, filename)
        file.save(upload_path)
        update_data["filename"] = filename

    db.surat.update_one({"_id": ObjectId(item_id)}, {"$set": update_data})
    flash("Surat berhasil diperbarui!", "success")
    return redirect(url_for("manajemen_surat_bp.manajemen_surat"))
