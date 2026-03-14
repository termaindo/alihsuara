import streamlit as st
import subprocess
import sys

# Paksa instalasi jika requirements.txt gagal
try:
    import google.cloud.texttospeech
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-cloud-text-to-speech"])

st.title("Tes Koneksi Suara")
st.success("Jika tulisan ini muncul, berarti Library Suara sudah berhasil terpasang!")
