from config import db
import qrcode
from flask import request
import os

ruangan_collection = db['ruangan']



def generate_qris(kode_ruangan):
    url = f"{request.host_url}scan/{kode_ruangan}"
    img = qrcode.make(url)

    path = f"static/qris/{kode_ruangan}.png"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return path


def tambah_ruangan(nama_ruangan, kode_ruangan, kode_lokasi):
    
    qris_path = generate_qris(kode_ruangan)
    ruangan = {
        "nama_ruangan": nama_ruangan,
        "kode_ruangan": kode_ruangan,
        "kode_lokasi": kode_lokasi,
        "qris_path": qris_path
    }
    ruangan_collection.insert_one(ruangan)
    return ruangan

def get_semua_ruangan2():
    return list(ruangan_collection.find())


def get_ruangan_by_nama(nama_ruangan):
    return ruangan_collection.find_one({"nama_ruangan": nama_ruangan})

def get_semua_ruangan():
    pipeline = [
        {
            "$lookup": {    # join ke koleksi barang
                "from": "barang",
                "localField": "_id",
                "foreignField": "ruangan_id",
                "as": "barang_list"
            }
        },
        {
            "$addFields": {
                "total_barang": {"$size": "$barang_list"}  # hitung jumlah
            }
        },
        {
            "$project": {   # biar barang_list nggak ikut keluarin
                "barang_list": 0
            }
        }
    ]
    return list(ruangan_collection.aggregate(pipeline))
def get_ruangan_by_id(ruangan_id):
    from bson.objectid import ObjectId
    return ruangan_collection.find_one({"_id": ObjectId(ruangan_id)})

def hapus_ruangan(ruangan_id):
    from bson.objectid import ObjectId
    ruangan_collection.delete_one({"_id": ObjectId(ruangan_id)})
def get_ruangan_by_kode(kode_ruangan):
    """
    Mengambil data ruangan berdasarkan kode_ruangan
    """
    return ruangan_collection.find_one({"kode_ruangan": kode_ruangan})


def update_ruangan(ruangan_id, nama_baru, kode_ruangan_baru, kode_lokasi_baru):
    from bson.objectid import ObjectId
    ruangan_collection.update_one(
        {"_id": ObjectId(ruangan_id)},
        {"$set": {
            "nama_ruangan": nama_baru,
            "kode_ruangan": kode_ruangan_baru,
            "kode_lokasi": kode_lokasi_baru
        }}
    )


