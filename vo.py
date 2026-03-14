import streamlit as st
import re

def run():
    # Import HANYA dilakukan saat modul ini dipanggil agar tidak membebani memori utama
    from google.cloud import texttospeech
    from google.oauth2 import service_account
    import json

    # --- 1. SETUP KREDENSIAL GOOGLE CLOUD TTS ---
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
    # Memeriksa apakah ada hasil naskah dari Ruang 1 di dalam memori (Session State)
    if "hasil_naskah" in st.session_state and st.session_state.hasil_naskah:
        # Menggunakan Regex untuk mengambil teks HANYA di dalam blok kode (```)
        match = re.search(r'
