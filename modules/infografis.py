import streamlit as st
import re
import os
import json
import requests
import base64
import time

# ==========================================
# 🧩 1. SAFE IMAGE GENERATOR (HUGGING FACE)
# ==========================================
def generate_image_with_retry(prompt, negative_prompt="", dimensi=""):
    """Fungsi pembuat gambar dengan Hugging Face yang kebal terhadap Model Loading (503) & Mendukung Dimensi."""
    hf_key = st.secrets.get("HUGGINGFACE_API_KEY")
    if not hf_key:
        st.warning("⚠️ Kunci HUGGINGFACE_API_KEY tidak ditemukan!")
        return None
        
    # PERBAIKAN: Menggunakan URL router terbaru dari Hugging Face
    API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {hf_key}"}
    
    # Menyesuaikan resolusi (Width & Height) sesuai pilihan pengguna
    w, h = 1024, 1024 # Default Square
    if "Portrait" in dimensi:
        w, h = 896, 1152
    elif "Vertical" in dimensi:
        w, h = 768, 1344
    elif "Landscape" in dimensi:
        w, h = 1344, 768

    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": negative_prompt,
            "width": w,
            "height": h
        }
    }
    
    # Mekanisme Retry (Hugging Face API sering kali butuh waktu pemanasan)
    for attempt in range(3):
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            encoded = base64.b64encode(response.content).decode('utf-8')
            return f"data:image/png;base64,{encoded}"
        elif response.status_code == 503:
            # Jika Model Loading, tunggu 5 detik lalu coba lagi
            time.sleep(5)
            continue
        else:
            # Jika error lain (seperti kuota habis/kunci salah)
            st.warning(f"⚠️ Pelukis AI Error: {response.text}")
            return None
            
    st.warning("⚠️ Mesin Pelukis Hugging Face sedang sangat sibuk. Menggunakan Mode Cepat sementara.")
    return None

def safe_generate_image(prompt, negative_prompt="", dimensi=""):
    """Wraper cache cerdas agar tidak mencache kegagalan (NULL)"""
    # Inisialisasi custom cache di session_state
    if "img_cache" not in st.session_state:
        st.session_state.img_cache = {}
        
    cache_key = f"{prompt}_{dimensi}"
    
    # Jika sudah sukses dilukis sebelumnya, ambil dari cache
    if cache_key in st.session_state.img_cache:
        return st.session_state.img_cache[cache_key]
        
    # Jika belum, lukis gambar baru
    img_result = generate_image_with_retry(prompt, negative_prompt, dimensi)
    
    # HANYA simpan ke cache jika sukses!
    if img_result:
        st.session_state.img_cache[cache_key] = img_result
        
    return img_result

def is_quota_ok():
    """Mengecek apakah API Key Hugging Face tersedia."""
    return bool(st.secrets.get("HUGGINGFACE_API_KEY"))

# ==========================================
# 🧩 2. GROQ Llama 3.3 70B WRAPPER (JSON & PROMPT OPTIMIZER)
# ==========================================
def generate_structured_text_groq(prompt_text, opsi_slide, opsi_dimensi):
    """
    Menggunakan Groq untuk memecah naskah menjadi JSON Slide 
    sekaligus meracik Positive & Negative Prompt untuk Image Generator.
    """
    groq_key = st.secrets.get("GROQ_API_KEY")
    if not groq_key:
        raise Exception("GROQ_API_KEY tidak ditemukan di st.secrets! Silakan tambahkan terlebih dahulu.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json"
    }

    system_prompt = f"""Kamu adalah Ahli Desain Visual dan Prompt Engineer Profesional.
Tugasmu memecah teks menjadi slide infografis dan membuat 'image_prompt' (deskripsi gambar SANGAT DETAIL dalam Bahasa Inggris) serta 'negative_prompt' (elemen yang harus dihindari) untuk disuapkan ke AI Pelukis (Stable Diffusion).
Format output HARUS JSON valid dengan struktur berikut:
{{
  "slides": [
    {{
      "slide_number": 1,
      "title": "Judul Slide",
      "content": "Teks ringkas (sesuaikan kepadatan dengan dimensi {opsi_dimensi}). HINDARI TEKS TERLALU PANJANG JIKA DIMENSI SQUARE.",
      "image_prompt": "professional infographic illustration, highly detailed, clean vector, minimalist, [objek utama]... (sesuaikan komposisi/aspect ratio untuk {opsi_dimensi})",
      "negative_prompt": "text, watermark, ugly, blurry, deformed, cluttered"
    }}
  ]
}}"""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Dimensi Target: {opsi_dimensi}\nTarget Jumlah Slide: {opsi_slide}\nTeks Dasar yang harus diproses:\n{prompt_text}"}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.5
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        content_str = result["choices"][0]["message"]["content"]
        data = json.loads(content_str)
        return data.get("slides", [])
    else:
        raise Exception(f"Gagal menghubungi Groq: {response.text}")

# ==========================================
# 🧩 3. SMART VISUAL DECISION SYSTEM (SVDS)
# ==========================================
def decide_mode(user_mode, quota_ok, num_pages):
    if user_mode == "cepat":
        return "no_image"
    if user_mode == "visual":
        return "one_image" if quota_ok else "no_image"
    if user_mode == "lengkap":
        if quota_ok and num_pages <= 3:
            return "multi_image"
        elif quota_ok:
            return "one_image"
        else:
            return "no_image"
    return "no_image"

# ==========================================
# 🧩 4. HTML RENDERER ENGINE
# ==========================================
def render_html_cards(pages):
    """Template HTML dinamis yang sangat kebal terhadap layout rusak/pecah."""
    html_content = """
    <style>
        .infographic-container {
            display: flex;
            flex-direction: column;
            gap: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .slide-card {
            display: flex;
            flex-direction: row;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            overflow: hidden;
            border: 1px solid #e0e0e0;
            min-height: 250px;
        }
        .slide-content {
            padding: 25px;
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .slide-number {
            font-size: 0.8em;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        .slide-title {
            color: #2c3e50;
            margin: 0 0 15px 0;
            font-size: 1.5em;
        }
        .slide-text {
            color: #555;
            line-height: 1.6;
            margin: 0;
        }
        .slide-image-container {
            flex: 0 0 40%;
            background: #f8f9fa;
            display: flex;
            align-items: center;
            justify-content: center;
            border-right: 1px solid #e0e0e0;
            min-height: 250px;
        }
        .slide-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        @media (max-width: 600px) {
            .slide-card { flex-direction: column; }
            .slide-image-container {
                border-right: none;
                border-bottom: 1px solid #e0e0e0;
                height: 200px;
                min-height: 200px;
            }
        }
    </style>
    <div class="infographic-container">
    """
    
    for page in pages:
        img_html = ""
        # 🧩 CONDITIONAL RENDERING
        if page.get("image"):
            img_html = f"""
            <div class="slide-image-container">
                <img src="{page['image']}" class="slide-image" alt="Ilustrasi">
            </div>
            """
            
        html_content += f"""
        <div class="slide-card">
            {img_html}
            <div class="slide-content">
                <div class="slide-number">Slide {page.get('slide_number', '-')}</div>
                <h3 class="slide-title">{page.get('title', 'Judul')}</h3>
                <p class="slide-text">{page.get('content', '')}</p>
            </div>
        </div>
        """
        
    html_content += "</div>"
    return html_content

# ==========================================
# 🚀 MAIN APP RUNNER
# ==========================================
def run():
    st.title("🎨 Ruang 3: Studio Cetak (Visual & Infografis)")
    st.info("💡 **Ditenagai Groq Llama 3.3 70B & Hugging Face:** Modul ini telah 100% menggunakan infrastruktur Multi-AI terbaru untuk kecepatan kilat dan stabilitas Visual (SVDS).")

    # 1. TARIK NASKAH DARI STATE SECARA AMAN (ANTI CUT-OFF)
    raw_text = st.session_state.get("hasil_naskah", "")
    if not raw_text:
        st.warning("Belum ada naskah yang ditarik. Silakan buat naskah terlebih dahulu di Ruang 1 (Rapat Naskah).")
        return

    naskah_final = raw_text
    
    bt = chr(96) * 3 
    pattern = rf"{bt}(?:text|markdown|xml)?\n(.*?)({bt})"
    match_naskah = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)
    
    if match_naskah:
        naskah_final = match_naskah.group(1).strip()
        st.success("✅ Naskah dasar berhasil ditarik otomatis dari Ruang 1!")

    # 2. USER INPUT (UI)
    st.markdown("### 🎛️ Pengaturan Sistem & Desain")
    
    col1, col2 = st.columns(2)
    with col1:
        user_mode = st.selectbox(
            "1. Pilih Mode Render:",
            options=["cepat", "visual", "lengkap"],
            index=0,
            format_func=lambda x: {
                "cepat": "⚡ Cepat (Teks Saja - Tanpa Gambar)",
                "visual": "🖼️ Visual (1 Gambar Cover Saja)",
                "lengkap": "🌟 Lengkap (Gambar Tiap Slide)"
            }.get(x)
        )
        
        opsi_dimensi = st.selectbox(
            "2. Ukuran Dimensi / Platform:", 
            [
                "Pilih...",
                "1080 x 1080 px (Square / IG Feed)",
                "1080 x 1350 px (Portrait / IG Feed)",
                "1080 x 1920 px (Vertical / IG Story / TikTok)",
                "1920 x 1080 px (Landscape / Presentasi PPT / YouTube)"
            ]
        )
        
    with col2:
        opsi_slide = st.selectbox(
            "3. Target Jumlah Slide:", 
            [
                "Pilih...", 
                "Otomatis", 
                "1 Slide (Satu Halaman Penuh)", 
                "3 Slide", 
                "5 Slide", 
                "10 Slide", 
                "Isi sendiri..."
            ]
        )
        
        jawaban_slide = opsi_slide
        if opsi_slide == "Isi sendiri...":
            jawaban_slide = st.text_input("Masukkan target jumlah slide (misal: 7 slide, 2 halaman, dll):", placeholder="Contoh: 7 slide")

    user_input = st.text_area("Draft Naskah Dasar:", value=naskah_final, height=150)

    # 3. PROSES EKSEKUSI
    if st.button("✨ Hasilkan Infografis Cerdas", use_container_width=True, type="primary"):
        if opsi_dimensi == "Pilih..." or jawaban_slide == "Pilih..." or not jawaban_slide.strip():
            st.warning("⚠️ Mohon lengkapi pilihan Dimensi dan Target Jumlah Slide terlebih dahulu!")
            return
            
        if not user_input.strip():
            st.warning("⚠️ Draft naskah tidak boleh kosong!")
            return
            
        with st.spinner("🤖 Groq Llama 3.3 sedang mengoptimasi prompt & menstrukturkan data..."):
            try:
                # A. TEXT & PROMPT GENERATION VIA GROQ
                pages = generate_structured_text_groq(user_input, jawaban_slide, opsi_dimensi)
                
                num_pages = len(pages)
                quota_ok = is_quota_ok()
                
                # B. SVDS (DECISION ENGINE)
                final_mode = decide_mode(user_mode, quota_ok, num_pages)
                st.info(f"🧠 **Keputusan SVDS:** Sistem menjalankan mode `{final_mode}`.")
                
                # C. IMPLEMENTASI PER MODE (HUGGING FACE)
                with st.spinner("🎨 Merender elemen visual via Hugging Face (Harap tunggu, pelukis AI mungkin sedang bersiap)..."):
                    if final_mode == "no_image":
                        for page in pages:
                            page["image"] = None
                            
                    elif final_mode == "one_image":
                        main_prompt = pages[0].get("image_prompt", "Professional infographic design")
                        neg_prompt = pages[0].get("negative_prompt", "ugly, text, watermark")
                        # Mengirimkan opsi_dimensi ke pelukis
                        img = safe_generate_image(main_prompt, neg_prompt, opsi_dimensi)
                        for idx, page in enumerate(pages):
                            page["image"] = img if idx == 0 else None
                            
                    elif final_mode == "multi_image":
                        for page in pages:
                            p_prompt = page.get("image_prompt", "Minimalist vector illustration")
                            n_prompt = page.get("negative_prompt", "ugly, text, watermark")
                            page["image"] = safe_generate_image(p_prompt, n_prompt, opsi_dimensi)
                
                # D. RENDER HTML (OUTPUT)
                st.success("🎉 Infografis berhasil dirender!")
                final_html = render_html_cards(pages)
                st.components.v1.html(final_html, height=800, scrolling=True)
                
                # E. BAGIAN DOWNLOAD HASIL GAMBAR (BARU)
                image_pages = [p for p in pages if p.get('image')]
                if image_pages:
                    st.divider()
                    st.markdown("### 📥 Download Hasil Visual")
                    cols = st.columns(len(image_pages))
                    
                    for i, page in enumerate(image_pages):
                        b64_data = page["image"].split(",")[1]
                        img_bytes = base64.b64decode(b64_data)
                        
                        with cols[i]:
                            st.image(img_bytes, caption=f"Visual Slide {page.get('slide_number', i+1)}")
                            st.download_button(
                                label=f"⬇️ Download Gambar {i+1}",
                                data=img_bytes,
                                file_name=f"infografis_visual_slide_{page.get('slide_number', i+1)}.png",
                                mime="image/png",
                                use_container_width=True,
                                key=f"dl_btn_{i}"
                            )
                
                # Data Debugging untuk Ahli Developer
                with st.expander("🛠️ Lihat Data JSON Groq Mentah (Untuk Developer)"):
                    clean_pages = [{k: (v if k != 'image' else ('[BASE64_IMAGE_DATA]' if v else None)) for k, v in p.items()} for p in pages]
                    st.json(clean_pages)

            except Exception as e:
                st.error(f"❌ Terjadi kesalahan pada proses generasi: {str(e)}")

    # 4. NAVIGASI BAWAH
    st.divider()
    st.markdown("### 🚀 Lanjut Produksi Karya Lain")
    
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("🎙️ Ke Studio Rekaman (VO)", use_container_width=True):
            st.session_state.menu_aktif = "2. Studio Rekaman"
            st.rerun()
    with col_nav2:
        if st.button("📝 Kembali ke Ruang Naskah", use_container_width=True):
            st.session_state.menu_aktif = "1. Ruang Naskah"
            st.rerun()
