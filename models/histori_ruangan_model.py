from config import db
from datetime import datetime
from bson.objectid import ObjectId

histori_ruangan_collection = db["histori_ruangan"]

def simpan_histori_ruangan(ruangan):
    """
    Menyimpan data ruangan ke histori_ruangan sebelum dihapus.
    """
    histori_data = {
        "ruangan_id_asli": str(ruangan["_id"]),
        "nama_ruangan": ruangan.get("nama_ruangan"),
        "kode_ruangan": ruangan.get("kode_ruangan"),
        "kode_lokasi": ruangan.get("kode_lokasi"),
        "penanggung_jawab": ruangan.get("penanggung_jawab"),
        "nip_pj": ruangan.get("nip_pj"),
        "qris_path": ruangan.get("qris_path"),
        "deleted_at": datetime.utcnow()  # kapan dihapus
    }
    histori_ruangan_collection.insert_one(histori_data)
    return histori_data

def get_semua_histori():
    return list(histori_ruangan_collection.find().sort("deleted_at", -1))

def get_histori_by_id(histori_id):
    return histori_ruangan_collection.find_one({"_id": ObjectId(histori_id)})



def hapus_histori(histori_id):
    result = histori_ruangan_collection.delete_one({"_id": ObjectId(histori_id)})
    return result.deleted_count > 0