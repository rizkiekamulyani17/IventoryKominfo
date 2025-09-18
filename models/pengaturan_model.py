from config import db
pengaturan_collection = db['pengaturan']

def get_pengaturan():
    return pengaturan_collection.find_one() or {}

def update_pengaturan(nama_pengguna, nip_pengguna,
                      nama_pengurus, nip_pengurus):
    pengaturan_collection.update_one(
        {},  # update dokumen pertama
        {"$set": {
            "nama_pengguna": nama_pengguna,
            "nip_pengguna": nip_pengguna,
            "nama_pengurus": nama_pengurus,
            "nip_pengurus": nip_pengurus
        }},
        upsert=True
    )
