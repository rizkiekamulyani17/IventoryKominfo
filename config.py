from pymongo import MongoClient


# MONGO_URI = "mongodb+srv://rizkiekamulyani123:pUHl3sgYGuSsim34@cluster0.qycctfx.mongodb.net/"
# DB_NAME = "Inventory_Kominfo" 
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
# config.py
PUBLIC_TOKENS = [
    "abc123",   # Token umum buat CRUD Barang & Ruangan
    "xyz789"    # Bisa tambahkan token lain kalau perlu
]
