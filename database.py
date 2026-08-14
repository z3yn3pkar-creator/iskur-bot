import json
import os

DB_NAME = "ilanlar.json"


def veritabani_olustur():
    if not os.path.exists(DB_NAME):
        with open(DB_NAME, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)


def ilan_var_mi(ilan_no):
    if not os.path.exists(DB_NAME):
        return False

    with open(DB_NAME, "r", encoding="utf-8") as f:
        ilanlar = json.load(f)

    return ilan_no in ilanlar


def ilan_ekle(ilan_no, baslik, tarih, calisma_yeri):
    if os.path.exists(DB_NAME):
        with open(DB_NAME, "r", encoding="utf-8") as f:
            ilanlar = json.load(f)
    else:
        ilanlar = {}

    ilanlar[ilan_no] = {
        "baslik": baslik,
        "tarih": tarih,
        "calisma_yeri": calisma_yeri
    }

    with open(DB_NAME, "w", encoding="utf-8") as f:
        json.dump(ilanlar, f, ensure_ascii=False, indent=2)
