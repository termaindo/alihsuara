import streamlit as st
import google.generativeai as genai
import os

def run():
    # --- 1. KARANTINA MEMORI SISTEM ---
    os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

    # --- 2. PROMPT DIREKTUR KREATIF (VERSI SSML ADVANCED) ---
    DIREKTUR_PROMPT = """
[PERAN]
Kamu adalah Direktur Kreatif Script Alih Suara. Kamu ahli dalam menyusun naskah yang menggunakan SSML (Speech Synthesis Markup Language) agar suara AI Google Wavenet terdengar natural, berjiwa, dan tidak kaku.

[ALUR KERJA]
Berdasarkan data wawancara, susunlah output sebagai berikut:

1. 💡 Alasan Kreatif:
Jelaskan dengan bahasa ramah kenapa naskah ini dibuat seperti ini.

2. 🎛️ Arahan Rekaman:
Berikan panduan tone dan suasana.

3. 🎙️ Naskah Final (Format SSML):
Kamu WAJIB membungkus naskah di dalam kotak kode (markdown code block).
Gunakan tag SSML untuk mengatur ritme. Contoh penggunaan yang harus kamu ikuti:
- Gunakan <break time="400ms"/> untuk jeda napas antar kalimat.
- Gunakan <prosody pitch="+2st" rate="1.1">teks</prosody> untuk kalimat yang antusias/promo.
- Gunakan <prosody pitch="-1st" rate="0.9">teks</prosody> untuk kalimat yang serius/berwibawa.
- Seluruh naskah harus diawali dengan <speak> dan diakhiri dengan </speak>.

PENTING: Pastikan teks di dalam SSML tetap bersih dan enak didengar.
    """

    # --- 3. SETUP KREDENSIAL GEMINI ---
    try:
        gemini_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=gemini_key)
    except Exception as e:
        st.error(f"Kredensial Gemini bermasalah: {e}")
        st.stop()

    st.title("📝 Ruang 1: Rapat Naskah Direktur Kreatif")

    # --- 4. INISIALISASI STATE (WIZARD) ---
    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 1
        st.session_state.jawaban = {
            "produk": "", 
            "poin_penting": "", 
            "durasi": "", 
            "audiens": "", 
            "vibe": "", 
            "konteks": "", 
            "tambahan": ""
        }
        st.session_state.hasil_naskah = ""

    # ==========================================
    # LANGKAH 1: PRODUK / JASA
    # ==========================================
    if st.session_state.wizard_step == 1:
        st.subheader("Langkah 1 dari 6: Produk atau Jasa")
        pilihan = st.selectbox("Apa produk atau jasa yang ingin Anda buatkan narasinya?", 
                               ["Pilih...", 
                                "Produk Kesehatan & Suplemen", 
                                "Makanan & Minuman", 
                                "Layanan / Jasa Komunitas", 
                                "Barang Elektronik / Gadget", 
                                "Acara / Webinar",
                                "Isi sendiri..."])
        
        jawaban_final = pilihan
        if pilihan == "Isi sendiri...":
            jawaban_final = st.text_input("Sebutkan produk atau jasa Anda:")

        if st.button("Selanjutnya ➡️"):
            if jawaban_final and jawaban_final != "Pilih...":
                st.session_state.jawaban["produk"] = jawaban_final
                st.session_state.wizard_step = 2
                st.rerun()
            else:
                st.warning("Mohon pilih atau isi produk/jasa terlebih dahulu.")

    # ==========================================
    # LANGKAH 2: POIN PENTING / KEUNGGULAN
    # ==========================================
    elif st.session_state.wizard_step == 2:
        st.subheader("Langkah 2 dari 6: Keunggulan Utama")
        pilihan = st.selectbox("Apa pesan utama atau keunggulan yang WAJIB disampaikan?", 
                               ["Pilih...", 
                                "Manfaat kesehatan & bahan alami yang digunakan", 
                                "Promo diskon terbatas & harga spesial", 
                                "Solusi praktis untuk masalah sehari-hari", 
                                "Ajakan bergabung ke komunitas / acara",
                                "Isi sendiri..."])
        
        jawaban_final = pilihan
        if pilihan == "Isi sendiri...":
            jawaban_final = st.text_area("Tuliskan poin penting/keunggulan produk Anda:")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali"):
                st.session_state.wizard_step = 1
                st.rerun()
        with col2:
            if st.button("Selanjutnya ➡️"):
                if jawaban_final and jawaban_final != "Pilih...":
                    st.session_state.jawaban["poin_penting"] = jawaban_final
                    st.session_state.wizard_step = 3
                    st.rerun()
                else:
                    st.warning("Mohon pilih atau isi poin penting terlebih dahulu.")

    # ==========================================
    # LANGKAH 3: DURASI
    # ==========================================
    elif st.session_state.wizard_step == 3:
        st.subheader("Langkah 3 dari 6: Target Durasi")
        pilihan = st.selectbox("Berapa detik target durasi naskah Anda?", 
                               ["Pilih...", "15 detik (Singkat / Iklan Cepat)", "30 detik (Standar Iklan/Reels)", "60 detik (Edukasi / Penjelasan Lengkap)", "Isi sendiri..."])
        
        jawaban_final = pilihan
        if pilihan == "Isi sendiri...":
            jawaban_final = st.text_input("Masukkan durasi yang Anda inginkan (misal: 45 detik):")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali"):
                st.session_state.wizard_step = 2
                st.rerun()
        with col2:
            if st.button("Selanjutnya ➡️"):
                if jawaban_final and jawaban_final != "Pilih...":
                    st.session_state.jawaban["durasi"] = jawaban_final
                    st.session_state.wizard_step = 4
                    st.rerun()
                else:
                    st.warning("Mohon pilih atau isi durasi terlebih dahulu.")

    # ==========================================
    # LANGKAH 4: AUDIENS & VIBE
    # ==========================================
    elif st.session_state.wizard_step == 4:
        st.subheader("Langkah 4 dari 6: Audiens & Suasana")
        pilihan_audiens = st.selectbox("Siapa pendengar utama naskah ini?", 
                               ["Pilih...", "Pensiunan / Senior (Jelas, santai, hormat)", "Profesional / Pekerja (Formal, padat, lugas)", "Anak Muda / Gen Z (Cepat, kasual, gaul)", "Ibu Rumah Tangga (Hangat, akrab, praktis)", "Isi sendiri..."])
        
        jawaban_audiens = pilihan_audiens
        if pilihan_audiens == "Isi sendiri...":
            jawaban_audiens = st.text_input("Masukkan target audiens Anda:")

        pilihan_vibe = st.selectbox("Perasaan apa yang ingin dibangun?", 
                               ["Pilih...", "Semangat & Menggebu-gebu (Promosi)", "Tenang & Meyakinkan (Kesehatan/Edukasi)", "Santai & Menghibur (Kasual)", "Isi sendiri..."])
        
        jawaban_vibe = pilihan_vibe
        if pilihan_vibe == "Isi sendiri...":
            jawaban_vibe = st.text_input("Masukkan vibe/emosi yang Anda inginkan:")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali"):
                st.session_state.wizard_step = 3
                st.rerun()
        with col2:
            if st.button("Selanjutnya ➡️"):
                if jawaban_audiens and jawaban_vibe and jawaban_audiens != "Pilih..." and jawaban_vibe != "Pilih...":
                    st.session_state.jawaban["audiens"] = jawaban_audiens
                    st.session_state.jawaban["vibe"] = jawaban_vibe
                    st.session_state.wizard_step = 5
                    st.rerun()
                else:
                    st.warning("Mohon lengkapi audiens dan suasana terlebih dahulu.")

    # ==========================================
    # LANGKAH 5: KONTEKS & RANGKUMAN FINAL
    # ==========================================
    elif st.session_state.wizard_step == 5:
        st.subheader("Langkah 5 dari 6: Konteks & Koreksi")
        
        pilihan_konteks = st.selectbox("Naskah ini akan digunakan untuk platform apa?", 
                               ["Pilih...", "Video Pendek (TikTok/Reels/Shorts)", "Audio Presentasi / Komunitas", "Voice Over Video YouTube", "Isi sendiri..."])
        
        jawaban_konteks = pilihan_konteks
        if pilihan_konteks == "Isi sendiri...":
            jawaban_konteks = st.text_input("Masukkan platform tujuan Anda:")

        st.divider()
        st.info("📋 **Periksa Kembali Panduan Naskah Anda:**\nSilakan edit langsung di dalam kotak jika ada yang ingin diubah sebelum diserahkan ke Direktur Kreatif.")

        # Menampilkan input editable seperti versi terbaik sebelumnya
        edit_produk = st.text_input("1. Produk/Jasa", value=st.session_state.jawaban.get("produk", ""))
        edit_poin = st.text_input("2. Poin Penting", value=st.session_state.jawaban.get("poin_penting", ""))
        edit_durasi = st.text_input("3. Target Durasi", value=st.session_state.jawaban.get("durasi", ""))
        edit_audiens = st.text_input("4. Target Audiens", value=st.session_state.jawaban.get("audiens", ""))
        edit_vibe = st.text_input("5. Suasana", value=st.session_state.jawaban.get("vibe", ""))
        edit_tambahan = st.text_area("Catatan Tambahan (Opsional)", placeholder="Misal: Wajib sebutkan kata 'Autofagi'.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali"):
                st.session_state.wizard_step = 4
                st.rerun()
        with col2:
            if st.button("✨ Hasilkan Naskah Berjiwa (SSML)", type="primary"):
                if jawaban_konteks and jawaban_konteks != "Pilih...":
                    st.session_state.jawaban["konteks"] = jawaban_konteks
                    st.session_state.jawaban["produk"] = edit_produk
                    st.session_state.jawaban["poin_penting"] = edit_poin
                    st.session_state.jawaban["durasi"] = edit_durasi
                    st.session_state.jawaban["audiens"] = edit_audiens
                    st.session_state.jawaban["vibe"] = edit_vibe
                    st.session_state.jawaban["tambahan"] = edit_tambahan
                    st.session_state.wizard_step = 6
                    st.rerun()
                else:
                    st.warning("Mohon pilih atau isi konteks platform terlebih dahulu.")

    # ==========================================
    # LANGKAH 6: PROSES AI & HASIL
    # ==========================================
    elif st.session_state.wizard_step == 6:
        st.subheader("🎬 Hasil Naskah Pro (Format SSML)")

        if not st.session_state.hasil_naskah:
            with st.spinner("Direktur sedang menyusun naskah dengan teknik SSML..."):
                try:
                    model_direktur = genai.GenerativeModel(
                        model_name="gemini-2.5-flash",
                        system_instruction=DIREKTUR_PROMPT
                    )
                    
                    # Menyusun prompt yang lebih rapi ke Gemini
                    prompt_final = f"""
                    Tolong buatkan naskah SSML berdasarkan panduan berikut:
                    - Produk/Jasa: {st.session_state.jawaban['produk']}
                    - Poin Penting/Keunggulan: {st.session_state.jawaban['poin_penting']}
                    - Durasi Target: {st.session_state.jawaban['durasi']}
                    - Target Audiens: {st.session_state.jawaban['audiens']}
                    - Vibe/Emosi: {st.session_state.jawaban['vibe']}
                    - Konteks Platform: {st.session_state.jawaban['konteks']}
                    - Catatan Tambahan: {st.session_state.jawaban['tambahan'] if st.session_state.jawaban['tambahan'] else "Tidak ada"}
                    """
                    
                    response = model_direktur.generate_content(prompt_final)
                    st.session_state.hasil_naskah = response.text
                    st.rerun()
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat menghubungi AI: {e}")
                    if st.button("Coba Lagi"):
                        st.rerun()
        else:
            # Menampilkan hasil
            st.markdown(st.session_state.hasil_naskah)

            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Buat Naskah Baru"):
                    st.session_state.hasil_naskah = ""
                    st.session_state.wizard_step = 1
                    st.rerun()
            with col2:
                if st.button("🚀 Pindah ke Studio Rekaman (VO)", use_container_width=True):
                    st.session_state.menu_aktif = "2. Studio Rekaman"
                    st.rerun()
