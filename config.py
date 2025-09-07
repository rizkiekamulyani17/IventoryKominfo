from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "Inventaris_Kominfo"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
# config.py
PUBLIC_TOKENS = [
    "abc123",   # Token umum buat CRUD Barang & Ruangan
    "xyz789"    # Bisa tambahkan token lain kalau perlu
]
