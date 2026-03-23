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
# FUNGSI: PEMROSESAN GAMBAR (RESIZE)
# ==========================================
def process_product_image(uploaded_file):
    try:
        image = Image.open(uploaded_file)
        # [CRITICAL] Batasi resolusi agar RAM server tetap aman
        image.thumbnail((800, 800))
        
        buf = BytesIO()
        image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        base64_img = base64.b64encode(byte_im).decode('utf-8')
        return f"data:image/png;base64,{base64_img}"
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses gambar: {e}")
        return None

# ==========================================
# FUNGSI: EKSTRAKSI NASKAH KE JSON (GEMINI 2.5 FLASH)
# ==========================================
def generate_json_structure(naskah):
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    Ubah naskah promosi berikut menjadi struktur data JSON murni.
    Format wajib:
    {{
        "infographic_title": "Judul Singkat",
        "items": ["Poin 1", "Poin 2", "Poin 3"]
    }}
    Naskah Mentah:
    {naskah}
    """
    try:
        response = model.generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(response.text)
    except Exception:
        return {"error": "429"}

# ==========================================
# ENGINE TEMA CSS & LAYOUT (READABILITY OPTIMIZED)
# ==========================================
def get_theme_css(theme_name, layout_type, mode_foto):
    # Pengaturan Layout Dimensi
    if layout_type == "Square (1:1)":
        aspect_ratio, max_width = "1 / 1", "450px"
    elif layout_type == "Portrait (9:16)":
        aspect_ratio, max_width = "9 / 16", "350px"
    else: # Landscape (16:9)
        aspect_ratio, max_width = "16 / 9", "700px"

    # Palet Tema dengan Kontras Tinggi & Tipografi Lega
    themes = {
        "minimalist": {"bg": "#ffffff", "text": "#333333", "accent": "#f9f9f9", "font": "sans-serif"},
        "elegant_dark": {"bg": "#1a1a2e", "text": "#ffffff", "accent": "#16213e", "font": "serif"},
        "modern_gradient": {"bg": "linear-gradient(135deg, #667eea, #764ba2)", "text": "#ffffff", "accent": "rgba(255,255,255,0.15)", "font": "sans-serif"},
        "earthy_nature": {"bg": "#e9e5cd", "text": "#4b6542", "accent": "#d4cda3", "font": "sans-serif"},
        "vibrant_pop": {"bg": "#ffeb3b", "text": "#212121", "accent": "#ffffff", "font": "Impact, sans-serif"}
    }
    
    t = themes.get(theme_name, themes["minimalist"])
    color_main = t["text"]

    # Logika Tampilan Foto
    if mode_foto == "Foto Studio (Latar Putih)":
        img_style = "mix-blend-mode: multiply; filter: drop-shadow(0px 15px 25px rgba(0,0,0,0.15));"
    else:
        img_style = "border-radius: 12px; border: 4px solid white; box-shadow: 0 15px 35px rgba(0,0,0,0.2);"

    css = f"""
    <style>
        .poster-container {{
            width: 100%; max-width: {max_width}; aspect-ratio: {aspect_ratio};
            background: {t['bg']}; color: {color_main}; font-family: {t['font']};
            margin: 0 auto; display: flex; flex-direction: column;
            justify-content: space-between; border-radius: 20px;
            padding: 35px; box-sizing: border-box; position: relative;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        .poster-header {{ 
            text-align: center; font-size: 1.5em; font-weight: 600; 
            text-transform: uppercase; margin-bottom: 20px; 
            line-height: 1.3; letter-spacing: 0.5px;
        }}
        .poster-content {{ 
            display: flex; flex-direction: column; align-items: center; 
            justify-content: center; flex-grow: 1; gap: 25px; 
        }}
        .poster-image-wrap {{ width: 100%; display: flex; justify-content: center; }}
        .poster-image-wrap img {{
            max-width: 95%; max-height: 280px; object-fit: contain;
            {img_style}
        }}
        .items-container {{ width: 100%; display: flex; flex-direction: column; gap: 12px; }}
        .item-box {{ 
            background: {t['accent']}; padding: 14px 18px; border-radius: 10px; 
            font-size: 0.95em; width: 100%; font-weight: 500; 
            line-height: 1.5; border-left: 5px solid {color_main};
            box-sizing: border-box;
        }}
        .poster-footer {{ 
            text-align: center; font-size: 0.75em; border-top: 1px solid rgba(128,128,128,0.2); 
            padding-top: 15px; margin-top: 20px; font-weight: 600; opacity: 0.8;
        }}
    </style>
    """
    return css

def render_html_poster(json_data, base64_img, layout_type, theme_name, mode_foto):
    css = get_theme_css(theme_name, layout_type, mode_foto)
    items_html = "".join([f"<div class='item-box'>✓ {i}</div>" for i in json_data.get("items", [])])
    
    html = f"""
    {css}
    <div class="poster-container">
        <div class="poster-header">{json_data.get('infographic_title', 'Visual Produk')}</div>
        <div class="poster-content">
            <div class="poster-image-wrap"><img src="{base64_img}"></div>
            <div class="items-container">{items_html}</div>
        </div>
        <div class="poster-footer">
            <div>Studio Kreatif Pro - KTB UKM JATIM</div>
            <div>📸 @ktbukm.jatim | 🌐 https://ktbukm-jatim.store</div>
        </div>
    </div>
    """
    return html

# ==========================================
# FUNGSI: INSTRUKSI PROMPT MANUAL
# ==========================================
def create_manual_prompt(naskah):
    return f"""
    *Salin teks di bawah ini dan tempel di ChatGPT atau Gemini Web:*

    "Buatkan saya ide desain infografis atau poster untuk mempromosikan produk saya. 
    Gunakan elemen visual yang menarik dan layout yang profesional.
    
    Berikut adalah naskah dasar yang ingin saya sampaikan:
    {naskah}
    
    Tolong berikan rekomendasi warna, tata letak teks, dan konsep gambar yang cocok."
    """

# ==========================================
# MODUL UTAMA RUN()
# ==========================================
def run():
    st.title("🎨 Ruang 3: Studio Cetak / Visual")
    setup_gemini()

    naskah_mentah = st.session_state.get("hasil_naskah", "")
    if not naskah_mentah:
        st.info("ℹ️ Silakan buat naskah di Ruang 1: Studio Kreasi Naskah terlebih dahulu.")
        naskah_mentah = "Produk Unggulan UMKM Jawa Timur."

    st.markdown("---")
    
    st.markdown("### 1. Pengaturan Foto")
    mode_foto = st.radio(
        "Pilih Jenis Foto yang Diunggah:",
        ["Foto Studio (Latar Putih)", "Foto Estetik / Sudah Ada Latar"],
        help="Gunakan 'Foto Studio' jika foto berlatar putih bersih agar produk terlihat menyatu dengan desain poster.",
        horizontal=True
    )

    uploaded_file = st.file_uploader("Pilih foto produk (JPG/PNG)", type=['jpg', 'jpeg', 'png'])
    
    col1, col2 = st.columns(2)
    with col1:
        layout_choice = st.selectbox("Pilih Dimensi Desain:", ["Portrait (9:16)", "Square (1:1)", "Landscape (16:9)"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 Buat Desain Visual Sekarang!", type="primary"):
        if not uploaded_file:
            st.warning("⚠️ Mohon unggah foto produk Anda agar direktur kreatif bisa bekerja.")
        else:
            with st.spinner("⚙️ Direktur kreatif sedang memproduksi visual cetakan..."):
                base64_img = process_product_image(uploaded_file)
                json_data = generate_json_structure(naskah_mentah)
                
                if isinstance(json_data, dict) and json_data.get("error") == "429":
                    st.error("⏳ Server sedang penuh. Tunggu 1 menit lalu tekan tombol lagi.")
                else:
                    st.success("✨ Visual Berhasil Dicetak!")
                    
                    # Pilih tema acak
                    themes_list = ["minimalist", "elegant_dark", "modern_gradient", "earthy_nature", "vibrant_pop"]
                    theme = random.choice(themes_list)
                    
                    html_poster = render_html_poster(json_data, base64_img, layout_choice, theme, mode_foto)
                    
                    # Tampilan Visual
                    st.components.v1.html(html_poster, height=750, scrolling=True)
                    
                    # TOMBOL DOWNLOAD (TANPA TULISAN HTML DI DALAM KURUNG)
                    full_html = f"<html><body style='margin:0; background:#f0f2f6; padding:20px;'>{html_poster}</body></html>"
                    st.download_button(
                        label="📥 Unduh Hasil Desain",
                        data=full_html,
                        file_name="desain_produk_umkm.html",
                        mime="text/html",
                        use_container_width=True
                    )
            
            # PROMPT SIAP COPAS
            st.markdown("---")
            st.markdown("### 💡 Instruksi Praktis Prompt Manual")
            st.info("Salin teks di bawah ini jika Anda ingin mencoba desain di aplikasi AI lain:")
            st.code(create_manual_prompt(naskah_mentah), language="text")
