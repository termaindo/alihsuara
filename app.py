import streamlit as st
import sys

st.title("Audit Sistem Sulih Suara")

st.write("### 1. Informasi Sistem")
st.write(f"Versi Python: {sys.version}")

st.write("### 2. Pengecekan Library")

# Cek Streamlit
try:
    import streamlit
    st.success("✅ Streamlit terpasang dengan benar.")
except ImportError:
    st.error("❌ Streamlit tidak ditemukan.")

# Cek Google Generative AI (Gemini)
try:
    import google.generativeai
    st.success("✅ Google Generative AI terpasang dengan benar.")
except ImportError:
    st.error("❌ Google Generative AI tidak ditemukan.")

# Cek Google Cloud Text-to-Speech
try:
    from google.cloud import texttospeech
    st.success("✅ Google Cloud Text-to-Speech terpasang dengan benar.")
except ImportError:
    st.error("❌ Google Cloud Text-to-Speech tidak ditemukan.")

st.divider()
st.write("Jika semua tanda centang berwarna hijau (✅), berarti masalahnya bukan pada instalasi, melainkan pada pengaturan 'Secrets' atau logika kode sebelumnya.")
