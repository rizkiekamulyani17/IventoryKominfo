from flask import Blueprint, render_template, redirect, url_for, flash, request
from utils.auth import login_or_token_required
from models.histori_mutasi_model import get_all_histori, hapus_histori
from models.barang_model import get_barang_by_id
from models.ruangan_model import get_ruangan_by_id

histori_mutasi_bp = Blueprint('histori_mutasi', __name__, url_prefix='/histori_mutasi')


@histori_mutasi_bp.route('/', methods=['GET'])
@login_or_token_required
def index():
    histori_list = get_all_histori()

    for h in histori_list:
        h['id'] = str(h['_id'])

        # Ambil snapshot barang (kalau ada di histori) atau fallback ke get_barang_by_id
        barang = h.get('snapshot_barang') or get_barang_by_id(h.get('barang_id'))
        if barang:
            h['nama_barang'] = barang.get('nama_barang', '-')
            h['merk'] = barang.get('merk', '-')
            h['no_seri'] = barang.get('no_seri', '-')
            h['ukuran'] = barang.get('ukuran', '-')
            h['bahan'] = barang.get('bahan', '-')
            h['tahun'] = barang.get('tahun', '-')
            h['jumlah'] = barang.get('jumlah', 0)
            h['kondisi'] = barang.get('kondisi', '-')
            h['kode_barang'] = barang.get('kode_barang', '-')
            h['harga_beli'] = barang.get('harga_beli', '-')
            h['keterangan'] = barang.get('keterangan', '-')
        else:
            # fallback kalau barang sudah dihapus
            h['nama_barang'] = '[Barang tidak ditemukan]'
            h['merk'] = h['no_seri'] = h['ukuran'] = h['bahan'] = "-"
            h['tahun'] = h['jumlah'] = h['kondisi'] = "-"
            h['kode_barang_manual'] = h['harga_beli'] = h['keterangan'] = "-"

        # Ruangan Asal
        if h.get('ruangan_asal_id'):
            ruangan_asal = get_ruangan_by_id(h['ruangan_asal_id'])
            h['nama_ruangan_asal'] = ruangan_asal['nama_ruangan'] if ruangan_asal else '-'
        else:
            h['nama_ruangan_asal'] = 'Belum Ada'

        # Ruangan Tujuan
        if h.get('ruangan_tujuan_id'):
            ruangan_tujuan = get_ruangan_by_id(h['ruangan_tujuan_id'])
            h['nama_ruangan_tujuan'] = ruangan_tujuan['nama_ruangan'] if ruangan_tujuan else '-'
        else:
            h['nama_ruangan_tujuan'] = h.get('keterangan_luar', 'Luar Kantor')

    return render_template('histori_mutasi.html', histori_list=histori_list)


@histori_mutasi_bp.route('/hapus/<id>', methods=['POST'])
@login_or_token_required
def hapus(id):
    result = hapus_histori(id)
    if result.deleted_count:
        flash("✅ Data histori berhasil dihapus.", "success")
    else:
        flash("⚠️ Data histori tidak ditemukan.", "warning")
    return redirect(url_for('histori_mutasi.index'))



