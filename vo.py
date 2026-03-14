import streamlit as st
import re

def run():
    # Import dilakukan di dalam fungsi agar isolasi modul tetap terjaga
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
    
    # --- 2. LOGIKA PENARIKAN DATA OTOMATIS ---
    # Inisialisasi variabel penampung
    instruksi_rekaman = ""
    naskah_untuk_kotak = ""
    
    # Cek apakah ada data dari Ruang 1 (naskah.py)
    if "hasil_naskah" in st.session_state and st.session_state.hasil_naskah:
        raw_text = st.session_state.hasil_naskah
        
        # A. Ekstraksi Arahan Rekaman (Mencari teks antara 🎛️ dan 🎙️)
        try:
            search_arahan = re.search(r"🎛️ Arahan Rekaman:(.*?)🎙️", raw_text, re.DOTALL | re.IGNORECASE)
            if search_arahan:
                instruksi_rekaman = search_arahan.group(1).strip()
        except:
            instruksi_rekaman = ""

        # B. Ekstraksi Naskah Final (Mencari teks di dalam blok kode ```)
        bt = "```" # Menghindari error tampilan chat dengan variabel
        pattern = rf"{bt}(?:text|markdown)?\n(.*?){bt}"
        match_naskah = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)
        
        if match_naskah:
            naskah_untuk_kotak = match_naskah.group(1).strip()
            st.success("✅ Berhasil menarik naskah otomatis dari Ruang 1!")
        else:
            # Jika tidak ada blok kode, ambil seluruh teks sebagai fallback
            naskah_untuk_kotak = raw_text
            st.info("💡 Naskah ditarik secara utuh (tanpa pemisahan otomatis).")
    else:
        st.info("💡 Belum ada naskah dari Ruang 1. Silakan buat naskah dulu atau ketik manual di bawah.")

    # --- 3. TAMPILAN ARAHAN & KOTAK KERJA ---
    # Tampilkan Arahan Rekaman jika ditemukan
    if instruksi_rekaman:
        with st.expander("📖 Lihat Arahan Rekaman (Tone & Kecepatan)", expanded=True):
            st.markdown(instruksi_rekaman)

    # Kotak Teks Utama
    user_input = st.text_area(
        "Edit Naskah Final di sini:", 
        value=naskah_untuk_kotak, 
        height=300,
        help="Naskah di dalam kotak ini yang akan diubah menjadi suara."
    )

    # Panel Kontrol Mesin
    col1, col2, col3 = st.columns(3)
    with col1:
        gender = st.selectbox(
            "Pilih Karakter Suara:", 
            ["Wanita (Wavenet-A)", "Pria (Wavenet-B)", "Pria (Wavenet-C)", "Wanita (Wavenet-D)"]
        )
    with col2:
        speed = st.slider("Laju Bicara (Speed):", 0.5, 1.5, 1.0, 0.1)
    with col3:
        pitch = st.slider("Nada Suara (Pitch):", -10.0, 10.0, 0.0, 0.5)

    # --- 4. PROSES PRODUKSI AUDIO ---
    if st.button("🔥 Produksi Suara Sekarang", use_container_width=True):
        if user_input:
            try:
                with st.spinner("Mesin Google Wavenet sedang memproduksi suara..."):
                    client = texttospeech.TextToSpeechClient(credentials=tts_credentials)
                    
                    # Pembersihan teks dari instruksi non-verbal agar tidak dibaca robot
                    # Menghapus apapun di dalam kurung ( ) dan [ ]
                    clean_text = re.sub(r'\[.*?\]', '', user_input)
                    clean_text = re.sub(r'\(.*?\)', '', clean_text)
                    
                    synthesis_input = texttospeech.SynthesisInput(text=clean_text.strip())
                    
                    # Mapping Suara
                    voice_map = {
                        "Wanita (Wavenet-A)": "id-ID-Wavenet-A",
                        "Pria (Wavenet-B)": "id-ID-Wavenet-B",
                        "Pria (Wavenet-C)": "id-ID-Wavenet-C",
                        "Wanita (Wavenet-D)": "id-ID-Wavenet-D"
                    }
                    
                    voice = texttospeech.VoiceSelectionParams(
                        language_code="id-ID", 
                        name=voice_map.get(gender, "id-ID-Wavenet-A")
                    )
                    
                    audio_config = texttospeech.AudioConfig(
                        audio_encoding=texttospeech.AudioEncoding.MP3,
                        speaking_rate=speed,
                        pitch=pitch
                    )

                    response = client.synthesize_speech(
                        input=synthesis_input, 
                        voice=voice, 
                        audio_config=audio_config
                    )

                    st.success("✅ Selesai! Klik tombol putar di bawah:")
                    st.audio(response.audio_content, format="audio/mp3")
            except Exception as e:
                st.error(f"Gagal memproduksi suara: {e}")
        else:
            st.warning("Silakan isi atau tarik naskah terlebih dahulu.")
