from config import db
from bson.objectid import ObjectId
from models.ruangan_model import get_ruangan_by_id

barang_collection = db['barang']

def get_summary_kondisi():
    """
    Menghitung jumlah barang per kondisi
    """
    pipeline = [
        {"$group": {"_id": "$kondisi", "jumlah": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    return list(barang_collection.aggregate(pipeline))

def get_barang_by_kondisi(kondisi):
    """
    Ambil daftar barang berdasarkan kondisi tertentu
    """
    result = list(barang_collection.find({"kondisi": kondisi}))
    barang_list = []
    for item in result:
        ruangan = get_ruangan_by_id(item["ruangan_id"]) if item.get("ruangan_id") else None
        barang_list.append({
            "_id": str(item["_id"]),
            "nama_barang": item.get("nama_barang", ""),
            "merk": item.get("merk", ""),
            "tahun": item.get("tahun", ""),
            "kode_barang": item.get("kode_barang", ""),
            "kondisi": item.get("kondisi", ""),
            "ruangan": ruangan["nama_ruangan"] if ruangan else "Tidak diketahui"
        })
    return barang_list
