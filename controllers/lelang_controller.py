import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, current_app,request
from bson import ObjectId
from utils.auth import login_or_token_required
from models.lelang_model import (
    get_dashboard_data,
    get_barang_rusak_berat,  # ✅ Tambahkan fungsi ini
    update_barang,
    delete_barang,
    get_barang_by_id,
    insert_riwayat_lelang
)
from models.histori_mutasi_model import catat_mutasi

lelang_bp = Blueprint("lelang_bp", __name__, url_prefix="/lelang")

# --- INDEX ---

@lelang_bp.route("/")
def index():
    return redirect(url_for("lelang_bp.dashboard"))

# --- HALAMAN BARANG RUSAK BERAT ---

@lelang_bp.route("/barang-rusak")
@lelang_bp.route("/barang-rusak/<kategori>")
@login_or_token_required
def barang_rusak(kategori=None):
    db = current_app.config.get("db")

    # Ambil data dari database otomatis
    barang_list = get_barang_rusak_berat(db)

    # Jika difilter berdasarkan kategori
    if kategori and kategori != "Semua":
        barang_list = [b for b in barang_list if b.get("kategori") == kategori]
    # Filter hanya barang yang belum selesai dilelang
    barang_list = [b for b in barang_list if b.get("status_lelang") != "Selesai"]
    return render_template(
        "lelang/barang_rusak.html",
        barang_list=barang_list,
        selected_kategori=kategori
    )

# --- DASHBOARD LELANG ---
# @lelang_bp.route("/dashboard")
# def dashboard():
#     db = current_app.config.get("db")

#     # ✅ Ambil barang rusak berat yang belum dilelang
#     barang_rusak_berat = list(db.barang.find({"kondisi": "Rusak Berat"}))

#     # ✅ Ambil barang lelang yang sudah selesai
#     barang_selesai_lelang = list(db.barang_lelang.find({"status": "selesai"}))

#     # Gabungkan keduanya (bisa ditandai dengan flag asal data)
#     for b in barang_selesai_lelang:
#         b["asal_data"] = "barang_lelang"

#     for b in barang_rusak_berat:
#         b["asal_data"] = "barang"

#     barang_all = barang_rusak_berat + barang_selesai_lelang

#     # Statistik dashboard (sudah benar)
#     stats = get_dashboard_data(db)

#     # Ambil kategori dan jumlah barang per kategori (update realtime)
#     pipeline = [
#         {"$match": {"kondisi": "Rusak Berat", "kategori": {"$exists": True, "$ne": ""}}},
#         {"$group": {"_id": "$kategori", "total": {"$sum": 1}}}
#     ]
#     kategori_data = list(db.barang.aggregate(pipeline))
#     data_kategori = {d["_id"]: d["total"] for d in kategori_data}

#     return render_template(
#         "lelang/dashboard.html",
#         barang=barang_all,           # ✅ tampilkan semua barang
#         **stats,
#         data_kategori=data_kategori
#     )
@lelang_bp.route("/dashboard")
def dashboard():
    db = current_app.config.get("db")

    # ✅ Ambil semua barang rusak berat dari tabel barang
    barang_rusak_berat = list(db.barang.find({"kondisi": "Rusak Berat"}))
    for b in barang_rusak_berat:
        b["asal_data"] = "barang"
        b["status_lelang"] = "Belum"

    # ✅ Ambil semua barang dari tabel barang_lelang
    barang_lelang = list(db.barang_lelang.find())
    for b in barang_lelang:
        b["asal_data"] = "barang_lelang"
        # pastikan nilainya dalam huruf kecil agar konsisten
        status_val = b.get("status", "").lower()
        if status_val == "selesai":
            b["status_lelang"] = "Selesai"
        else:
            b["status_lelang"] = "Belum"

    # ✅ Gabungkan dua sumber data
    barang_all = barang_rusak_berat + barang_lelang

    # Statistik dashboard (pakai fungsi existing)
    stats = get_dashboard_data(db)

    # Ambil kategori dan jumlah barang per kategori
    pipeline = [
        {"$match": {"kondisi": "Rusak Berat", "kategori": {"$exists": True, "$ne": ""}}},
        {"$group": {"_id": "$kategori", "total": {"$sum": 1}}}
    ]
    kategori_data = list(db.barang.aggregate(pipeline))
    data_kategori = {d["_id"]: d["total"] for d in kategori_data}

    return render_template(
        "lelang/dashboard.html",
        barang=barang_all,
        **stats,
        data_kategori=data_kategori
    )

# --- SELESAIKAN LELANG ---

@lelang_bp.route("/selesai/<item_id>", methods=["POST"])
@login_or_token_required
def selesai_lelang(item_id):
    db = current_app.config.get("db")
    barang = get_barang_by_id(db, item_id)

    if not barang:
        flash("Barang tidak ditemukan!", "danger")
        return redirect(url_for("lelang_bp.dashboard"))

    # 📝 Tambahkan informasi tanggal selesai lelang
    barang["status_lelang"] = "Selesai"
    barang["tanggal_selesai"] = datetime.now()

    # ✅ Simpan ke riwayat lelang
    insert_riwayat_lelang(db, barang)

    # ✅ Simpan juga ke tabel barang_lelang
    from models.lelang_model import insert_barang_lelang
    insert_barang_lelang(db, barang)

    # ✅ Catat mutasi
    catat_mutasi(
        barang_id=item_id,
        ruangan_asal_id=barang.get("ruangan_id"),
        ruangan_tujuan_id="luar_kantor",
        keterangan="Sudah Dilelang"
    )

    # ❌ Hapus dari tabel barang utama
    delete_barang(db, item_id)

    flash("✅ Barang berhasil dilelang, dipindahkan ke riwayat & dihapus dari tabel utama!", "success")
    return redirect(url_for("lelang_bp.dashboard"))


# --- UPDATE KATEGORI BARANG RUSAK ---

@lelang_bp.route("/set-kategori/<item_id>", methods=["POST"])
@login_or_token_required
def set_kategori(item_id):
    db = current_app.config.get("db")
    from flask import request

    kategori_baru = request.form.get("kategori")
    if not kategori_baru:
        flash("Kategori tidak boleh kosong!", "danger")
        return redirect(url_for("lelang_bp.barang_rusak"))

    update_barang(db, item_id, {"kategori": kategori_baru})
    flash("Kategori barang berhasil diperbarui!", "success")
    return redirect(url_for("lelang_bp.barang_rusak"))


# --- UPDATE STATUS LELANG ---

@lelang_bp.route("/set-status-lelang/<item_id>", methods=["POST"])
@login_or_token_required
def set_status_lelang(item_id):
    db = current_app.config.get("db")
    from flask import request

    status_baru = request.form.get("status_lelang")
    if not status_baru:
        flash("Status lelang tidak boleh kosong!", "danger")
        return redirect(url_for("lelang_bp.barang_rusak"))

    update_barang(db, item_id, {"status_lelang": status_baru})
    flash("Status lelang berhasil diperbarui!", "success")
    return redirect(url_for("lelang_bp.barang_rusak"))



@lelang_bp.route("/barang-lelang")
@login_or_token_required
def barang_lelang():
    db = current_app.config["db"]
    kategori = request.args.get("kategori")

    # Ambil hanya barang yang rusak berat
    query = {"kondisi": "Rusak Berat"}

    if kategori and kategori != "Semua":
        query["kategori"] = kategori
        selected_kategori = kategori
    else:
        selected_kategori = "Semua"

    items = list(db.barang.find(query))
    kategori_list = db.barang.distinct("kategori", {"kondisi": "Rusak Berat"})

    return render_template(
        "lelang/barang_lelang.html",
        items=items,
        kategori_list=kategori_list,
        selected_kategori=selected_kategori
    )


@lelang_bp.route("/set-harga-tawar/<item_id>", methods=["POST"])
@login_or_token_required
def set_harga_tawar(item_id):
    db = current_app.config.get("db")
    harga_tawar = request.form.get("harga_tawar")
    if harga_tawar:
        update_barang(db, item_id, {"harga_tawar": float(harga_tawar)})
        flash("Harga tawar berhasil diperbarui!", "success")
    return redirect(url_for("lelang_bp.barang_rusak"))

@lelang_bp.route("/set-limit-akhir/<item_id>", methods=["POST"])
@login_or_token_required
def set_limit_akhir(item_id):
    db = current_app.config.get("db")
    limit_akhir = request.form.get("limit_akhir")
    if limit_akhir:
        update_barang(db, item_id, {"limit_akhir": float(limit_akhir)})
        flash("Limit akhir berhasil diperbarui!", "success")
    return redirect(url_for("lelang_bp.barang_rusak"))


@lelang_bp.route("/riwayat-lelang")
@login_or_token_required
def riwayat_lelang():
    db = current_app.config.get("db")
    # Ambil semua barang dari riwayat_lelang
    items = list(db.riwayat_lelang.find())
    
    # Buat list tahun unik dari tanggal_selesai
    tahun_list = sorted({item['tanggal_selesai'].year for item in items}, reverse=True)
    selected_tahun = request.args.get('tahun')

    # Filter jika ada tahun yang dipilih
    if selected_tahun:
        items = [i for i in items if str(i['tanggal_selesai'].year) == selected_tahun]

    return render_template(
        "lelang/riwayat_lelang.html",
        items=items,
        tahun_list=tahun_list,
        selected_tahun=selected_tahun
    )

from flask import current_app, flash, redirect, url_for
from bson import ObjectId

# --- UPDATE DESKRIPSI BARANG ---

@lelang_bp.route("/set-deskripsi/<item_id>", methods=["POST"])
@login_or_token_required
def set_deskripsi(item_id):
    db = current_app.config.get("db")
    deskripsi_baru = request.form.get("deskripsi")
    if deskripsi_baru is None:
        flash("Deskripsi tidak boleh kosong!", "danger")
        return redirect(url_for("lelang_bp.barang_rusak"))

    update_barang(db, item_id, {"deskripsi": deskripsi_baru})
    flash("Deskripsi barang berhasil diperbarui!", "success")
    return redirect(url_for("lelang_bp.barang_rusak"))


@lelang_bp.route("/kembalikan-lelang/<item_id>", methods=["POST"])
@login_or_token_required
def kembalikan_lelang(item_id):
    db = current_app.config.get("db")

    # Cari data dari riwayat lelang
    barang_riwayat = db.riwayat_lelang.find_one({"_id": ObjectId(item_id)})
    if not barang_riwayat:
        flash("Data riwayat lelang tidak ditemukan!", "danger")
        return redirect(url_for("lelang_bp.riwayat_lelang"))

    # Hapus _id lama agar tidak bentrok saat insert ulang
    barang_riwayat.pop("_id", None)
    barang_riwayat["status_lelang"] = "Belum"  # dikembalikan ke kondisi awal

    # Masukkan kembali ke tabel barang utama
    db.barang.insert_one(barang_riwayat)

    # 🧹 Hapus dari tabel barang_lelang juga
    db.barang_lelang.delete_one({"barang_id": barang_riwayat.get("barang_id")})

    # Hapus dari riwayat lelang
    db.riwayat_lelang.delete_one({"_id": ObjectId(item_id)})

    flash("✅ Barang berhasil dikembalikan ke daftar barang utama dan dihapus dari lelang!", "success")
    return redirect(url_for("lelang_bp.riwayat_lelang"))
