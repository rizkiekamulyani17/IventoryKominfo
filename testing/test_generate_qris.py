import os
import sys
import uuid
import pytest
from unittest.mock import patch, MagicMock

# Pastikan pytest bisa menemukan folder models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.ruangan_model import generate_qris


@pytest.fixture
def mock_request():
    """Mock objek request Flask untuk menyediakan host_url"""
    mock = MagicMock()
    mock.host_url = "http://localhost:5000/"
    return mock


@patch("models.ruangan_model.request")
@patch("models.ruangan_model.qrcode.make")
def test_generate_qris_creates_unique_file(mock_qrcode_make, mock_request, tmp_path):
    """
    ✅ Uji bahwa fungsi generate_qris():
    1. Membuat file QR Code di path static/qris/
    2. Nama file unik (UUID)
    3. Mengembalikan path yang valid
    """

    # Buat folder sementara (tidak menulis ke static asli)
    static_path = tmp_path / "static" / "qris"
    os.makedirs(static_path, exist_ok=True)

    # Patch os.makedirs agar tidak bikin folder sungguhan
    with patch("models.ruangan_model.os.makedirs") as mock_makedirs, \
         patch("models.ruangan_model.uuid.uuid4", return_value=uuid.uuid4()):
        
        mock_request.host_url = "http://localhost:5000/"
        mock_img = MagicMock()
        mock_qrcode_make.return_value = mock_img

        kode_ruangan = "R001"
        result_path = generate_qris(kode_ruangan)

        # ✅ Pastikan URL QR benar
        expected_url = f"http://localhost:5000/scan/{kode_ruangan}"
        mock_qrcode_make.assert_called_once_with(expected_url)

        # ✅ Folder dibuat
        mock_makedirs.assert_called_once()

        # ✅ File path valid
        assert result_path.startswith("static/qris/")
        assert result_path.endswith(".png")

        # ✅ Simpan gambar QR dipanggil
        mock_img.save.assert_called_once_with(result_path)


@patch("models.ruangan_model.request")
@patch("models.ruangan_model.qrcode.make")
def test_generate_qris_creates_directory(mock_qrcode_make, mock_request, tmp_path):
    """✅ Uji bahwa fungsi membuat folder static/qris jika belum ada"""

    mock_request.host_url = "http://localhost:5000/"
    mock_img = MagicMock()
    mock_qrcode_make.return_value = mock_img

    # Patch os.makedirs agar aman
    with patch("models.ruangan_model.os.makedirs") as mock_makedirs:
        from models import ruangan_model
        result_path = ruangan_model.generate_qris("R002")

        # ✅ Folder dibuat minimal sekali
        mock_makedirs.assert_called_once()

        # ✅ Path hasil valid
        assert "static/qris" in result_path
        assert result_path.endswith(".png")
