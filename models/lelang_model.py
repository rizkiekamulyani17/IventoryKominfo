from bson import ObjectId
from datetime import datetime

# Semua fungsi menerima `db` dari app.py

def get_dashboard_data(db):
    """
    Statistik Dashboard Lelang:
    - Total Barang Rusak Berat (termasuk yang sudah dilelang)
    - Belum Dilelang
    - On Going
    - Sudah Dilelang (selesai)
    """
    # Barang rusak berat dari koleksi barang
    total_rusak_barang = db.barang.count_documents({"kondisi": "Rusak Berat"})
    total_rusak_lelang = db.barang_lelang.count_documents({"kondisi": "Rusak Berat"})
    total_barang = total_rusak_barang + total_rusak_lelang

    # Hitung per status lelang di koleksi barang utama
    belum_dilelang = db.barang.count_documents({
        "kondisi": "Rusak Berat",
        "status_lelang": "Belum"
    })

    on_going = db.barang.count_documents({
        "kondisi": "Rusak Berat",
        "status_lelang": "On Going"
    })

    # Barang yang sudah selesai lelang dari tabel barang_lelang
    sudah_dilelang = db.barang_lelang.count_documents({"status": "selesai"})

    jumlah_surat = db.surat.count_documents({})

    return {
        "total_barang": total_barang,
        "belum_dilelang": belum_dilelang,
        "on_going": on_going,
        "total_selesai": sudah_dilelang,
        "jumlah_surat": jumlah_surat
    }


def get_barang_rusak_berat(db):
    """
    Mengambil semua barang dengan kondisi 'Rusak Berat'
    """
    return list(db.barang.find({"kondisi": "Rusak Berat"}))


def update_barang(db, item_id, update_data):
    """
    Update data barang berdasarkan ID
    """
    db.barang.update_one({"_id": ObjectId(item_id)}, {"$set": update_data})


def delete_barang(db, item_id):
    """
    Hapus barang berdasarkan ID
    """
    db.barang.delete_one({"_id": ObjectId(item_id)})


def get_barang_by_id(db, item_id):
    """
    Ambil detail barang berdasarkan ID
    """
    return db.barang.find_one({"_id": ObjectId(item_id)})

def insert_riwayat_lelang(db, barang):
    """
    Memindahkan data barang yang sudah dilelang ke koleksi riwayat_lelang
    """
    db.riwayat_lelang.insert_one({
        "barang_id": str(barang["_id"]),
        "nama_barang": barang.get("nama_barang"),
        "merk": barang.get("merk"),
        "kategori": barang.get("kategori"),
        "kondisi": barang.get("kondisi"),
        "tahun": barang.get("tahun"),
        "jumlah": barang.get("jumlah"),
        "harga_beli": barang.get("harga_beli"),
        "gambar_barang": barang.get("gambar_barang"),
        "status_lelang": "Selesai",
        "tanggal_selesai": datetime.now()
    })


def insert_barang_lelang(db, barang):
    """
    Menambahkan data barang yang sudah dilelang ke koleksi barang_lelang
    """
    db.barang_lelang.insert_one({
        "barang_id": str(barang["_id"]),
        "nama_barang": barang.get("nama_barang"),
        "merk": barang.get("merk"),
        "kategori": barang.get("kategori"),
        "kondisi": barang.get("kondisi"),
        "tahun": barang.get("tahun"),
        "jumlah": barang.get("jumlah"),
        "harga_beli": barang.get("harga_beli"),
        "harga_tawar": barang.get("harga_tawar"),
        "limit_akhir": barang.get("limit_akhir"),
        "gambar_barang": barang.get("gambar_barang"),
        "status": "selesai",  # status di tabel barang_lelang
        "tanggal_selesai": datetime.now()
    })
