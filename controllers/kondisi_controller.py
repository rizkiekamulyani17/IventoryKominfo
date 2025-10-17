from flask import Blueprint, render_template
from models.kondisi_model import get_summary_kondisi, get_barang_by_kondisi
from utils.auth import login_or_token_required  

kondisi_bp = Blueprint("kondisi", __name__, url_prefix="/kondisi")

@kondisi_bp.route("/")

def index():
    summary = get_summary_kondisi()
    return render_template("kondisi/index.html", summary=summary)

@kondisi_bp.route("/detail/<kondisi>")

def detail(kondisi):
    barang = get_barang_by_kondisi(kondisi)
    return render_template("kondisi/detail.html", kondisi=kondisi, barang=barang)
