from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file, abort
from werkzeug.utils import safe_join

from models.barang_model import tambah_barang, get_all_barang, get_all_barang2,hapus_barang, get_barang_by_id, update_kondisi_barang, update_barang,get_barang_by_kode_manual,get_semua_barang
from models.ruangan_model import get_semua_ruangan

barang_bp = Blueprint('barang', __name__, url_prefix='/barang')

from config import PUBLIC_TOKENS
from utils.auth import login_or_token_required  


@barang_bp.route('/')
@login_or_token_required
def index():
    barang = get_all_barang()
    return render_template('barang.html', barang=barang)

# @barang_bp.route('/all')
# @login_or_token_required
# def all_barang():
#     barang = get_all_barang()  # sudah ada nama_ruangan
#     return render_template('all_barang.html', barang=barang)

@barang_bp.route('/all')
@login_or_token_required
def all_barang():
    barang = get_all_barang()
    q = request.args.get("q", "").strip().lower()

    if q:
        barang = [
            b for b in barang 
            if q in (b.get('nama_barang') or '').lower()
            or q in (b.get('merk') or '').lower()
            or q in (b.get('nama_ruangan') or '').lower()
            or q in str(b.get('tahun') or '').lower()
        ]

    return render_template('all_barang.html', barang=barang)

@barang_bp.route('/hapus/<barang_id>')
@login_or_token_required
def hapus(barang_id):
    hapus_barang(barang_id)
    flash("Barang berhasil dihapus", "success")
    return redirect(url_for('barang.index'))


@barang_bp.route('/detail/<barang_id>')
def detail(barang_id):
    barang = get_barang_by_id(barang_id)
    return render_template('detail_barang.html', barang=barang)
@barang_bp.route('/detail2/<barang_id>')
def detail2(barang_id):
    barang = get_barang_by_id(barang_id)
    return render_template('detail_barang2.html', barang=barang)

@barang_bp.route('/edit_kondisi/<barang_id>', methods=['GET', 'POST'])
@login_or_token_required
def edit_kondisi(barang_id):
    barang = get_barang_by_id(barang_id)
    
    if request.method == 'POST':
        kondisi_baru = request.form['kondisi']
        update_kondisi_barang(barang_id, kondisi_baru)
        flash("Kondisi barang berhasil diperbarui", "success")

        # Redirect ke detail ruangan setelah update
        return redirect(url_for('ruangan.detail', ruangan_id=str(barang['ruangan_id'])))
    
    return render_template('edit_kondisi_barang.html', barang=barang)


@barang_bp.route('/download_qris/<barang_id>')
@login_or_token_required
def download_qris(barang_id):
    barang = get_barang_by_id(barang_id)
    if not barang:
        abort(404)
    
    # nama file berdasarkan NamaBarang_No
    filename = f"{barang['nama_barang'].replace(' ', '_')}_{barang['no']}.png"
    file_path = safe_join('static', 'qris', f"{barang['kode_barang']}.png")
    
    return send_file(file_path, as_attachment=True, download_name=filename)

@barang_bp.route('/tambah', methods=['GET', 'POST'])
@login_or_token_required
def tambah():
    import os
    from werkzeug.utils import secure_filename

    ruangan_list = get_semua_ruangan()

    if request.method == 'POST':
        data = {
            "nama_barang": request.form.get('nama_barang', '').strip(),
            "merk": request.form.get('merk', '').strip(),
            "no_seri": request.form.get('no_seri', '').strip(),
            "ukuran": request.form.get('ukuran', '').strip(),
            "bahan": request.form.get('bahan', '').strip(),
            "tahun": request.form.get('tahun', '').strip(),
            "jumlah": int(request.form.get('jumlah', 1)),
            "kondisi": request.form.get('kondisi', 'Baik'),
            "ruangan_id": request.form.get('ruangan_id'),
            "kode_barang_manual": request.form.get('kode_barang_manual', '').strip(),
            "harga_beli": request.form.get('harga_beli', '').strip(),
            "keterangan": request.form.get('keterangan', '').strip()
        }

        # 📸 Handle foto upload
        foto_file = request.files.get("foto")
        if foto_file and foto_file.filename:
            filename = secure_filename(foto_file.filename)
            save_path = os.path.join("static/uploads/barang", filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            foto_file.save(save_path)
            data["foto"] = save_path.replace("\\", "/")  # simpan path relatif
        else:
            data["foto"] = None

        # Validasi kode barang
        if not data['kode_barang_manual']:
            flash("Kode barang manual harus diisi!", "danger")
            return redirect(url_for('barang.tambah'))

        try:
            data['harga_beli'] = int(data['harga_beli']) if data['harga_beli'] else 0
        except ValueError:
            flash("Harga beli harus berupa angka!", "danger")
            return redirect(url_for('barang.tambah'))

        tambah_barang(data)
        flash("Barang berhasil ditambahkan", "success")
        return redirect(url_for('barang.index'))

    return render_template('tambah_barang.html', ruangan_list=ruangan_list)

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "static/uploads/barang"

@barang_bp.route('/edit/<barang_id>', methods=['GET', 'POST'])
@login_or_token_required
def edit(barang_id):
    barang = get_barang_by_id(barang_id)
    if not barang:
        flash("Barang tidak ditemukan", "danger")
        return redirect(url_for('barang.index'))

    ruangan_list = get_semua_ruangan()

    if request.method == 'POST':
        data_baru = {
            "nama_barang": request.form.get('nama_barang', '').strip(),
            "kode_barang": request.form.get('kode_barang', '').strip(),
            "merk": request.form.get('merk', '').strip(),
            "no_seri": request.form.get('no_seri', '').strip(),
            "ukuran": request.form.get('ukuran', '').strip(),
            "bahan": request.form.get('bahan', '').strip(),
            "tahun": request.form.get('tahun', '').strip(),
            "jumlah": int(request.form.get('jumlah', 1)),
            "kondisi": request.form.get('kondisi', 'Baik'),
            "ruangan_id": request.form.get('ruangan_id'),
            "harga_beli": int(request.form.get('harga_beli', 0)),
            "keterangan": request.form.get('keterangan', '').strip()
        }

        # 🔹 Cek apakah ada file foto baru
        file = request.files.get("foto")
        if file and file.filename:
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            file.save(save_path)
            # Simpan path relatif (pakai / bukan \)
            data_baru["foto"] = save_path.replace("\\", "/")

        update_barang(barang_id, data_baru)
        flash("Data barang berhasil diperbarui", "success")
        return redirect(url_for('barang.index'))

    return render_template('edit_barang.html', barang=barang, ruangan_list=ruangan_list)

@barang_bp.route('/detail_data/<kode>')
def detail_data(kode):
    from models.ruangan_model import get_ruangan_by_id
    from models.barang_model import get_barang_by_kode_manual

    merk = request.args.get("merk")
    tahun = request.args.get("tahun")
    harga = request.args.get("harga", type=int)
    ruangan_id = request.args.get("ruangan_id")  # ✅ ambil ruangan_id, bukan kode_ruangan

    print("DEBUG:", kode, merk, tahun, harga, ruangan_id)
    items = get_barang_by_kode_manual(kode, merk, tahun, harga, ruangan_id)

    for item in items:
        if "ruangan_id" in item:
            ruangan_obj = get_ruangan_by_id(item["ruangan_id"])
            item["nama_ruangan"] = ruangan_obj["nama_ruangan"] if ruangan_obj else "Tidak diketahui"
        else:
            item["nama_ruangan"] = "Tidak diketahui"
        item["_id"] = str(item["_id"])

    return render_template("detail_data.html", kode=kode, items=items)

@barang_bp.route('/barang/list')
def list_barang():
    barang_list = get_semua_barang()
    print(barang_list)  # debug
    return render_template('list_barang.html', barang_list=barang_list)
