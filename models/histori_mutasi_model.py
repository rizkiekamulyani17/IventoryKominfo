from config import db
from bson.objectid import ObjectId
from datetime import datetime
from models.barang_model import get_barang_by_id

histori_mutasi_collection = db['histori_mutasi']

# Catat mutasi (barang dipindah / keluar kantor / dihapus)
def catat_mutasi(barang_id, ruangan_asal_id, ruangan_tujuan_id, keterangan=None):
    barang = get_barang_by_id(barang_id)

    snapshot = {}
    if barang:
        snapshot = {
            "nama_barang": barang.get("nama_barang", "-"),
            "merk": barang.get("merk", "-"),
            "no_seri": barang.get("no_seri", "-"),
            "ukuran": barang.get("ukuran", "-"),
            "bahan": barang.get("bahan", "-"),
            "tahun": barang.get("tahun", "-"),
            "jumlah": barang.get("jumlah", 0),
            "kondisi": barang.get("kondisi", "-"),
            "kode_barang": barang.get("kode_barang", "-"),  # ✅ ini ikut disimpan
            "harga_beli": barang.get("harga_beli", "-"),
            "keterangan": barang.get("keterangan", "-"),
        }

    histori = {
        "barang_id": ObjectId(barang_id),
        "ruangan_asal_id": ObjectId(ruangan_asal_id) if ruangan_asal_id else None,
        "ruangan_tujuan_id": ObjectId(ruangan_tujuan_id) if ruangan_tujuan_id != "luar_kantor" else None,
        "keterangan_luar": keterangan if ruangan_tujuan_id == "luar_kantor" else None,
        "tanggal_mutasi": datetime.now(),
        "snapshot_barang": snapshot  # ✅ simpan snapshot fix
    }

    histori_mutasi_collection.insert_one(histori)
    return histori


# Ambil semua histori mutasi
def get_all_histori():
    return list(histori_mutasi_collection.find().sort("tanggal_mutasi", -1))

# Hapus histori mutasi
def hapus_histori(id):
    return histori_mutasi_collection.delete_one({"_id": ObjectId(id)})


