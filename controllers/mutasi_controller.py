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

    # Dictionary ruangan: kunci string
    ruangan_dict = {str(r['_id']): r['nama_ruangan'] for r in ruangan_list}

    filtered_barang = []
    for b in barang_list:
        # 🚫 Jangan tampilkan barang yang status lelangnya selesai
        if (b.get('status_lelang') or '').strip().lower() == 'selesai':
            continue

        ruangan_id = b.get('ruangan_id')
        if ruangan_id:
            b['nama_ruangan'] = ruangan_dict.get(str(ruangan_id), 'Belum Ada')
            b['keterangan_luar'] = ''
            filtered_barang.append(b)

    return render_template('mutasi.html', barang_list=filtered_barang, ruangan_list=ruangan_list)


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

    # Catat histori mutasi (opsional)
    from models.histori_mutasi_model import catat_mutasi
    catat_mutasi(barang_id, ruangan_asal_id, ruangan_tujuan_id, keterangan_luar)

    flash("Barang berhasil dimutasi")
    return redirect(url_for('mutasi.index'))
