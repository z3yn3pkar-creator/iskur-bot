import os
import requests
import time

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from database import veritabani_olustur, ilan_var_mi, ilan_ekle


# .env dosyasını yükle
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": mesaj
    }

    response = requests.post(url, data=data, timeout=20)

    if response.ok:
        print("Telegram mesajı gönderildi.")
    else:
        print("Telegram hatası:", response.text)


def iskur_kontrol_et():
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(
                "https://esube.iskur.gov.tr/istihdam/AcikisilanAra.aspx"
            )

            page.wait_for_load_state("domcontentloaded")

            print("İŞKUR açıldı.")

            # Düzce
            page.locator("#ctl04_ctlIl").select_option(
                label="DÜZCE"
            )

            print("Düzce seçildi.")

            # Kamu
            page.locator("#ctl04_kamuRadio").check()

            print("Kamu seçildi.")

            # Ara
            page.locator(
                "#ctl04_ctlAcikIsPageCommand_CommandItem_Search"
            ).click()

            print("Ara butonuna basıldı.")

            try:
                page.wait_for_load_state(
                    "networkidle",
                    timeout=15000
                )
            except:
                pass

            print("Sonuçlar okunuyor...")

            tablo = page.locator(
                "#ctl04_ctlGridAcikIslerListeDetail"
            )

            tablo_metni = tablo.inner_text()

            # Hiç ilan yoksa
            if (
                "Aradığınız kriterlere uygun kayıt bulunamadı."
                in tablo_metni
            ):
                print("Düzce + Kamu için ilan bulunamadı.")
                return

            ilan_basliklari = tablo.locator(
                "a[id*='_flag_']"
            )

            print(
                f"Bulunan ilan sayısı: "
                f"{ilan_basliklari.count()}"
            )

            for i in range(ilan_basliklari.count()):

                baslik_elementi = ilan_basliklari.nth(i)

                baslik = (
                    baslik_elementi
                    .inner_text()
                    .strip()
                )

                satir = baslik_elementi.locator(
                    "xpath=ancestor::tr[1]"
                )

                # İlan numarası
                ilan_no_elementi = satir.locator(
                    "a[href*='PopupJobDetails']"
                ).last

                ilan_no = (
                    ilan_no_elementi
                    .inner_text()
                    .strip()
                )

                # Son başvuru tarihi
                tarih_elementi = satir.locator(
                    "span[title='Son Başvuru Tarihi']"
                )

                tarih = (
                    tarih_elementi
                    .inner_text()
                    .strip()
                )

                # Çalışma yeri
                yer_elementi = satir.locator(
                    "span[title='Çalışma Yeri']"
                )

                if yer_elementi.count() > 0:

                    calisma_yeri = (
                        yer_elementi
                        .inner_text()
                        .strip()
                    )

                else:

                    calisma_yeri = ""

                    spanlar = satir.locator("span")

                    for j in range(spanlar.count()):

                        span_text = (
                            spanlar
                            .nth(j)
                            .inner_text()
                            .strip()
                        )

                        if "Çalışma Yeri:" in span_text:

                            calisma_yeri = span_text
                            break

                # Daha önce gördük mü?
                if ilan_var_mi(ilan_no):

                    print(
                        f"[ESKİ] "
                        f"{ilan_no} - {baslik}"
                    )

                else:

                    print(
                        f"[YENİ] "
                        f"{ilan_no} - {baslik}"
                    )

                    # Önce veritabanına kaydet
                    ilan_ekle(
                        ilan_no,
                        baslik,
                        tarih,
                        calisma_yeri
                    )

                    mesaj = (
                        "🚨 YENİ DÜZCE KAMU İLANI\n\n"
                        f"Meslek: {baslik}\n"
                        f"İlan No: {ilan_no}\n"
                        f"Son Başvuru: {tarih}\n"
                        f"Çalışma Yeri: {calisma_yeri}\n\n"
                        "İŞKUR:\n"
                        "https://esube.iskur.gov.tr/"
                        "istihdam/AcikisilanAra.aspx"
                    )

                    telegram_gonder(mesaj)

        finally:
            browser.close()


# Veritabanını hazırla
veritabani_olustur()

while True:
    print("\n" + "=" * 60)
    print("İŞKUR KONTROLÜ BAŞLIYOR")
    print("=" * 60)

    try:
        iskur_kontrol_et()
        print("\nKontrol başarıyla tamamlandı.")

    except Exception as e:
        print("\n⚠️ Kontrol sırasında hata oluştu:")
        print(e)

        # Telegram üzerinden hata bildirimi
        try:
            telegram_gonder(
                "⚠️ İŞKUR botunda hata oluştu.\n\n"
                f"Hata: {e}"
            )
        except Exception:
            pass

    print("\n10 dakika bekleniyor...")

    time.sleep(600)