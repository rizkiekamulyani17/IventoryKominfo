from config import db
import qrcode
from flask import request
import os
import uuid  # <-- tambah uuid

ruangan_collection = db['ruangan']

def generate_qris(kode_ruangan):
    # URL QRIS tetap bisa pakai kode_ruangan
    url = f"{request.host_url}scan/{kode_ruangan}"
    img = qrcode.make(url)

    # Nama file QRIS pakai UUID supaya unik
    file_uuid = str(uuid.uuid4())
    path = f"static/qris/{file_uuid}.png"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    
    return path  # path lengkap ke file QRIS



# def tambah_ruangan(nama_ruangan, kode_ruangan, kode_lokasi):
    
#     qris_path = generate_qris(kode_ruangan)
#     ruangan = {
#         "nama_ruangan": nama_ruangan,
#         "kode_ruangan": kode_ruangan,
#         "kode_lokasi": kode_lokasi,
#         "qris_path": qris_path
#     }
#     ruangan_collection.insert_one(ruangan)
#     return ruangan

def tambah_ruangan(nama_ruangan, kode_ruangan, kode_lokasi,
                   penanggung_jawab=None, nip_pj=None):
    qris_path = generate_qris(kode_ruangan)
    ruangan = {
        "nama_ruangan": nama_ruangan,
        "kode_ruangan": kode_ruangan,
        "kode_lokasi": kode_lokasi,
        "qris_path": qris_path,
        "penanggung_jawab": penanggung_jawab,
        "nip_pj": nip_pj
    }
    ruangan_collection.insert_one(ruangan)
    return ruangan

def update_penanggung_jawab(ruangan_id, nama_pj, nip_pj):
    from bson.objectid import ObjectId
    ruangan_collection.update_one(
        {"_id": ObjectId(ruangan_id)},
        {"$set": {
            "penanggung_jawab": nama_pj,
            "nip_pj": nip_pj
        }}
    )


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

from config import db
import qrcode
from flask import request
import os
import uuid  # <-- tambah uuid

ruangan_collection = db['ruangan']

def generate_qris(kode_ruangan):
    # URL QRIS tetap bisa pakai kode_ruangan
    url = f"{request.host_url}scan/{kode_ruangan}"
    img = qrcode.make(url)

    # Nama file QRIS pakai UUID supaya unik
    file_uuid = str(uuid.uuid4())
    path = f"static/qris/{file_uuid}.png"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    
    return path  # path lengkap ke file QRIS



# def tambah_ruangan(nama_ruangan, kode_ruangan, kode_lokasi):
    
#     qris_path = generate_qris(kode_ruangan)
#     ruangan = {
#         "nama_ruangan": nama_ruangan,
#         "kode_ruangan": kode_ruangan,
#         "kode_lokasi": kode_lokasi,
#         "qris_path": qris_path
#     }
#     ruangan_collection.insert_one(ruangan)
#     return ruangan

def tambah_ruangan(nama_ruangan, kode_ruangan, kode_lokasi,
                   penanggung_jawab=None, nip_pj=None):
    qris_path = generate_qris(kode_ruangan)
    ruangan = {
        "nama_ruangan": nama_ruangan,
        "kode_ruangan": kode_ruangan,
        "kode_lokasi": kode_lokasi,
        "qris_path": qris_path,
        "penanggung_jawab": penanggung_jawab,
        "nip_pj": nip_pj
    }
    ruangan_collection.insert_one(ruangan)
    return ruangan

def update_penanggung_jawab(ruangan_id, nama_pj, nip_pj):
    from bson.objectid import ObjectId
    ruangan_collection.update_one(
        {"_id": ObjectId(ruangan_id)},
        {"$set": {
            "penanggung_jawab": nama_pj,
            "nip_pj": nip_pj
        }}
    )


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
    from models.histori_ruangan_model import simpan_histori_ruangan

    ruangan = ruangan_collection.find_one({"_id": ObjectId(ruangan_id)})
    if ruangan:
        # simpan dulu ke histori
        simpan_histori_ruangan(ruangan)
        # baru hapus dari koleksi utama
        ruangan_collection.delete_one({"_id": ObjectId(ruangan_id)})

def get_ruangan_by_kode(kode_ruangan):
    """
    Mengambil data ruangan berdasarkan kode_ruangan
    """
    return ruangan_collection.find_one({"kode_ruangan": kode_ruangan})



def update_ruangan(ruangan_id, nama_baru, kode_ruangan_baru, kode_lokasi_baru, 
                   penanggung_jawab_baru, nip_pj_baru, regenerate_qris=False):
    from bson.objectid import ObjectId

    update_data = {
        "nama_ruangan": nama_baru,
        "kode_ruangan": kode_ruangan_baru,
        "kode_lokasi": kode_lokasi_baru,
        "penanggung_jawab": penanggung_jawab_baru,
        "nip_pj": nip_pj_baru
    }

    if regenerate_qris:
        from models.ruangan_model import generate_qris
        qris_path = generate_qris(kode_ruangan_baru)
        update_data["qris_path"] = qris_path

    ruangan_collection.update_one(
        {"_id": ObjectId(ruangan_id)},
        {"$set": update_data}
    )

def get_ruangan_by_kode(kode_ruangan):
    """
    Mengambil data ruangan berdasarkan kode_ruangan
    """
    return ruangan_collection.find_one({"kode_ruangan": kode_ruangan})



def update_ruangan(ruangan_id, nama_baru, kode_ruangan_baru, kode_lokasi_baru, 
                   penanggung_jawab_baru, nip_pj_baru, regenerate_qris=False):
    from bson.objectid import ObjectId

    update_data = {
        "nama_ruangan": nama_baru,
        "kode_ruangan": kode_ruangan_baru,
        "kode_lokasi": kode_lokasi_baru,
        "penanggung_jawab": penanggung_jawab_baru,
        "nip_pj": nip_pj_baru
    }

    if regenerate_qris:
        from models.ruangan_model import generate_qris
        qris_path = generate_qris(kode_ruangan_baru)
        update_data["qris_path"] = qris_path

    ruangan_collection.update_one(
        {"_id": ObjectId(ruangan_id)},
        {"$set": update_data}
    )
