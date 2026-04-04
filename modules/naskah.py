import streamlit as st
import google.generativeai as genai
import os
import re

def run():
    # --- 1. KARANTINA MEMORI SISTEM ---
    os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

    # --- 2. PROMPT DIREKTUR KREATIF (VERSI PREMIUM & UNIVERSAL) ---
    DIREKTUR_PROMPT = """
[PERAN]
Kamu adalah Direktur Kreatif, Scriptwriter, dan Ahli Copywriting Profesional. Kamu sangat ahli menyusun naskah berjiwa, memikat, dan natural dengan gaya bahasa komunitas UMKM yang hangat dan persuasif.

[ATURAN KONDISIONAL FORMAT NASKAH - WAJIB MUTLAK DIIKUTI!]
1. KHUSUS JIKA TARGET ADALAH "Pesan Singkat", "WhatsApp", ATAU "Caption":
   - Output WAJIB 100% TEKS BERSIH SIAP COPAS. Leburkan kalimat pembuka dan naskah utama menjadi satu kesatuan pesan yang mengalir natural.
   - HARAM HUKUMNYA (DILARANG KERAS) menggunakan label kurung siku seperti [Hook] atau [Naskah Utama] di dalam teks.
   - HARAM HUKUMNYA (DILARANG KERAS) memunculkan elemen [Poin Infografis] maupun [Objek Visual Aman]. JANGAN DITULIS SAMA SEKALI. Kotak kode HANYA boleh berisi teks naskah promosi/edukasi yang siap kirim.
   - Naskah siap copas ini WAJIB diakhiri dengan Call to Action (CTA) atau ajakan bertindak yang diracik menarik berdasarkan panduan [Cara Mendapatkan/Membeli] dan [Info Kontak/Link] yang diinputkan pengguna.

2. JIKA TARGET ADALAH "Video", "Audio", "Voice Over", atau "Teks Infografis/Carousel":
   - WAJIB gunakan pemecahan modular dengan label: [Hook / Judul Pemikat], [Naskah Utama], [Poin Infografis], dan [Objek Visual Aman].
   - Jika diminta "1 Slide", berikan [Poin Infografis] yang padat (maks 5 kata per poin), abaikan naskah lisan panjang.
   - Naskah utama WAJIB diakhiri dengan Call to Action (CTA) atau ajakan bertindak yang diracik menarik berdasarkan panduan [Cara Mendapatkan/Membeli] dan [Info Kontak/Link] yang diinputkan pengguna.
   - KHUSUS JIKA TARGET ADALAH "Teks Infografis / Carousel", WAJIB cantumkan stempel 1 baris ini di bagian paling bawah naskah/poin: "dibuat dengan Studio Kreatif Pro (https://s.id/bikinpromo)"

3. ATURAN UMUM:
   - Gunakan bahasa membumi khas UMKM, gunakan sapaan/panggilan yang sesuai permintaan, dan hindari jargon teknis tingkat tinggi.

[ALUR KERJA]
1. 💡 Alasan Kreatif & Strategi
2. 🎛️ Arahan Rekaman / Publikasi
3. 🎙️ Naskah Final (Di dalam Kotak Kode):
Kamu WAJIB membungkus naskah final di dalam kotak kode (markdown code block) dengan awalan ```text dan akhiran ```. (Terapkan Aturan Kondisional di atas dengan SANGAT KETAT untuk isi di dalam kotak ini).
    """

    # --- 3. SETUP KREDENSIAL GEMINI ---
    try:
        gemini_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=gemini_key)
    except Exception as e:
        st.error(f"Kredensial Gemini bermasalah: {e}")
        st.stop()

    st.title("📝 Ruang 1: Studio Kreasi Naskah")
    
    st.info("💡 **Informasi:** Studio ini adalah titik awal produksi Anda. Di sini, Kecerdasan Buatan (AI) bertindak sebagai Direktur Kreatif yang akan membantu Anda menyusun naskah profesional.")

    # --- 4. INISIALISASI STATE (WIZARD) ---
    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 1
        st.session_state.jawaban = {
            "produk": "", "poin_penting": "", "cara_beli": "", "info_cta": "",
            "audiens": "", "sapaan": "", 
            "platform_tujuan": "", "durasi": "", "vibe": "", "tambahan": ""
        }
        st.session_state.hasil_naskah = ""

    # ==========================================
    # LANGKAH 1 TO 3 (WIZARD INPUTS BARU)
    # ==========================================
    
    # --- LANGKAH 1 (BARU): PRODUK, KEUNGGULAN, CARA BELI ---
    if st.session_state.wizard_step == 1:
        st.subheader("Langkah 1 dari 3: Informasi Produk & Penawaran")
        
        # 1. Produk
        st.markdown("**1. Apa produk atau jasa yang ditawarkan?**")
        pilihan_prod = st.selectbox("Pilih kategori atau isi sendiri:", 
                               ["Pilih...", "Aplikasi Kesehatan - Konsultan Puasa IF", "Aplikasi Pintar Saham", "Produk Kesehatan & Perawatan Pribadi", "Produk Makanan, Minuman & Suplemen", "Layanan / Jasa Komunitas", "Barang Elektronik / Gadget", "Acara / Webinar", "Isi Sendiri ..."], key="sb_prod", label_visibility="collapsed")
        jawaban_prod = pilihan_prod
        if pilihan_prod == "Isi Sendiri ...":
            jawaban_prod = st.text_input("Sebutkan produk atau jasa Anda secara spesifik:", key="ti_prod")

        # 2. Keunggulan
        st.markdown("**2. Apa pesan utama atau keunggulan yang WAJIB disampaikan?**")
        pilihan_poin = st.selectbox("Pilih atau isi sendiri:", 
                               ["Pilih...", "Aplikasi Kesehatan: IF Aman, Nutrisi Cerdas, Olahraga Terukur, Laporan Instan.", "Aplikasi Pintar Saham: Modul Analisa Premium, Screening Otomatis, Data Real-Time.", "Manfaat kesehatan & bahan alami yang digunakan", "Promo diskon terbatas & harga spesial", "Solusi praktis untuk masalah sehari-hari", "Ajakan bergabung ke komunitas / acara", "Isi Sendiri ..."], key="sb_poin", label_visibility="collapsed")
        jawaban_poin = pilihan_poin
        if pilihan_poin == "Isi Sendiri ...":
            jawaban_poin = st.text_area("Tuliskan poin penting/keunggulan produk Anda:", key="ta_poin")

        # 3. Cara Mendapatkan/Membeli
        st.markdown("**3. Bagaimana cara pembeli mendapatkan produk/jasa ini?**")
        col_beli1, col_beli2 = st.columns(2)
        with col_beli1:
            pilihan_beli = st.selectbox("Metode Pembelian/Akses:", 
                                   ["Pilih...", "Hubungi WhatsApp", "Beli via Marketplace (Shopee/Tokopedia/Tiktok)", "Kunjungi Website", "Datang Langsung ke Toko/Klinik", "Daftar via Link", "Isi Sendiri ..."], key="sb_beli")
            jawaban_beli = pilihan_beli
            if pilihan_beli == "Isi Sendiri ...":
                jawaban_beli = st.text_input("Sebutkan metode spesifik:", key="ti_beli")
        
        with col_beli2:
            jawaban_cta = st.text_input("Info CTA (No. WA / Nama Toko / Link Web):", placeholder="Contoh: 08123456789 atau namatoko.com", key="ti_cta")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Selanjutnya ➡️", key="btn_next_1"):
            if jawaban_prod and jawaban_prod != "Pilih..." and jawaban_poin and jawaban_poin != "Pilih..." and jawaban_beli and jawaban_beli != "Pilih..." and jawaban_cta:
                st.session_state.jawaban["produk"] = jawaban_prod
                st.session_state.jawaban["poin_penting"] = jawaban_poin
                st.session_state.jawaban["cara_beli"] = jawaban_beli
                st.session_state.jawaban["info_cta"] = jawaban_cta
                st.session_state.wizard_step = 2
                st.rerun()
            else:
                st.warning("Mohon lengkapi semua isian (Produk, Keunggulan, Metode Pembelian, dan Info Kontak) terlebih dahulu.")

    # --- LANGKAH 2 (BARU): SASARAN KONSUMEN & SAPAAN ---
    elif st.session_state.wizard_step == 2:
        st.subheader("Langkah 2 dari 3: Sasaran Konsumen & Sapaan")
        
        col_aud, col_sap = st.columns(2)
        with col_aud:
            pilihan_audiens = st.selectbox("Siapa target audiens atau pembaca naskah ini?", 
                                           ["Pilih...", "Pensiunan / Senior (Jelas, santai, hormat)", "Profesional / Pekerja (Formal, padat, lugas)", "Anak Muda / Gen Z (Cepat, kasual, gaul)", "Ibu Rumah Tangga (Hangat, akrab, praktis)", "Isi Sendiri ..."], key="sb_aud")
            jawaban_audiens = pilihan_audiens
            if pilihan_audiens == "Isi Sendiri ...":
                jawaban_audiens = st.text_input("Masukkan target audiens Anda secara spesifik:", key="ti_aud")
                
        with col_sap:
            pilihan_sapaan = st.selectbox("Panggilan/Sapaan apa yang biasa dipakai?", 
                                          ["Pilih...", "Teman-teman", "Bapak/Ibu", "Saudara-saudari", "Sobat UMKM", "Kakak/Adik", "Isi Sendiri ..."], key="sb_sap")
            jawaban_sapaan = pilihan_sapaan
            if pilihan_sapaan == "Isi Sendiri ...":
                jawaban_sapaan = st.text_input("Masukkan sapaan spesifik Anda:", key="ti_sap")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali", key="btn_back_2"):
                st.session_state.wizard_step = 1
                st.rerun()
        with col2:
            if st.button("Selanjutnya ➡️", key="btn_next_2"):
                if jawaban_audiens and jawaban_audiens != "Pilih..." and jawaban_sapaan and jawaban_sapaan != "Pilih...":
                    st.session_state.jawaban["audiens"] = jawaban_audiens
                    st.session_state.jawaban["sapaan"] = jawaban_sapaan
                    st.session_state.wizard_step = 3
                    st.rerun()
                else:
                    st.warning("Mohon pilih/isi sasaran konsumen beserta sapaannya terlebih dahulu.")

    # --- LANGKAH 3 (BARU): PLATFORM, DURASI, VIBE & KOREKSI ---
    elif st.session_state.wizard_step == 3:
        st.subheader("Langkah 3 dari 3: Platform, Durasi & Koreksi Akhir")
        
        # Platform Dinamis
        pilihan_platform = st.selectbox("Di mana naskah ini akan dipublikasikan?", 
                                        ["Pilih...", 
                                         "Pesan Singkat (WhatsApp / Telegram / Threads)", 
                                         "Caption Media Sosial (Instagram / Facebook / TikTok)", 
                                         "Teks Infografis / Carousel (Feed IG / Presentasi)", 
                                         "Video Pendek (TikTok / Reels / Shorts)", 
                                         "Voice Over Video YouTube / Audio Komunitas", 
                                         "Isi Sendiri ..."], key="sb_plat")
        jawaban_platform = pilihan_platform
        if pilihan_platform == "Isi Sendiri ...":
            jawaban_platform = st.text_input("Sebutkan platform tujuan spesifik Anda:", key="ti_plat")

        # Durasi Dinamis menyesuaikan Platform
        opsi_durasi = ["Pilih..."]
        if "WhatsApp" in jawaban_platform or "Pesan" in jawaban_platform or "Caption" in jawaban_platform:
            opsi_durasi.extend(["1 Paragraf Singkat (Sangat Padat)", "2-3 Paragraf (Standar Promo)", "Maksimal 300 Kata (Detail Lengkap)", "Isi Sendiri ..."])
        elif "Infografis" in jawaban_platform or "Carousel" in jawaban_platform:
            opsi_durasi.extend(["1 Slide Penuh (Poster Tunggal)", "3 Slide (Carousel Singkat)", "5 Slide (Carousel Standar)", "Isi Sendiri ..."])
        elif "Video" in jawaban_platform or "Voice Over" in jawaban_platform or "Audio" in jawaban_platform:
            opsi_durasi.extend(["15 detik (Iklan Cepat)", "30 detik (Standar Reels/TikTok)", "60 detik (Edukasi)", "Isi Sendiri ..."])
        else:
            opsi_durasi.extend(["Sangat Pendek / Singkat", "Sedang", "Panjang / Detail", "Isi Sendiri ..."])

        col_dur, col_vib = st.columns(2)
        with col_dur:
            pilihan_durasi = st.selectbox("Target Panjang/Durasi?", opsi_durasi, key="sb_dur")
            jawaban_durasi = pilihan_durasi
            if pilihan_durasi == "Isi Sendiri ...":
                jawaban_durasi = st.text_input("Masukkan target ukuran/durasi spesifik:", key="ti_dur")

            if jawaban_durasi and jawaban_durasi != "Pilih...":
                angka_ditemukan = re.findall(r'\d+', jawaban_durasi)
                if angka_ditemukan:
                    nilai_angka = int(angka_ditemukan[0])
                    teks_kecil = jawaban_durasi.lower()
                    if "jam" in teks_kecil: total_detik = nilai_angka * 3600
                    elif "menit" in teks_kecil: total_detik = nilai_angka * 60
                    elif "detik" in teks_kecil: total_detik = nilai_angka
                    else: total_detik = 0 
                    
                    if total_detik > 180:
                        st.warning("⏳ Maksimal target durasi untuk Audio/Video adalah **180 detik**. Isian dikunci ke batas maksimal.")
                        jawaban_durasi = "180 detik (Batas maksimal)"

        with col_vib:
            pilihan_vibe = st.selectbox("Suasana (Vibe)?", ["Pilih...", "Semangat (Promosi)", "Tenang (Edukasi)", "Santai (Kasual)", "Isi Sendiri ..."], key="sb_vibe")
            jawaban_vibe = pilihan_vibe
            if pilihan_vibe == "Isi Sendiri ...":
                jawaban_vibe = st.text_input("Masukkan emosi/suasana:", key="ti_vibe")

        st.divider()
        st.info("📋 **Koreksi Akhir Naskah Anda:**\nPastikan data di bawah ini sudah tepat sebelum dieksekusi oleh AI.")

        # Menampilkan data ringkas untuk diedit
        edit_produk = st.text_input("1. Produk/Jasa", value=st.session_state.jawaban.get("produk", ""), key="ed_prod")
        edit_poin = st.text_area("2. Keunggulan", value=st.session_state.jawaban.get("poin_penting", ""), key="ed_poin")
        
        col_ed_beli1, col_ed_beli2 = st.columns(2)
        with col_ed_beli1:
            edit_beli = st.text_input("3a. Cara Beli/Akses", value=st.session_state.jawaban.get("cara_beli", ""), key="ed_beli")
        with col_ed_beli2:
            edit_cta = st.text_input("3b. Info Kontak/Link", value=st.session_state.jawaban.get("info_cta", ""), key="ed_cta")
            
        col_ed1, col_ed2 = st.columns(2)
        with col_ed1:
            edit_audiens = st.text_input("4a. Sasaran Konsumen", value=st.session_state.jawaban.get("audiens", ""), key="ed_aud")
        with col_ed2:
            edit_sapaan = st.text_input("4b. Sapaan/Panggilan", value=st.session_state.jawaban.get("sapaan", ""), key="ed_sap")
            
        edit_tambahan = st.text_area("Catatan Tambahan (Opsional)", placeholder="Misal: Wajib sebutkan promo bebas ongkir.", key="ed_tambahan")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali", key="btn_back_3"):
                st.session_state.wizard_step = 2
                st.rerun()
        with col2:
            if st.button("✨ Lanjutkan ke Tahap Produksi", type="primary", key="btn_next_3"):
                if jawaban_platform and jawaban_platform != "Pilih..." and jawaban_durasi and jawaban_durasi != "Pilih..." and jawaban_vibe and jawaban_vibe != "Pilih...":
                    st.session_state.jawaban["produk"] = edit_produk
                    st.session_state.jawaban["poin_penting"] = edit_poin
                    st.session_state.jawaban["cara_beli"] = edit_beli
                    st.session_state.jawaban["info_cta"] = edit_cta
                    st.session_state.jawaban["audiens"] = edit_audiens
                    st.session_state.jawaban["sapaan"] = edit_sapaan
                    st.session_state.jawaban["platform_tujuan"] = jawaban_platform
                    st.session_state.jawaban["durasi"] = jawaban_durasi
                    st.session_state.jawaban["vibe"] = jawaban_vibe
                    st.session_state.jawaban["tambahan"] = edit_tambahan
                    st.session_state.wizard_step = 4
                    st.rerun()
                else:
                    st.warning("Mohon lengkapi Platform, Target Durasi, dan Suasana (Vibe) terlebih dahulu.")

    # ==========================================
    # LANGKAH 4 (BARU): PROSES AI & HASIL
    # ==========================================
    elif st.session_state.wizard_step == 4:
        platform_tujuan = st.session_state.jawaban.get("platform_tujuan", "")
        if "Audio" in platform_tujuan or "Video" in platform_tujuan or "Voice Over" in platform_tujuan:
            header_text = "🎬 Hasil Naskah Pro (Format Audio / Skrip Video)"
            spinner_text = "Direktur sedang menyusun naskah dengan teknik intonasi/SSML..."
            instruksi_tambahan = "Gunakan label skrip modular. WAJIB gunakan tag SSML untuk rekaman."
        elif "Pesan" in platform_tujuan or "WhatsApp" in platform_tujuan or "Caption" in platform_tujuan:
            header_text = "📱 Hasil Naskah Pro (Siap Copas)"
            spinner_text = "Direktur sedang menyusun pesan siap copas..."
            instruksi_tambahan = "WAJIB bentuk teks SIAP COPAS bersih 100%. DILARANG KERAS menyertakan [Poin Infografis] maupun [Objek Visual Aman]. JANGAN DITULIS SAMA SEKALI. DILARANG menggunakan tag SSML."
        else:
            header_text = "📝 Hasil Naskah Pro (Format Teks / Visual)"
            spinner_text = "Direktur sedang menyusun naskah Copywriting visual..."
            instruksi_tambahan = "Gunakan label skrip modular. DILARANG KERAS menggunakan tag SSML. KHUSUS UNTUK INFOGRAFIS WAJIB CANTUMKAN STEMPEL 'dibuat dengan Studio Kreatif Pro (https://s.id/bikinpromo)' di akhir."

        st.subheader(header_text)

        if not st.session_state.hasil_naskah:
            st.info("💡 **Pengaturan naskah Anda sudah diamankan!** Silakan tekan tombol di bawah ini untuk menginstruksikan AI menyusun naskah Anda.")
            
            if st.button("✨ Eksekusi Naskah Sekarang", type="primary", use_container_width=True, key="btn_eksekusi_final"):
                with st.spinner(spinner_text):
                    try:
                        model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=DIREKTUR_PROMPT)
                        
                        prompt_final = f"""
                        Tolong buatkan naskah berdasarkan panduan berikut:
                        - Produk/Jasa: {st.session_state.jawaban.get('produk', '')}
                        - Keunggulan Utama: {st.session_state.jawaban.get('poin_penting', '')}
                        - Cara Mendapatkan/Membeli: {st.session_state.jawaban.get('cara_beli', '')}
                        - Info Kontak / Link CTA: {st.session_state.jawaban.get('info_cta', '')}
                        - Sasaran Konsumen: {st.session_state.jawaban.get('audiens', '')}
                        - Sapaan/Panggilan: {st.session_state.jawaban.get('sapaan', '')}
                        - Platform & Tujuan: {st.session_state.jawaban.get('platform_tujuan', '')}
                        - Target Durasi/Panjang: {st.session_state.jawaban.get('durasi', '')}
                        - Suasana/Vibe: {st.session_state.jawaban.get('vibe', '')}
                        - Catatan Tambahan: {st.session_state.jawaban.get('tambahan', '')}
                        
                        ATURAN KHUSUS SAAT INI (BACA DENGAN TELITI): {instruksi_tambahan}. Pastikan untuk menggunakan kata sapaan/panggilan dan Call To Action yang diracik menarik dari Info Kontak di atas.
                        """
                        
                        response = model.generate_content(prompt_final)
                        st.session_state.hasil_naskah = response.text
                        st.rerun()
                        
                    except Exception as e:
                        err_msg = str(e).lower()
                        if "429" in err_msg or "quota" in err_msg:
                            st.error("⏳ **Mesin AI Sedang Beristirahat (Batas Kuota Beruntun).**")
                            st.info("💡 **Solusi Aman:** Karena request beruntun terlalu cepat, Google menghentikan sementara aksesnya. **TIDAK PERLU KEMBALI KE AWAL ATAU MENEKAN TOMBOL LAIN**. Cukup lepaskan *mouse* Anda, **tunggu 1 menit penuh**, lalu klik kembali tombol **'✨ Eksekusi Naskah Sekarang'** di atas. Data Anda aman dan tidak akan hilang.")
                        else:
                            st.error(f"❌ Terjadi kesalahan saat menghubungi AI: {e}")
        else:
            # Menggunakan sistem Tab agar tampilan tetap rapi, tombol copy tetap ada, namun naskah tetap bisa diedit.
            tab1, tab2 = st.tabs(["📄 Hasil Naskah (Klik Icon Copy)", "✏️ Edit Naskah Manual"])
            
            with tab1:
                st.markdown(st.session_state.hasil_naskah)
                
            with tab2:
                st.info("💡 Anda bisa mengubah kata-kata secara manual di kotak ini. **Penting:** Mohon JANGAN MENGHAPUS tanda ```text di awal dan ``` di bagian paling akhir naskah agar fitur tombol *copy* (tumpukan dokumen) di tab sebelah tetap berfungsi.")
                edited_text = st.text_area("Edit langsung naskah di sini:", value=st.session_state.hasil_naskah, height=400, key="ta_hasil_final")
                st.session_state.hasil_naskah = edited_text

            st.divider()
            st.info("🛠️ **Opsi Perubahan Naskah:**\nAnda bisa membuat ulang untuk produk/jasa lain, atau mengubah platform/format untuk produk ini (misal: dari WA ke Infografis) tanpa mengetik ulang info dari awal.")
            
            col_reset1, col_reset2 = st.columns(2)
            with col_reset1:
                # Tombol Ganti Format memicu rerun ke Langkah 3 (Kini Platform ada di Langkah 3)
                if st.button("🔁 Ganti Format (Platform/Tujuan) untuk Produk Ini", use_container_width=True, key="btn_ganti_format"):
                    st.session_state.hasil_naskah = ""
                    st.session_state.wizard_step = 3
                    st.rerun()
            with col_reset2:
                if st.button("🔄 Buat Naskah Baru (Produk/Jasa Lain)", use_container_width=True, key="btn_buat_baru"):
                    st.session_state.hasil_naskah = ""
                    st.session_state.wizard_step = 1
                    for key in st.session_state.jawaban:
                        st.session_state.jawaban[key] = ""
                    st.rerun()

            st.divider()
            st.info("🚀 **Lanjut Tahap Produksi:**\nSistem kami akan otomatis menarik data dari naskah di atas. Silakan pilih studio selanjutnya:")
            
            col_nav1, col_nav2 = st.columns(2)
            with col_nav1:
                if st.button("🎨 Ke Studio Kreasi Cetak / Visual", use_container_width=True, key="btn_nav_visual"):
                    st.session_state.menu_aktif = "3. Studio Kreasi Cetak / Visual"
                    st.rerun()
            with col_nav2:
                if st.button("🎙️ Ke Studio Kreasi Suara / Audio", use_container_width=True, key="btn_nav_audio"):
                    st.session_state.menu_aktif = "2. Studio Kreasi Suara / Audio"
                    st.rerun()
