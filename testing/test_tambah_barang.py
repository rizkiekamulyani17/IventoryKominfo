import pytest
from bson import ObjectId
from unittest.mock import MagicMock
import sys
import os

# Tambahkan path root proyek agar bisa import "models"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import fungsi yang akan diuji
from models.barang_model import tambah_barang, barang_collection


@pytest.fixture
def mock_barang_collection(monkeypatch):
    """Mock MongoDB collection agar tidak menulis ke database asli."""
    mock_collection = MagicMock()
    monkeypatch.setattr("models.barang_model.barang_collection", mock_collection)
    return mock_collection


def test_tambah_barang_berhasil(mock_barang_collection):
    """
    ✅ Pengujian unit untuk memastikan fungsi tambah_barang()
    berhasil menambahkan data ke koleksi barang di MongoDB.
    """

    # --- Data input dummy ---
    dummy_data = {
        "nama_barang": "Laptop Lenovo ThinkPad",
        "merk": "Lenovo",
        "no_seri": "SN123456",
        "ukuran": "14 inci",
        "bahan": "Plastik",
        "tahun": "2024",
        "jumlah": 2,
        "kondisi": "Baik",
        "harga_beli": 10000000,
        "ruangan_id": str(ObjectId()),  # gunakan ObjectId palsu
        "kode_barang_manual": "LP.001",
        "keterangan": "Laptop baru untuk kantor",
        "foto": ["static/uploads/barang/laptop1.png"]
    }

    # --- Jalankan fungsi yang diuji ---
    hasil = tambah_barang(dummy_data)

    # --- Validasi hasil ---
    # 1️⃣ Pastikan fungsi insert_one() dipanggil sejumlah barang (jumlah=2)
    assert mock_barang_collection.insert_one.call_count == 2

    # 2️⃣ Pastikan hasil mengandung jumlah item yang sama dengan jumlah input
    assert len(hasil) == 2

    # 3️⃣ Pastikan kode barang di-generate dengan benar
    assert hasil[0]["kode_barang"].startswith("LP.001.")
    assert hasil[1]["kode_barang"].startswith("LP.001.")

    # 4️⃣ Pastikan setiap barang punya field wajib
    for barang in hasil:
        assert "nama_barang" in barang
        assert "ruangan_id" in barang
        assert "kondisi" in barang
        assert "kode_barang" in barang
        assert "harga_beli" in barang
