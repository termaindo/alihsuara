import streamlit as st
import naskah
import vo

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Studio Alih Suara Pro", page_icon="🎙️", layout="wide")

# Inisialisasi state navigasi
if 'menu_aktif' not in st.session_state:
    st.session_state.menu_aktif = "Home"

# --- HEADER & NAVIGASI HALAMAN UTAMA ---
st.title("🎙️ Studio Alih Suara Pro")
st.markdown("Pilih ruangan kerja Anda di bawah ini:")

# Membuat 3 tombol sejajar sebagai menu utama
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🏠 Halaman Utama", use_container_width=True):
        st.session_state.menu_aktif = "Home"
        st.rerun()
with col2:
    if st.button("📝 Ruang Naskah", use_container_width=True):
        st.session_state.menu_aktif = "1. Ruang Naskah"
        st.rerun()
with col3:
    if st.button("🎧 Studio Rekaman", use_container_width=True):
        st.session_state.menu_aktif = "2. Studio Rekaman"
        st.rerun()

st.divider()

# --- ROUTER LOGIC ---
if st.session_state.menu_aktif == "Home":
    st.subheader("Selamat Datang, Bapak Musa!")
    st.write("Silakan pilih mana ruangan kerja dan direktur kreatif yang kamu perlukan? Apakah Direktur Kreatif Penyusun Naskah, atau Direktur Kreatif Perekaman Suara?")
    st.info("💡 **Petunjuk:** Silakan klik tombol **📝 Ruang Naskah** di atas untuk meracik skrip bersama Direktur Kreatif, atau **🎧 Studio Rekaman** jika Anda sudah punya teks yang ingin langsung diubah menjadi suara.")

elif st.session_state.menu_aktif == "1. Ruang Naskah":
    naskah.run()

elif st.session_state.menu_aktif == "2. Studio Rekaman":
    vo.run()
