from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.ruangan_model import tambah_ruangan, get_semua_ruangan, hapus_ruangan, get_ruangan_by_id
from flask import send_file, abort
import os
import zipfile
from io import BytesIO
#from models.barang_model import get_barang_per_ruangan  # pastikan ada fungsi ini
from flask import send_file
from fpdf import FPDF
import io
from utils.auth import login_or_token_required  
from models.barang_model import get_barang_per_ruangan
from models.ruangan_model import get_ruangan_by_id
ruangan_bp = Blueprint('ruangan', __name__, url_prefix='/ruangan')



@ruangan_bp.route('/')
@login_or_token_required
def index():
    data = get_semua_ruangan()
    return render_template('ruangan.html', ruangan=data)

@ruangan_bp.route('/tambah', methods=['GET','POST'])
@login_or_token_required
def tambah():
    if request.method == 'POST':
        nama = request.form['nama_ruangan']
        kode_ruangan = request.form['kode_ruangan']
        kode_lokasi = request.form['kode_lokasi']
        
        tambah_ruangan(nama, kode_ruangan,kode_lokasi)
        flash("Ruangan berhasil ditambahkan")
        return redirect(url_for('ruangan.index'))
    return render_template('tambah_ruangan.html')

@ruangan_bp.route('/hapus/<ruangan_id>')
@login_or_token_required
def hapus(ruangan_id):
    hapus_ruangan(ruangan_id)
    flash("Ruangan berhasil dihapus")
    return redirect(url_for('ruangan.index'))



@ruangan_bp.route('/edit/<ruangan_id>', methods=['GET', 'POST'])
@login_or_token_required
def edit(ruangan_id):
    from models.ruangan_model import get_ruangan_by_id, update_ruangan
    ruangan = get_ruangan_by_id(ruangan_id)
    
    if request.method == 'POST':
        nama_baru = request.form['nama_ruangan']
        kode_ruangan_baru = request.form['kode_ruangan']   # ✅ ambil dari input kode_ruangan
        kode_lokasi_baru = request.form['kode_lokasi']     # ✅ ambil dari input kode_lokasi

        update_ruangan(ruangan_id, nama_baru, kode_ruangan_baru, kode_lokasi_baru)
        flash("Ruangan berhasil diperbarui")
        return redirect(url_for('ruangan.index'))
    
    return render_template('edit_ruangan.html', ruangan=ruangan)

@ruangan_bp.route('/detail/<ruangan_id>')
def detail(ruangan_id):
    ruangan = get_ruangan_by_id(ruangan_id)
    from models.barang_model import get_barang_per_ruangan
    barang = get_barang_per_ruangan(ruangan_id)

    search = request.args.get('search', '').lower().strip()

    if search:
        # Filter barang sesuai search input
        barang = [
            b for b in barang
            if search in str(b.get('nama_barang', '')).lower()
            or search in str(b.get('kode_barang', '')).lower()
            or search in str(b.get('merk', '')).lower()
            or search in str(b.get('tahun', '')).lower()
        ]

    # Urutkan barang berdasarkan 'tahun' ascending
    barang = sorted(barang, key=lambda x: int(x.get('tahun', 0)))

    return render_template('detail_ruangan.html', ruangan=ruangan, barang=barang)






@ruangan_bp.route('/scan/<kode_ruangan>')
def scan_ruangan(kode_ruangan):
    from models.ruangan_model import get_ruangan_by_kode
    ruangan = get_ruangan_by_kode(kode_ruangan)
    if not ruangan:
        abort(404, description="Ruangan tidak ditemukan")

    from models.barang_model import get_barang_per_ruangan
    barang_list = get_barang_per_ruangan(str(ruangan["_id"]))

    return render_template("scan_ruangan.html", ruangan=ruangan, barang_list=barang_list)





@ruangan_bp.route('/download_qris/<ruangan_id>')
@login_or_token_required
def download_qris_ruangan(ruangan_id):
    ruangan = get_ruangan_by_id(ruangan_id)
    if not ruangan:
        abort(404)

    file_path = os.path.join('static', 'qris', f"{ruangan['nama_ruangan']}.png")
    if not os.path.exists(file_path):
        abort(404)

    filename = f"{ruangan['nama_ruangan'].replace(' ', '_')}.png"
    return send_file(file_path, as_attachment=True, download_name=filename)

# @ruangan_bp.route('/download_semua_qris/<ruangan_id>')
# @login_required
# def download_semua_qris_barang(ruangan_id):
#     ruangan = get_ruangan_by_id(ruangan_id)
#     if not ruangan:
#         abort(404)

#     barang_list = get_barang_per_ruangan(ruangan_id)
#     if not barang_list:
#         flash("Tidak ada barang di ruangan ini")
#         return redirect(url_for('ruangan.detail', ruangan_id=ruangan_id))

#     # Buat zip di memori
#     memory_file = BytesIO()
#     with zipfile.ZipFile(memory_file, 'w') as zf:
#         for b in barang_list:
#             file_path = os.path.join('static', 'qris', f"{b['kode_barang']}.png")
#             if os.path.exists(file_path):
#                 zf.write(file_path, arcname=f"{b['kode_barang']}.png")
#     memory_file.seek(0)

#     return send_file(memory_file,
#                      download_name=f"{ruangan['nama_ruangan'].replace(' ','_')}_QRIS.zip",
#                      as_attachment=True)
@ruangan_bp.route('/download_qris_pdf/<ruangan_id>')
@login_or_token_required
def download_qris_pdf(ruangan_id):
    ruangan = get_ruangan_by_id(ruangan_id)
    if not ruangan:
        abort(404)

    barang_list = get_barang_per_ruangan(ruangan_id)

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Daftar QRIS Barang - {ruangan['nama_ruangan']}", ln=True, align='C')
    pdf.ln(10)

    x_start = 10
    y_start = pdf.get_y()
    col_width = 60   # lebar tiap kolom
    row_height = 35  # tinggi tiap baris
    col = 0

    for b in barang_list:
        x = x_start + col * col_width

        # Tambahkan bingkai
        pdf.rect(x, y_start, col_width, row_height)

        # Tambahkan QRIS
        qris_path = os.path.join('static', 'qris', f"{b['nama_barang']}.png")
        if os.path.exists(qris_path):
            pdf.image(qris_path, x=x+3, y=y_start+3, w=30, h=30)
            pdf.set_xy(x + 34, y_start + 5)
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(col_width-34, 5, f"{b['nama_barang']}\nKode: {b['kode_barang']}", border=0)

        col += 1
        if col >= 3:
            col = 0
            y_start += row_height
            if y_start + row_height > 285:  # batas bawah A4
                pdf.add_page()
                y_start = pdf.get_y()

    # Simpan ke memory buffer
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        download_name=f"{ruangan['nama_ruangan'].replace(' ', '_')}_QRIS.pdf",
        as_attachment=True
    )
from collections import defaultdict
from fpdf import FPDF
from flask import send_file, abort, current_app
import io, os

@ruangan_bp.route('/download_data_pdf/<ruangan_id>')
@login_or_token_required
def download_data_pdf(ruangan_id):
    ruangan = get_ruangan_by_id(ruangan_id)
    if not ruangan:
        abort(404)

    barang_list = get_barang_per_ruangan(ruangan_id)

    # --- Grouping barang ---
    grouped = defaultdict(list)
    for b in barang_list:
        kode_base = b.get("kode_barang", "").rsplit(".", 1)[0]
        key = (
            kode_base,
            b.get("nama_barang", ""),
            b.get("merk", ""),
            b.get("tahun", ""),
            b.get("harga_beli", 0),
            b.get("keterangan", "")
        )
        grouped[key].append(b)

    grouped_list = []
    for (kode_base, nama, merk, tahun, harga, keterangan), items in grouped.items():
        kondisi_counts = {"B": 0, "KB": 0, "RB": 0}
        kondisi_map = {
            "BAIK": "B", "B": "B",
            "KURANG BAIK": "KB", "KB": "KB",
            "RUSAK BERAT": "RB", "RB": "RB",
        }
        for i in items:
            kondisi_raw = str(i.get("kondisi", "")).upper().strip()
            kondisi = kondisi_map.get(kondisi_raw)
            if kondisi:
                kondisi_counts[kondisi] += 1

        grouped_list.append({
            "kode_barang": kode_base,
            "nama_barang": nama,
            "merk": merk,
            "tahun": tahun,
            "harga_beli": harga,
            "no_seri": ", ".join(sorted(set(i.get("no_seri", "") for i in items if i.get("no_seri")))),
            "ukuran": ", ".join(sorted(set(i.get("ukuran", "") for i in items if i.get("ukuran")))),
            "bahan": ", ".join(sorted(set(i.get("bahan", "") for i in items if i.get("bahan")))),
            "jumlah": len(items),
            "kondisi_B": kondisi_counts["B"],
            "kondisi_KB": kondisi_counts["KB"],
            "kondisi_RB": kondisi_counts["RB"],
            "keterangan": "; ".join(sorted(set(i.get("keterangan", "") for i in items if i.get("keterangan"))))
        })

    # --- Buat PDF ---
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()

    # === Header dengan Logo & Judul ===
    logo_path = os.path.join(current_app.root_path, "static", "brebes.jpg")
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=10, w=25)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "PEMERINTAHAN KABUPATEN BREBES", ln=True, align="C")
    pdf.cell(0, 8, "KARTU INVENTARIS RUANGAN", ln=True, align="C")
    pdf.ln(5)

    # Identitas Organisasi
    pdf.set_font("Arial", '', 10)
    pdf.cell(60, 6, "Provinsi", 0, 0)
    pdf.cell(0, 6, ": Jawa Tengah", ln=True)

    pdf.cell(60, 6, "Kabupaten/Kota", 0, 0)
    pdf.cell(0, 6, ": Brebes", ln=True)

    pdf.cell(60, 6, "Unit Organisasi", 0, 0)
    pdf.cell(0, 6, ": Dinas Komunikasi dan Informatika", ln=True)

    pdf.cell(60, 6, "Sub Unit Organisasi", 0, 0)
    pdf.cell(0, 6, ": Dinas Komunikasi dan Informatika", ln=True)

    pdf.cell(60, 6, "OB", 0, 0)
    pdf.cell(0, 6, ": Dinkominfo", ln=True)

    pdf.cell(60, 6, "Ruangan", 0, 0)
    pdf.cell(0, 6, f": {ruangan['nama_ruangan']}", ln=True)

    pdf.cell(60, 6, "Kode Lokasi", 0, 0)
    pdf.cell(0, 6, f": {ruangan['kode_lokasi']}", ln=True)

    pdf.ln(5)

    # === Header Tabel ===
    pdf.set_font("Arial", 'B', 8)

    col_widths = [8, 35, 50, 15, 15, 15, 15, 15, 15, 30, 25, 30]
    headers1 = ["No", "Kode Barang", "Nama Barang", "Merk", "No Seri", "Ukuran",
                "Bahan", "Tahun", "Jumlah", "Kondisi", "Harga Beli", "Keterangan"]

    for i, header in enumerate(headers1):
        if header == "Kondisi":
            pdf.cell(col_widths[i], 10, header, border=1, align="C")
        else:
            pdf.cell(col_widths[i], 20, header, border=1, align="C")
    pdf.ln()

    y = pdf.get_y() - 10
    pdf.set_xy(sum(col_widths[:9]) + pdf.l_margin, y)
    sub_width = col_widths[9] / 3
    for sub in ["B", "KB", "RB"]:
        pdf.cell(sub_width, 10, sub, border=1, align="C")
    pdf.ln(10)

    # === Isi Tabel ===
    pdf.set_font("Arial", '', 8)
    total_jumlah = 0
    total_harga = 0

    for idx, g in enumerate(grouped_list, start=1):
        total_jumlah += g["jumlah"]
        total_harga += g["harga_beli"] * g["jumlah"]

        row = [
            str(idx),
            g["kode_barang"],
            g["nama_barang"],
            g["merk"],
            g["no_seri"],
            g["ukuran"],
            g["bahan"],
            str(g["tahun"]),
            str(g["jumlah"]),
            "",
            f"Rp {g['harga_beli']:,.0f}",
            g["keterangan"] or ""
        ]

        # posisi awal
        x_start = pdf.get_x()
        y_start = pdf.get_y()

        # hitung tinggi baris keterangan
        pdf.set_font("Arial", '', 7)
        keterangan_text = str(row[-1]) if row[-1] else ""   # pastikan string
        if keterangan_text.strip():  
            # ada isi keterangan → hitung panjang teks
            text_width = pdf.get_string_width(keterangan_text)
            max_width = col_widths[-1]
            line_count = max(1, int(text_width / max_width) + 1)
        else:
            # keterangan kosong → cukup 1 baris
            line_count = 1

        row_height = line_count * 6


        # cetak cell selain kondisi & keterangan
        for i, val in enumerate(row[:-1]):
            if i == 9:  # kondisi
                sub_width = col_widths[9] / 3
                pdf.cell(sub_width, row_height, str(g["kondisi_B"]), border=1, align="C")
                pdf.cell(sub_width, row_height, str(g["kondisi_KB"]), border=1, align="C")
                pdf.cell(sub_width, row_height, str(g["kondisi_RB"]), border=1, align="C")
            else:
                pdf.cell(col_widths[i], row_height, val, border=1)

        # cetak keterangan pakai multi_cell
        x = pdf.get_x()
        y = pdf.get_y()
        pdf.multi_cell(col_widths[-1], 5, row[-1], border=1)
        pdf.set_xy(x_start, y_start + row_height)

    # === Baris Total ===
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(sum(col_widths[:8]), 8, "TOTAL", border=1, align="C")
    pdf.cell(col_widths[8], 8, str(total_jumlah), border=1, align="C")
    pdf.cell(col_widths[9], 8, "", border=1)  
    pdf.cell(col_widths[10], 8, f"Rp {total_harga:,.0f}", border=1, align="R")
    pdf.cell(col_widths[11], 8, "", border=1)
    pdf.ln()

    # === Simpan Buffer ===
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        download_name=f"{ruangan['nama_ruangan'].replace(' ', '_')}_DataBarang.pdf",
        as_attachment=True
    )
