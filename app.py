from flask import Flask, render_template, session
from controllers.auth_controller import auth_bp
from controllers.ruangan_controller import ruangan_bp
from controllers.barang_controller import barang_bp
from controllers.mutasi_controller import mutasi_bp
from controllers.akun_controller import akun_bp
from controllers.histori_mutasi import histori_mutasi_bp
from models.ruangan_model import get_semua_ruangan
from models.barang_model import get_all_barang
from models.ruangan_model import get_ruangan_by_kode
from models.barang_model import get_barang_by_kode, get_barang_per_ruangan
from controllers.pengaturan_controller import pengaturan_bp
from controllers.histori_ruangan_controller import histori_ruangan_bp
from controllers.kondisi_controller import kondisi_bp
from controllers.lelang_controller import lelang_bp
from config import db
app = Flask(__name__)
app.secret_key = "secret123"
# Simpan ke config agar bisa diakses di controller
app.config["db"] = db
# Blueprints
from controllers.manajemen_surat import manajemen_surat_bp
app.register_blueprint(manajemen_surat_bp)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(ruangan_bp)
app.register_blueprint(barang_bp)
app.register_blueprint(mutasi_bp)
app.register_blueprint(akun_bp)
app.register_blueprint(histori_mutasi_bp)
app.register_blueprint(pengaturan_bp)
app.register_blueprint(histori_ruangan_bp)
app.register_blueprint(kondisi_bp)
app.register_blueprint(lelang_bp)
# @app.route('/')
# def dashboard():
#     ruangan_list = get_semua_ruangan()
#     barang_list = get_all_barang()

#     # Hitung total barang per ruangan
#     for r in ruangan_list:
#         r['_id'] = str(r['_id'])  # Supaya bisa di-url
#         r['total_barang'] = len(get_barang_per_ruangan(r['_id']))

#     return render_template('dashboard.html', ruangan=ruangan_list, barang=barang_list)




from models.kondisi_model import get_summary_kondisi
from models.lelang_model import get_dashboard_data

@app.route('/')
def dashboard():
    db = app.config["db"]
    ruangan_list = get_semua_ruangan()
    barang_list = get_all_barang()
    summary_kondisi = get_summary_kondisi()
    lelang_stats = get_dashboard_data(db)  # ✅ Tambahkan ini

    # Hitung total barang per ruangan
    for r in ruangan_list:
        r['_id'] = str(r['_id'])
        r['total_barang'] = len(get_barang_per_ruangan(r['_id']))

    kondisi_dict = {item['_id']: item['jumlah'] for item in summary_kondisi}

    return render_template(
        'dashboard.html',
        ruangan=ruangan_list,
        barang=barang_list,
        kondisi=kondisi_dict,
        total_selesai=lelang_stats.get("total_selesai", 0)  # ✅ kirim ke template
    )


@app.route('/dashboard/ruangan')
def dashboard_all_ruangan():
    ruangan_list = get_semua_ruangan()
    for r in ruangan_list:
        r['_id'] = str(r['_id'])
        r['total_barang'] = len(get_barang_per_ruangan(r['_id']))
    return render_template('all_ruangan.html', ruangan=ruangan_list)

@app.route('/dashboard/barang')
def dashboard_all_barang():
    barang_list = get_all_barang()
    return render_template('all_barang.html', barang=barang_list)


@app.route('/scan/<kode>')
def scan_qr(kode):
    # cek apakah kode adalah ruangan
    ruangan = get_ruangan_by_kode(kode)
    if ruangan:
        barang_list = get_barang_per_ruangan(ruangan['_id'])
        return render_template('scan_ruangan.html', ruangan=ruangan, barang_list=barang_list)
    
    # cek apakah kode adalah barang
    barang = get_barang_by_kode(kode)
    if barang:
        return render_template('scan_barang.html', barang=barang)
    
    return "QRIS tidak ditemukan", 404
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

