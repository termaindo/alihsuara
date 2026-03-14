import streamlit as st
import re

def run():
    # Import HANYA dilakukan saat modul ini dipanggil
    from google.cloud import texttospeech
    from google.oauth2 import service_account
    import json

    # --- 1. SETUP KREDENSIAL TTS ---
    try:
        gcp_creds = st.secrets["GCP_CREDENTIALS"]
        if isinstance(gcp_creds, str):
            gcp_creds_dict = json.loads(gcp_creds)
        else:
            gcp_creds_dict = dict(gcp_creds)
            
        tts_credentials = service_account.Credentials.from_service_account_info(gcp_creds_dict)
    except Exception as e:
        st.error(f"Kredensial Google Cloud bermasalah: {e}")
        st.stop()

    st.title("🎧 Ruang 2: Studio Rekaman Pro")
    
    # --- 2. LOGIKA TRANSFER OTOMATIS DARI RUANG 1 ---
    teks_bawaan = ""
    if "hasil_naskah" in st.session_state and st.session_state.hasil_naskah:
        # Mencari teks yang dibungkus oleh tiga backtick (```) dari output Gemini
        match = re.search(r'
http://googleusercontent.com/immersive_entry_chip/0

**Perubahan Kunci yang Saya Lakukan:**
1.  **Deteksi Otomatis (Regex):** Sistem kini mengais teks di antara tanda ``` secara otomatis dari memori `st.session_state`.
2.  **Slider Nada (Pitch):** Bapak kini bisa memanipulasi frekuensi suara. Mau Wavenet-B terdengar lebih dalam layaknya penyiar radio berita? Geser Pitch ke arah minus (misal: -3.0). Mau Wavenet-A terdengar lebih antusias untuk promo diskon? Geser Pitch ke arah positif (misal: +2.0).
3.  **Pembersih Cerdas:** Saya menggunakan modul `re` (Regex) bawaan Python agar pembersihan tanda kurung `[]` dan `()` jauh lebih bersih, jadi teks instruksi seperti *(tersenyum)* di naskah otomatis diabaikan oleh mesin tanpa merusak tanda baca aslinya.

Silakan *commit* dan coba alur kerjanya langsung dari Ruang 1 menuju Ruang 2, Pak. Apakah naskahnya berhasil melompat otomatis ke kotak teks?
