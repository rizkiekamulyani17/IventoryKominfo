from config import db
from bson.objectid import ObjectId
from datetime import datetime

histori_mutasi_collection = db['histori_mutasi']

def catat_mutasi(barang_id, ruangan_asal_id, ruangan_tujuan_id, keterangan=None):
    histori = {
        "barang_id": ObjectId(barang_id),
        "ruangan_asal_id": ObjectId(ruangan_asal_id) if ruangan_asal_id else None,
        "ruangan_tujuan_id": ObjectId(ruangan_tujuan_id) if ruangan_tujuan_id != "luar_kantor" else None,
        "keterangan_luar": keterangan if ruangan_tujuan_id == "luar_kantor" else None,
        "tanggal_mutasi": datetime.now()
    }
    histori_mutasi_collection.insert_one(histori)
    return histori

def get_all_histori():
    return list(histori_mutasi_collection.find().sort("tanggal_mutasi", -1))

def hapus_histori(id):
    return histori_mutasi_collection.delete_one({"_id": ObjectId(id)})
