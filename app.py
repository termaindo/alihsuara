import streamlit as st
from modules import naskah, vo, infografis

st.set_page_config(page_title="Studio Kreatif Pro", page_icon="✨", layout="wide")

# Header Utama Aplikasi
st.markdown("<h2 style='text-align: center; color: #1E88E5;'>✨ Studio Kreatif Pro</h2>", unsafe_allow_html=True)

# 1. DAFTAR NAMA MENU STANDAR (MUTLAK)
daftar_menu = [
    "1. Studio Kreasi Naskah", 
    "2. Studio Kreasi Suara / Audio", 
    "3. Studio Kreasi Cetak / Visual"
]

# 2. SOLUSI ANTI-ERROR (VALUE ERROR FIX)
# Jika memori browser masih menyimpan nama menu versi lama, 
# sistem akan mendeteksinya dan otomatis mereset ke menu pertama agar tidak crash.
if "menu_aktif" not in st.session_state or st.session_state.menu_aktif not in daftar_menu:
    st.session_state.menu_aktif = daftar_menu[0]

# 3. MENU MENDATAR / HORIZONTAL (TANPA SIDEBAR SAMA SEKALI)
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
menu = st.radio(
    "Pilih Ruang Kerja:",
    options=daftar_menu,
    index=daftar_menu.index(st.session_state.menu_aktif),
    horizontal=True,
    label_visibility="collapsed" # Menyembunyikan judul radio button agar tampilannya bersih
)
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# Simpan pilihan menu yang sedang aktif
st.session_state.menu_aktif = menu

# 4. PENGALIHAN (ROUTING) KE MASING-MASING STUDIO
if menu == "1. Studio Kreasi Naskah":
    naskah.run()
elif menu == "2. Studio Kreasi Suara / Audio":
    vo.run()
elif menu == "3. Studio Kreasi Cetak / Visual":
    infografis.run()
