from flask import Blueprint, render_template, redirect, url_for, flash
from utils.auth import login_or_token_required
from models.histori_mutasi_model import get_all_histori, hapus_histori
from models.barang_model import get_barang_by_id
from models.ruangan_model import get_ruangan_by_id
from bson.objectid import ObjectId

histori_mutasi_bp = Blueprint('histori_mutasi', __name__, url_prefix='/histori_mutasi')

@histori_mutasi_bp.route('/', methods=['GET'])
@login_or_token_required
def index():
    histori_list = get_all_histori()

    # Tambahkan detail barang & ruangan + konversi _id ke string
    for h in histori_list:
        h['id'] = str(h['_id'])
        barang = get_barang_by_id(h['barang_id'])
        h['nama_barang'] = barang['nama_barang'] if barang else '-'

        ruangan_asal = get_ruangan_by_id(h['ruangan_asal_id']) if h.get('ruangan_asal_id') else None
        h['nama_ruangan_asal'] = ruangan_asal['nama_ruangan'] if ruangan_asal else 'Belum Ada'

        ruangan_tujuan = get_ruangan_by_id(h['ruangan_tujuan_id']) if h.get('ruangan_tujuan_id') else None
        h['nama_ruangan_tujuan'] = ruangan_tujuan['nama_ruangan'] if ruangan_tujuan else 'Luar Kantor'

    return render_template('histori_mutasi.html', histori_list=histori_list)

@histori_mutasi_bp.route('/hapus/<id>', methods=['POST'])
@login_or_token_required
def hapus(id):
    result = hapus_histori(id)
    if result.deleted_count:
        flash("Data histori berhasil dihapus.", "success")
    else:
        flash("Data histori tidak ditemukan.", "warning")
    return redirect(url_for('histori_mutasi.index'))




