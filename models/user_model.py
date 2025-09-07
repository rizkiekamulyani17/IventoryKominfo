from config import db
from werkzeug.security import generate_password_hash, check_password_hash

user_collection = db['user']

def create_admin(username, password):
    if user_collection.find_one({"username": username}):
        return False
    user_collection.insert_one({
        "username": username,
        "password_hash": generate_password_hash(password),
        "role": "admin"
    })
    return True

def verify_login(username, password):
    user = user_collection.find_one({"username": username})
    if user and check_password_hash(user['password_hash'], password):
        return user   # ✅ kembalikan dict user
    return None        # ✅ kalau gagal, return None
# fungsi untuk ambil user by id
from bson.objectid import ObjectId

def get_user_by_id(user_id):
    return user_collection.find_one({"_id": ObjectId(user_id)})

# fungsi untuk ambil user by email
def get_user_by_email(email):
    return user_collection.find_one({"email": email})

# fungsi untuk update user
def update_user(user_id, data):
    return user_collection.update_one({"_id": ObjectId(user_id)}, {"$set": data})

# fungsi untuk hapus user
def delete_user(user_id):
    return user_collection.delete_one({"_id": ObjectId(user_id)})

# fungsi untuk ambil semua user
def get_all_users():
    return list(user_collection.find())