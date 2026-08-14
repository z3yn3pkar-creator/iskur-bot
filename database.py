import sqlite3


DB_NAME = "ilanlar.db"


def veritabani_olustur():
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS ilanlar (
            ilan_no TEXT PRIMARY KEY,
            baslik TEXT NOT NULL,
            tarih TEXT,
            calisma_yeri TEXT
        )
    """)

    conn.commit()
    conn.close()


def ilan_var_mi(ilan_no):
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.execute(
        "SELECT 1 FROM ilanlar WHERE ilan_no = ?",
        (ilan_no,)
    )

    sonuc = cursor.fetchone()

    conn.close()

    return sonuc is not None


def ilan_ekle(ilan_no, baslik, tarih, calisma_yeri):
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        INSERT OR IGNORE INTO ilanlar
        (ilan_no, baslik, tarih, calisma_yeri)
        VALUES (?, ?, ?, ?)
    """, (
        ilan_no,
        baslik,
        tarih,
        calisma_yeri
    ))

    conn.commit()
    conn.close()