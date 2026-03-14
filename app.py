import os
import subprocess
import sys

# --- PAKSA INSTALASI LIBRARY ---
def install_library(package):
    try:
        __import__(package.replace("-", "_"))
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Coba paksa instal
install_library("google-cloud-text-to-speech")
install_library("google-generativeai")

import streamlit as st
from google.cloud import texttospeech

st.title("Uji Coba Paksa Instalasi")
st.success("Jika Bapak melihat pesan ini, berarti library sudah berhasil dipasang paksa!")
