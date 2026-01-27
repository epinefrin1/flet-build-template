import flet as ft
import sqlite3
from datetime import datetime
import os

def main(page: ft.Page):
    # --- AYARLAR ---
    page.title = "KNORGY FC vs EFSANE FUTBOL"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = "adaptive"
    page.padding = 20
    
    # --- VERİTABANI BAĞLANTISI ---
    try:
        klasor_yolu = os.path.dirname(os.path.abspath(__file__))
        db_yolu = os.path.join(klasor_yolu, "turnuva_mobil.db")
        
        conn = sqlite3.connect(db_yolu, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maclar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarih TEXT,
                skor1 INTEGER,
                skor2 INTEGER
            )
        """)
        conn.commit()
    except Exception as e:
        page.add(ft.Text(f"Veritabanı Hatası: {e}", color="red"))
        return

    # --- ARAYÜZ ELEMANLARI ---
    lbl_baslik = ft.Text("PUAN DURUMU", size=30, weight="bold", text_align="center")
    
    txt_takim1 = ft.Text("KNORGY FC", size=20, weight="bold", color="#833a2e")
    txt_takim2 = ft.Text("EFSANE FUTBOL", size=20, weight="bold", color="#3d70ff")

    txt_skor = ft.Text("0 - 0", size=50, weight="bold")
    
    txt_av1 = ft.Text("Av: 0", color="grey")
    txt_av2 = ft.Text("Av: 0", color="grey")
    
    txt_gol1 = ft.Text("Gol: 0", color="#a85c50", weight="bold")
    txt_gol2 = ft.Text("Gol: 0", color="#6e91ff", weight="bold")

    txt_toplam = ft.Text("Oynanan Maç: 0", size=12)
    liste_gecmis = ft.Column(spacing=10)

    # --- FONKSİYONLAR ---

    def verileri_getir():
        cursor.execute("SELECT * FROM maclar ORDER BY id DESC")
        maclar = cursor.fetchall()
        
        puan_a, puan_b = 0, 0
        gol_a, gol_b = 0, 0
        
        liste_gecmis.controls.clear()

        for mac in maclar:
            mac_id, tarih, s1, s2 = mac
            gol_a += s1
            gol_b += s2
            
            if s1 > s2: puan_a += 3
            elif s2 > s1: puan_b += 3
            else:
                puan_a += 1
                puan_b += 1
            
            renk = "white"
            yazi = f"{tarih} | {s1} - {s2}"
            if s1 > s2: 
                yazi += " (KNORGY)"
                renk = "#833a2e"
            elif s2 > s1: 
                yazi += " (EFSANE)"
                renk = "#3d70ff"

            # --- KESİN ÇÖZÜM (Container Yöntemi) ---
            # Hazır butonlar yerine, içine 'X' yazısı koyduğumuz tıklanabilir bir kutu yapıyoruz.
            # Bu yöntem Flet'in her sürümünde çalışır, hata vermez.
            sil_butonu = ft.Container(
                content=ft.Text("X", color="red", weight="bold"),
                data=mac_id, # ID'yi buraya gizledik
                on_click=sil_tusuna_basildi, # Tıklanınca çalışacak
                padding=10, # Dokunmatik için alanı genişlettik
            )

            satir = ft.Container(
                content=ft.Row(
                    [
                        ft.Text(yazi, color=renk, size=16, weight="bold", expand=True),
                        sil_butonu
                    ],
                    alignment="spaceBetween"
                ),
                padding=10,
                bgcolor="#1AFFFFFF", 
                border_radius=10
            )
            liste_gecmis.controls.append(satir)

        txt_skor.value = f"{puan_a} - {puan_b}"
        txt_av1.value = f"Av: {gol_a - gol_b:+d}"
        txt_av2.value = f"Av: {gol_b - gol_a:+d}"
        txt_gol1.value = f"Gol: {gol_a}"
        txt_gol2.value = f"Gol: {gol_b}"
        txt_toplam.value = f"Toplam Oynanan Maç: {len(maclar)}"
        page.update()

    def sil_tusuna_basildi(e):
        # Tıklanan kutunun ID'sini al
        silinecek_id = e.control.data
        if silinecek_id is not None:
            cursor.execute("DELETE FROM maclar WHERE id = ?", (silinecek_id,))
            conn.commit()
            verileri_getir()

    def mac_ekle(e):
        try:
            if not input_skor1.value or not input_skor2.value: return
            s1 = int(input_skor1.value)
            s2 = int(input_skor2.value)
            tarih = datetime.now().strftime("%d.%m %H:%M")
            
            cursor.execute("INSERT INTO maclar (tarih, skor1, skor2) VALUES (?, ?, ?)", (tarih, s1, s2))
            conn.commit()
            
            input_skor1.value = ""
            input_skor2.value = ""
            verileri_getir()
        except ValueError:
            pass

    # --- GİRİŞ KUTULARI ---
    input_skor1 = ft.TextField(hint_text="K", width=60, text_align="center", keyboard_type="number")
    input_skor2 = ft.TextField(hint_text="E", width=60, text_align="center", keyboard_type="number")
    btn_ekle = ft.ElevatedButton("EKLE", on_click=mac_ekle, bgcolor="green", color="white")

    # --- SAYFA DÜZENİ ---
    takim_bilgileri = ft.Row(
        [
            ft.Column([txt_takim1, txt_av1, txt_gol1], alignment="center", horizontal_alignment="center"),
            txt_skor,
            ft.Column([txt_takim2, txt_av2, txt_gol2], alignment="center", horizontal_alignment="center"),
        ],
        alignment="spaceEvenly",
        vertical_alignment="center"
    )

    giris_alani = ft.Row(
        [input_skor1, ft.Text("-", size=20), input_skor2, btn_ekle],
        alignment="center"
    )

    page.add(
        lbl_baslik,
        ft.Divider(),
        takim_bilgileri,
        ft.Divider(),
        txt_toplam,
        ft.Divider(),
        giris_alani,
        ft.Divider(),
        ft.Text("Maç Geçmişi", size=18),
        liste_gecmis
    )

    verileri_getir()

# Başlat
# Bilgisayarın yerel ağında yayına başla
# Düzeltilmiş Satır:
ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550, host="0.0.0.0")
