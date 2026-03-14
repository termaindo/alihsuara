import streamlit as st
import re

def run():
    # Import HANYA dilakukan saat modul ini dipanggil agar memori tetap efisien
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
    # Memeriksa apakah ada hasil naskah dari Ruang 1 di dalam memori aplikasi
    if "hasil_naskah" in st.session_state and st.session_state.hasil_naskah:
        # Rumus untuk mengambil teks di dalam kotak kode (tanpa memutus tampilan sistem)
        simbol_kutip = "```"
        pola_pencarian = rf"{simbol_kutip}(?:text|markdown)?\n(.*?).*?{simbol_kutip}"
        
        match = re.search(pola_pencarian, st.session_state.hasil_naskah, re.DOTALL | re.IGNORECASE)
        if match:
            teks_bawaan = match.group(1).strip()
            st.success("✅ Naskah final dari Ruang Naskah berhasil ditarik otomatis!")
        else:
            # Jika Gemini tidak memberikan kotak kode, ambil semua teksnya saja
            teks_bawaan = st.session_state.hasil_naskah
            st.info("💡 Naskah ditarik tanpa format kotak kode. Silakan periksa kembali.")

    if not teks_bawaan:
        st.write("Silakan tempelkan (*paste*) naskah Anda di bawah ini.")

    # --- 3. ANTARMUKA STUDIO REKAMAN ---
    user_input = st.text_area("Kotak Naskah Studio:", value=teks_bawaan, height=250)

    # Panel Kontrol Suara
    col1, col2, col3 = st.columns(3)
    with col1:
        gender = st.selectbox(
            "Pilih Karakter Suara:", 
            ["Wanita (Wavenet-A)", "Pria (Wavenet-B)", "Pria (Wavenet-C)", "Wanita (Wavenet-D)"]
        )
    with col2:
        speed = st.slider("Kecepatan (Pacing):", 0.5, 1.5, 1.0, 0.1, help="Di atas 1.0 bicara cepat, di bawah 1.0 bicara lambat.")
    with col3:
        # Fitur Nada (Pitch) untuk emosi
        pitch = st.slider("Nada (Pitch):", -10.0, 10.0, 0.0, 0.5, help="Positif untuk ceria/tinggi, Negatif untuk berat/berwibawa.")

    # --- 4. PROSES PRODUKSI AUDIO ---
    if st.button("🔥 Produksi Suara Sekarang", use_container_width=True):
        if user_input:
            try:
                with st.spinner("Mesin Google sedang meracik suara..."):
                    client = texttospeech.TextToSpeechClient(credentials=tts_credentials)
                    
                    # MEMBERSIHKAN NASKAH: 
                    # Menghapus instruksi sutradara dalam tanda [] atau () agar tidak dibaca robot
                    naskah_bersih = re.sub(r'\[.*?\]', '', user_input)
                    naskah_bersih = re.sub(r'\(.*?\)', '', naskah_bersih)
                    
                    synthesis_input = texttospeech.SynthesisInput(text=naskah_bersih.strip())
                    
                    # Pemetaan nama suara
                    voice_map = {
                        "Wanita (Wavenet-A)": "id-ID-Wavenet-A",
                        "Pria (Wavenet-B)": "id-ID-Wavenet-B",
                        "Pria (Wavenet-C)": "id-ID-Wavenet-C",
                        "Wanita (Wavenet-D)": "id-ID-Wavenet-D"
                    }
                    voice_name = voice_map.get(gender, "id-ID-Wavenet-A")
                    
                    voice = texttospeech.VoiceSelectionParams(language_code="id-ID", name=voice_name)
                    
                    audio_config = texttospeech.AudioConfig(
                        audio_encoding=texttospeech.AudioEncoding.MP3, 
                        speaking_rate=speed,
                        pitch=pitch
                    )

                    response_audio = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

                    st.success("✅ Produksi Selesai!")
                    st.audio(response_audio.audio_content, format="audio/mp3")
                    
            except Exception as e:
                st.error(f"Gagal memproduksi suara: {e}")
        else:
            st.warning("Kotak naskah masih kosong.")
