from pymongo import MongoClient

# --- Koneksi ke MongoDB ---
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "Inventaris_Kominfo"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    print("✅ Database names:", client.list_database_names())
except Exception as e:
    print("❌ Error:", e)


# --- Definisi Collection ---
barang_collection = db["barang"]
histori_mutasi_collection = db["histori_mutasi"]
ruangan_collection = db["ruangan"]   # (kalau kamu punya ruangan)
# Tambahkan collection lain di sini jika perlu

# --- Token Akses ---
PUBLIC_TOKENS = [
    "dinkominfotik",
    "kominfobbs"
]
