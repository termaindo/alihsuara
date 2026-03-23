import streamlit as st
import google.generativeai as genai
import json
import random
import base64
import re
from io import BytesIO
from PIL import Image
from google.api_core.exceptions import ResourceExhausted

# ==========================================
# KONFIGURASI API GEMINI
# ==========================================
def setup_gemini():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
    except Exception:
        st.error("🔑 Kunci API Gemini belum dikonfigurasi di st.secrets.")

# ==========================================
# FUNGSI: PEMROSESAN GAMBAR
# ==========================================
def process_product_image(uploaded_file):
    try:
        image = Image.open(uploaded_file)
        # Resize tetap dilakukan agar hemat RAM & Bandwidth
        image.thumbnail((800, 800))
        
        buf = BytesIO()
        image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        base64_img = base64.b64encode(byte_im).decode('utf-8')
        return f"data:image/png;base64,{base64_img}"
    except Exception as e:
        st.error(f"Gagal memproses gambar: {e}")
        return None

# ==========================================
# FUNGSI: EKSTRAKSI NASKAH KE JSON (GEMINI)
# ==========================================
def generate_json_structure(naskah):
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    Ubah naskah promosi ini menjadi JSON murni untuk poster.
    Format: {{"infographic_title": "Judul", "items": ["Poin 1", "Poin 2"]}}
    Naskah: {naskah}
    """
    try:
        response = model.generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        return json.loads(match.group(0)) if match else json.loads(response.text)
    except Exception:
        return {"error": "429"}

# ==========================================
# ENGINE TEMA CSS & LAYOUT (9:16 & MODE PILIHAN)
# ==========================================
def get_theme_css(theme_name, layout_type, mode_foto):
    # Dimensi
    if layout_type == "Square (1:1)":
        aspect_ratio, max_width = "1 / 1", "450px"
    elif layout_type == "Portrait (9:16)":
        aspect_ratio, max_width = "9 / 16", "350px"
    else:
        aspect_ratio, max_width = "16 / 9", "700px"

    themes = {
        "minimalist": {"bg": "#ffffff", "text": "#333333", "accent": "#f0f0f0", "font": "sans-serif"},
        "elegant_dark": {"bg": "#1a1a2e", "text": "#e94560", "accent": "#16213e", "font": "serif"},
        "modern_gradient": {"bg": "linear-gradient(135deg, #667eea, #764ba2)", "text": "#ffffff", "accent": "rgba(255,255,255,0.2)", "font": "sans-serif"},
        "earthy_nature": {"bg": "#e9e5cd", "text": "#4b6542", "accent": "#d4cda3", "font": "sans-serif"},
        "vibrant_pop": {"bg": "#ffdf00", "text": "#ff007f", "accent": "#00d2ff", "font": "Impact"}
    }
    
    t = themes.get(theme_name, themes["minimalist"])
    color_main = t["text"] if theme_name != "modern_gradient" else "#ffffff"

    # Logika CSS berdasarkan Mode Foto
    if mode_foto == "Foto Studio (Latar Putih)":
        # Gunakan trik transparan
        img_style = "mix-blend-mode: multiply; filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.1));"
    else:
        # Gunakan foto asli utuh dengan bingkai cantik
        img_style = "border-radius: 12px; border: 3px solid white; box-shadow: 0 10px 25px rgba(0,0,0,0.2);"

    css = f"""
    <style>
        .poster-container {{
            width: 100%; max-width: {max_width}; aspect-ratio: {aspect_ratio};
            background: {t['bg']}; color: {color_main}; font-family: {t['font']};
            margin: 0 auto; display: flex; flex-direction: column;
            justify-content: space-between; border-radius: 15px;
            padding: 25px; box-sizing: border-box; box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        }}
        .poster-header {{ text-align: center; font-size: 1.4em; font-weight: bold; text-transform: uppercase; }}
        .poster-content {{ display: flex; flex-direction: column; align-items: center; justify-content: center; flex-grow: 1; gap: 15px; }}
        .poster-image-wrap {{ width: 100%; display: flex; justify-content: center; }}
        .poster-image-wrap img {{
            max-width: 95%; max-height: 280px; object-fit: cover;
            {img_style}
        }}
        .item-box {{ background: {t['accent']}; padding: 10px; border-radius: 8px; font-size: 0.85em; width: 100%; font-weight: 500; }}
        .poster-footer {{ 
            text-align: center; font-size: 0.65em; border-top: 1px solid rgba(128,128,128,0.3); 
            padding-top: 10px; margin-top: 10px; font-weight: bold;
        }}
    </style>
    """
    return css

def render_html_poster(json_data, base64_img, layout_type, theme_name, mode_foto):
    css = get_theme_css(theme_name, layout_type, mode_foto)
    items_html = "".join([f"<div class='item-box'>✓ {i}</div>" for i in json_data.get("items", [])])
    
    return f"""
    {css}
    <div class="poster-container">
        <div class="poster-header">{json_data.get('infographic_title', 'Visual Produk')}</div>
        <div class="poster-content">
            <div class="poster-image-wrap"><img src="{base64_img}"></div>
            <div style="width: 100%; display: flex; flex-direction: column; gap: 8px;">{items_html}</div>
        </div>
        <div class="poster-footer">
            <div>Studio Kreatif Pro - KTB UKM JATIM</div>
            <div>📸 @ktbukm.jatim | 🌐 https://ktbukm-jatim.store</div>
        </div>
    </div>
    """

# ==========================================
# MODUL UTAMA RUN()
# ==========================================
def run():
    st.title("🎨 Ruang 3: Studio Cetak / Visual")
    setup_gemini()

    naskah_mentah = st.session_state.get("hasil_naskah", "")
    if not naskah_mentah:
        st.info("ℹ️ Silakan buat naskah di Ruang 1 terlebih dahulu.")
        naskah_mentah = "Produk UMKM Berkualitas Tinggi."

    st.markdown("---")
    
    st.markdown("### 1. Pengaturan Foto")
    # PILIHAN MODE FOTO (PENGATURAN BARU)
    mode_foto = st.radio(
        "Jenis Foto yang Anda Unggah:",
        ["Foto Studio (Latar Putih)", "Foto Estetik / Sudah Ada Latar"],
        help="Pilih 'Foto Studio' jika foto berlatar putih polos agar produk terlihat menyatu dengan poster. Pilih 'Foto Estetik' jika foto Anda sudah bagus seperti hasil produksi AI atau studio kontekstual."
    )

    uploaded_file = st.file_uploader("Pilih foto produk (JPG/PNG)", type=['jpg', 'jpeg', 'png'])
    
    col1, col2 = st.columns(2)
    with col1:
        layout_choice = st.selectbox("Pilih Dimensi Visual:", ["Portrait (9:16)", "Square (1:1)", "Landscape (16:9)"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 Buat Desain Visual Sekarang!", type="primary"):
        if not uploaded_file:
            st.warning("⚠️ Silakan unggah foto produk Anda terlebih dahulu.")
        else:
            # SPINNEER/LOADING SESUAI INSTRUKSI
            with st.spinner("⚙️ Direktur kreatif sedang memproduksi visual cetakan..."):
                base64_img = process_product_image(uploaded_file)
                json_data = generate_json_structure(naskah_mentah)
                
                if isinstance(json_data, dict) and json_data.get("error") == "429":
                    st.error("⏳ Server Google sedang mendinginkan mesin. Tunggu 1 menit.")
                else:
                    st.success("✨ Visual Berhasil Dicetak!")
                    theme = random.choice(["minimalist", "elegant_dark", "modern_gradient", "earthy_nature", "vibrant_pop"])
                    html_poster = render_html_poster(json_data, base64_img, layout_choice, theme, mode_foto)
                    st.components.v1.html(html_poster, height=750, scrolling=True)
