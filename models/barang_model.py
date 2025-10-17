from config import db, barang_collection, histori_mutasi_collection
from models.ruangan_model import generate_qris, get_ruangan_by_id
import qrcode
from datetime import datetime
from bson import ObjectId
barang_collection = db['barang']

def generate_kode_barang(base_kode, urutan):
    # Misal base_kode = M.123, urutan=1 → M.123.01
    return f"{base_kode}.{str(urutan).zfill(2)}"

# def tambah_barang(data):
#     from bson.objectid import ObjectId 

#     jumlah_input = int(data['jumlah'])
#     base_kode = data.get('kode_barang_manual')
#     if not base_kode:
#         raise ValueError("Kode barang manual harus diisi")

#     ruangan_id = ObjectId(data['ruangan_id'])

#     inserted_items = []
#     harga_total = int(data.get('harga_beli', 0))
#     harga_satuan = harga_total // jumlah_input if jumlah_input > 0 else harga_total

#     for i in range(jumlah_input):
#         kode_barang = generate_kode_barang(base_kode, i + 1)

#         barang_doc = {
#             "no": i + 1,
#             "nama_barang": data['nama_barang'],
#             "merk": data.get('merk'),
#             "no_seri": data.get('no_seri'),
#             "ukuran": data.get('ukuran'),
#             "bahan": data.get('bahan'),
#             "tahun": data.get('tahun'),
#             "kode_barang": kode_barang,
#             "jumlah": 1,
#             "kondisi": data['kondisi'],
#             "harga_beli": harga_satuan,
#             "ruangan_id": ruangan_id,
#             "keterangan": data.get("keterangan", "").strip(),
#             "foto": data.get("foto")  # simpan path foto jika ada
#         }

#         barang_collection.insert_one(barang_doc)
#         inserted_items.append(barang_doc)

#     return inserted_items


def get_barang_per_ruangan(ruangan_id):
    from bson.objectid import ObjectId
    return list(barang_collection.find({"ruangan_id": ObjectId(ruangan_id)}))

def get_barang_by_id(barang_id):
    from bson.objectid import ObjectId
    return barang_collection.find_one({"_id": ObjectId(barang_id)})

def hapus_barang(barang_id):
    from bson.objectid import ObjectId
    barang_collection.delete_one({"_id": ObjectId(barang_id)})

# def get_all_barang():
#     return list(barang_collection.find().sort("tahun", 1))  
#     # 1 = ascending (tahun paling lama dulu), -1 = descending
def get_all_barang():
    result = list(barang_collection.find().sort("tahun", 1))
    barang_list = []

    for item in result:
        status_lelang = (item.get("status_lelang") or "").strip().lower()

        # 🧹 Jika barang status lelangnya selesai, pindahkan ke histori_mutasi
        if status_lelang == "selesai":
            histori_mutasi_collection.insert_one({
                "barang_id": item["_id"],
                "snapshot_barang": item,  # simpan semua data barang saat ini
                "tanggal_mutasi": datetime.now(),
                "keterangan": "Lelang selesai",
                "ruangan_asal_id": item.get("ruangan_id"),
                "status_mutasi": "LELANG"
            })

            # 🗑️ Hapus barang dari tabel barang
            barang_collection.delete_one({"_id": ObjectId(item["_id"])})
            continue

        # ✅ Barang yang bukan lelang selesai akan tetap ditampilkan
        ruangan = get_ruangan_by_id(item["ruangan_id"]) if item.get("ruangan_id") else None
        barang_list.append({
            "_id": str(item["_id"]),
            "no": item.get("no", 0),
            "nama_barang": item.get("nama_barang", ""),
            "merk": item.get("merk", ""),
            "no_seri": item.get("no_seri", ""),
            "ukuran": item.get("ukuran", ""),
            "bahan": item.get("bahan", ""),
            "tahun": item.get("tahun", ""),
            "kode_barang": item.get("kode_barang", ""),
            "jumlah": item.get("jumlah", 1),
            "kondisi": item.get("kondisi", ""),
            "harga_beli": item.get("harga_beli", 0),
            "keterangan": item.get("keterangan", "-"),
            "qris_path": item.get("qris_path", ""),
            "foto": item.get("foto", ""),
            "file_bast": item.get("file_bast", ""),
            "status_lelang": item.get("status_lelang", ""),
            "nama_ruangan": ruangan["nama_ruangan"] if ruangan else "Tidak diketahui",
            "ruangan_id": str(item["ruangan_id"]) if item.get("ruangan_id") else None
        })

    return barang_list


def update_kondisi_barang(barang_id, kondisi_baru):
    from bson.objectid import ObjectId
    barang_collection.update_one(
        {"_id": ObjectId(barang_id)},
        {"$set": {"kondisi": kondisi_baru}}
    )
def get_barang_by_kode(kode_barang):
    """
    Mengambil data barang berdasarkan kode_barang
    """
    return barang_collection.find_one({"kode_barang": kode_barang})
def update_barang(barang_id, data_baru):
    from bson.objectid import ObjectId

    update_fields = {
        "nama_barang": data_baru.get("nama_barang"),
        "kode_barang": data_baru.get("kode_barang"),
        "merk": data_baru.get("merk"),
        "no_seri": data_baru.get("no_seri"),
        "ukuran": data_baru.get("ukuran"),
        "bahan": data_baru.get("bahan"),
        "tahun": data_baru.get("tahun"),
        "jumlah": int(data_baru.get("jumlah", 1)),
        "kondisi": data_baru.get("kondisi"),
        "harga_beli": int(data_baru.get("harga_beli", 0)),
        "ruangan_id": ObjectId(data_baru["ruangan_id"]) if data_baru.get("ruangan_id") else None,
        "keterangan": data_baru.get("keterangan", "").strip()
    }

    # 🔹 Tambahkan update foto jika ada
    if data_baru.get("foto"):
        update_fields["foto"] = data_baru["foto"]

    # 🔹 Tambahkan update file BAST jika ada
    if "file_bast" in data_baru:
        update_fields["file_bast"] = data_baru.get("file_bast")

    barang_collection.update_one(
        {"_id": ObjectId(barang_id)},
        {"$set": update_fields}
    )



def get_barang_by_kode_manual(kode_manual, merk=None, tahun=None, harga=None, ruangan_id=None):
    from models.ruangan_model import get_ruangan_by_id
    from bson.objectid import ObjectId

    query = {"kode_barang": {"$regex": f"^{kode_manual}"}}

    if merk:
        query["merk"] = merk
    if tahun:
        query["tahun"] = tahun
    if harga is not None:
        query["harga_beli"] = harga
    if ruangan_id:  # ✅ pakai ruangan_id, bukan kode_ruangan
        query["ruangan_id"] = ObjectId(ruangan_id)

    items = list(barang_collection.find(query).sort("no", 1))

    for item in items:
        if item.get("ruangan_id"):
            ruangan_obj = get_ruangan_by_id(item["ruangan_id"])
            item["nama_ruangan"] = ruangan_obj["nama_ruangan"] if ruangan_obj else "Tidak diketahui"
        else:
            item["nama_ruangan"] = "Luar Kantor"

        item["_id"] = str(item["_id"])

    return items






def get_semua_barang():
    """
    Mengambil semua data barang dan menambahkan nama_ruangan, _id sebagai string.
    """
    result = list(barang_collection.find().sort("tahun", 1))
    barang_list = []
    for item in result:
        barang_list.append({
            "_id": str(item["_id"]),
            "no": item.get("no", 0),
            "nama_barang": item.get("nama_barang", ""),
            "merk": item.get("merk", ""),
            "no_seri": item.get("no_seri", ""),
            "ukuran": item.get("ukuran", ""),
            "bahan": item.get("bahan", ""),
            "tahun": item.get("tahun", ""),
            "kode_barang": item.get("kode_barang", ""),
            "jumlah": item.get("jumlah", 1),
            "kondisi": item.get("kondisi", ""),
            "harga_beli": item.get("harga_beli", 0),
            "keterangan": item.get("keterangan", ""),
            "qris_path": item.get("qris_path", ""),
            "nama_ruangan": get_ruangan_by_id(item["ruangan_id"])["nama_ruangan"] if item.get("ruangan_id") else "Tidak diketahui"
        })
    return barang_list


def get_all_barang2():
    from models.ruangan_model import get_ruangan_by_id
    
    pipeline = [
        {
            "$group": {
                "_id": {
                    "nama_barang": "$nama_barang",
                    "merk": "$merk",
                    "kondisi": "$kondisi",
                    "tahun": "$tahun",
                    "harga_beli": "$harga_beli",
                    "kode_manual": {
                        "$arrayElemAt": [
                            {"$split": ["$kode_barang", "."]},
                            0
                        ]
                    },
                    "ruangan_id": "$ruangan_id"
                },
                "jumlah": {"$sum": 1},
                "doc": {"$first": "$$ROOT"}
            }
        },
        {"$sort": {"tahun": 1}}
    ]

    result = list(barang_collection.aggregate(pipeline))

    barang_list = []
    for r in result:
        d = r["doc"]
        base_kode = ".".join(d["kode_barang"].split(".")[:-1])
        
        # ✅ ambil nama ruangan
        ruangan = get_ruangan_by_id(r["_id"]["ruangan_id"]) if r["_id"].get("ruangan_id") else None
        nama_ruangan = ruangan["nama_ruangan"] if ruangan else "Tidak diketahui"

        barang_list.append({
            "_id": str(d["_id"]),
            "nama_barang": r["_id"]["nama_barang"],
            "merk": r["_id"]["merk"],
            "tahun": r["_id"]["tahun"],
            "kondisi": r["_id"]["kondisi"],
            "kode_barang": base_kode,
            "jumlah": r["jumlah"],
            "nama_ruangan": nama_ruangan  # ✅ tambahkan ke dict
        })
        # Urutkan ascending berdasarkan tahun
    barang_list = sorted(barang_list, key=lambda x: x["tahun"])
    return barang_list




# def tambah_barang(data):
#     from bson.objectid import ObjectId 

#     jumlah_input = int(data['jumlah'])
#     base_kode = data.get('kode_barang_manual')
#     if not base_kode:
#         raise ValueError("Kode barang manual harus diisi")

#     ruangan_id = ObjectId(data['ruangan_id'])

#     inserted_items = []
#     harga_total = int(data.get('harga_beli', 0))
#     harga_satuan = harga_total // jumlah_input if jumlah_input > 0 else harga_total

#     for i in range(jumlah_input):
#         kode_barang = generate_kode_barang(base_kode, i + 1)

#     barang_doc = {
#         "no": i + 1,
#         "nama_barang": data['nama_barang'],
#         "merk": data.get('merk'),
#         "no_seri": data.get('no_seri'),
#         "ukuran": data.get('ukuran'),
#         "bahan": data.get('bahan'),
#         "tahun": data.get('tahun'),
#         "kode_barang": kode_barang,
#         "jumlah": 1,
#         "kondisi": data['kondisi'],
#         "harga_beli": harga_satuan,
#         "ruangan_id": ruangan_id,
#         "keterangan": data.get("keterangan", "").strip(),
#         "foto": data.get("foto", [])  # simpan list foto
#     }

#     barang_collection.insert_one(barang_doc)
#     inserted_items.append(barang_doc)

#     return inserted_items

def tambah_barang(data):
    from bson.objectid import ObjectId 

    jumlah_input = int(data['jumlah'])
    base_kode = data.get('kode_barang_manual')
    if not base_kode:
        raise ValueError("Kode barang manual harus diisi")

    ruangan_id = ObjectId(data['ruangan_id'])

    inserted_items = []
    harga_total = int(data.get('harga_beli', 0))
    harga_satuan = harga_total // jumlah_input if jumlah_input > 0 else harga_total

    for i in range(jumlah_input):
        kode_barang = generate_kode_barang(base_kode, i + 1)

        barang_doc = {
            "no": i + 1,
            "nama_barang": data['nama_barang'],
            "merk": data.get('merk'),
            "no_seri": data.get('no_seri'),
            "ukuran": data.get('ukuran'),
            "bahan": data.get('bahan'),
            "tahun": data.get('tahun'),
            "kode_barang": kode_barang,
            "jumlah": 1,
            "kondisi": data['kondisi'],
            "harga_beli": harga_satuan,
            "ruangan_id": ruangan_id,
            "keterangan": data.get("keterangan", "").strip(),
            "foto": data.get("foto", []),           # simpan list foto
            "file_bast": data.get("file_bast")      # simpan file BAST jika ada
        }

        barang_collection.insert_one(barang_doc)
        inserted_items.append(barang_doc)

    return inserted_items
