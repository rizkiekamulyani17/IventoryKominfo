from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.barang_model import get_all_barang, barang_collection
from models.ruangan_model import get_semua_ruangan2
from bson.objectid import ObjectId
from models.barang_model import get_all_barang, barang_collection, get_barang_by_id

from utils.auth import login_or_token_required 
mutasi_bp = Blueprint('mutasi', __name__, url_prefix='/mutasi')

def login_required(func):
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@mutasi_bp.route('/', methods=['GET'])
@login_or_token_required
def index():
    barang_list = get_all_barang()
    ruangan_list = get_semua_ruangan2()

    # Tambahkan nama ruangan langsung ke barang_list
    ruangan_dict = {str(r['_id']): r['nama_ruangan'] for r in ruangan_list}
    for b in barang_list:
        if b.get('ruangan_id'):
            b['nama_ruangan'] = ruangan_dict.get(b['ruangan_id'], 'Belum Ada')
        else:
            b['nama_ruangan'] = 'Belum Ada'

    # Debug: cek isi data sebelum dikirim ke template
    print("=== DEBUG BARANG LIST ===")
    print(barang_list)
    print("=== DEBUG RUANGAN LIST ===")
    print(ruangan_list)

    return render_template('mutasi.html', barang_list=barang_list, ruangan_list=ruangan_list)

# @mutasi_bp.route('/mutasi/<barang_id>', methods=['POST'])
# @login_or_token_required
# def mutasi_barang(barang_id):
#     ruangan_tujuan_id = request.form['ruangan_tujuan_id']
    
#     update_data = {}
#     if ruangan_tujuan_id == 'luar_kantor':
#         keterangan = request.form.get('keterangan_luar', '').strip()
#         if not keterangan:
#             flash("Keterangan tujuan luar kantor harus diisi!", "danger")
#             return redirect(url_for('mutasi.index'))
#         update_data['ruangan_id'] = None
#         update_data['keterangan_luar'] = keterangan
#     else:
#         update_data['ruangan_id'] = ObjectId(ruangan_tujuan_id)
#         update_data['keterangan_luar'] = ""  # reset keterangan jika sebelumnya luar kantor

#     barang_collection.update_one(
#         {"_id": ObjectId(barang_id)},
#         {"$set": update_data}
#     )
#     flash("Barang berhasil dimutasi")
#     return redirect(url_for('mutasi.index'))

from models.histori_mutasi_model import catat_mutasi

@mutasi_bp.route('/mutasi/<barang_id>', methods=['POST'])
@login_or_token_required
def mutasi_barang(barang_id):
    ruangan_tujuan_id = request.form['ruangan_tujuan_id']
    keterangan_luar = request.form.get('keterangan_luar', None)

    barang = get_barang_by_id(barang_id)
    ruangan_asal_id = barang.get('ruangan_id')

    # Update ruangan
    if ruangan_tujuan_id == "luar_kantor":
        barang_collection.update_one(
            {"_id": ObjectId(barang_id)},
            {"$set": {"ruangan_id": None, "keterangan_luar": keterangan_luar}}
        )
    else:
        barang_collection.update_one(
            {"_id": ObjectId(barang_id)},
            {"$set": {"ruangan_id": ObjectId(ruangan_tujuan_id), "keterangan_luar": None}}
        )

    # Catat histori
    catat_mutasi(barang_id, ruangan_asal_id, ruangan_tujuan_id, keterangan_luar)

    flash("Barang berhasil dimutasi")
    return redirect(url_for('mutasi.index'))
@mutasi_bp.route('/hapus_mutasi/<id>', methods=['POST'])
def hapus_mutasi(id):
    # logika hapus histori berdasarkan id
    flash("Data histori berhasil dihapus.", "success")
    return redirect(url_for('barang.histori'))
