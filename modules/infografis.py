import streamlit as st
import re
import os
import json
import requests
import base64
import time

# ==========================================
# 🧩 1. HUGGING FACE IMAGE GENERATOR (FLUX)
# ==========================================
def generate_image_with_retry(prompt, dimensi=""):
    """Menggunakan model FLUX.1 dengan URL Router Hugging Face terbaru."""
    hf_key = st.secrets.get("HUGGINGFACE_API_KEY")
    if not hf_key:
        st.warning("⚠️ Kunci HUGGINGFACE_API_KEY tidak ditemukan!")
        return None
        
    API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {hf_key}"}
    
    # Resolusi default untuk ilustrasi tengah
    w, h = 1024, 1024 
    if "Portrait" in dimensi or "Vertical" in dimensi:
        w, h = 896, 1152 # Proporsi vertikal

    payload = {
        "inputs": prompt,
        "parameters": {
            "width": w,
            "height": h
        }
    }
    
    for attempt in range(3):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=40)
            if response.status_code == 200:
                encoded = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/png;base64,{encoded}"
            elif response.status_code == 503:
                time.sleep(5) 
                continue
            else:
                return None
        except Exception as e:
            time.sleep(3)
            continue
            
    return None

# ==========================================
# 🧩 2. GROQ Llama 3.3 70B WRAPPER
# ==========================================
def generate_structured_text_groq(prompt_text, opsi_slide):
    """
    Menggunakan Groq untuk memproduksi Multi-Slide Array.
    """
    groq_key = st.secrets.get("GROQ_API_KEY")
    if not groq_key:
        raise Exception("GROQ_API_KEY tidak ditemukan di st.secrets!")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json"
    }

    system_prompt = f"""Kamu adalah Ahli Desain Visual dan Copywriter Profesional.
Tugasmu memecah teks menjadi FORMAT MULTI-SLIDE infografis padat bergaya modern.
Format output HARUS JSON valid dengan struktur array 'slides' berikut:
{{
  "slides": [
    {{
      "slide_number": 1,
      "infographic_title": "Judul Slide Utama (Maks 5 Kata)",
      "image_prompt": "professional poster illustration, clean vector, minimalist, highly detailed, [DESKRIPSI BENDA NYATA SESUAI KONTEKS NASKAH, misal: botol sabun cair alami dengan busa / grafik saham hijau dengan koin emas]...",
      "items": [
        {{
          "icon_emoji": "🌍",
          "title": "Sub Judul Poin",
          "content": "Penjelasan sangat singkat, maksimal 2 baris."
        }}
      ]
    }}
  ]
}}
ATURAN MUTLAK KUALITAS: 
1. Buat jumlah slide di dalam array "slides" TEPAT sesuai dengan permintaan pengguna berikut: {opsi_slide}. Jika diminta 3 Slide, array WAJIB berisi 3 object slide yang bersambung menceritakan naskah.
2. Isian "image_prompt" WAJIB relevan dengan produk/topik di dalam naskah! Jangan buat objek acak.
3. Gunakan Emoji yang relevan di tiap "icon_emoji"."""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Teks Dasar yang harus diproses menjadi {opsi_slide}:\n{prompt_text}"}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.5
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        content_str = result["choices"][0]["message"]["content"]
        return json.loads(content_str)
    else:
        raise Exception(f"Gagal menghubungi Groq: {response.text}")

# ==========================================
# 🧩 3. WEB-BASED LAYOUT ENGINE (MULTI-SLIDE)
# ==========================================
def render_beautiful_html_poster(data_json, b64_images, opsi_dimensi):
    """
    Merender HTML yang memuat MULTIPLE Poster (Carousel) berderet ke bawah,
    lengkap dengan tombol download masing-masing.
    """
    max_width = "800px" if "Square" in opsi_dimensi else "650px"
    slides = data_json.get("slides", [])
    
    all_posters_html = ""
    
    # Looping pembuatan HTML untuk setiap slide
    for idx, slide in enumerate(slides):
        slide_num = slide.get("slide_number", idx + 1)
        b64_img = b64_images[idx] if idx < len(b64_images) else ""
        
        img_element = f'<img src="{b64_img}" class="hero-image" alt="Ilustrasi Slide {slide_num}">' if b64_img else ""
            
        items_html = ""
        for item in slide.get("items", []):
            icon = item.get("icon_emoji", "✨")
            title = item.get("title", "Judul Poin")
            content = item.get("content", "Deskripsi poin.")
            
            items_html += f"""
            <div class="card">
                <div class="card-icon">{icon}</div>
                <div class="card-text">
                    <div class="card-title">{title}</div>
                    <div class="card-desc">{content}</div>
                </div>
            </div>
            """
            
        poster_id = f"poster-container-{slide_num}"
        btn_id = f"btn-{slide_num}"
        
        # Merakit HTML Per Poster
        all_posters_html += f"""
        <div class="slide-wrapper">
            <div id="{poster_id}" class="poster-container">
                <div class="slide-badge">SLIDE {slide_num}</div>
                <h1 class="header-title">{slide.get("infographic_title", f"Slide {slide_num}")}</h1>
                {img_element}
                <div class="cards-wrapper">
                    {items_html}
                </div>
                <div class="footer-note">STUDIO KREATIF PRO • KTB UKM JATIM</div>
            </div>
            <button id="{btn_id}" class="download-btn" onclick="downloadPoster('{poster_id}', '{btn_id}', {slide_num})">
                <span>⬇️</span> Download Slide {slide_num} Kualitas Tinggi (PNG)
            </button>
        </div>
        """

    # Membungkus seluruh poster ke dalam satu dokumen HTML
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Nunito:wght@400;600;700&display=swap');
            
            body {{
                margin: 0;
                padding: 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
                background-color: #f0f2f5;
            }}
            
            .slide-wrapper {{
                margin-bottom: 60px;
                width: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            
            /* Kontainer Poster */
            .poster-container {{
                background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
                width: 100%;
                max-width: {max_width};
                padding: 40px;
                border-radius: 25px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                font-family: 'Nunito', sans-serif;
                position: relative;
                box-sizing: border-box;
            }}
            
            .slide-badge {{
                position: absolute;
                top: -15px;
                left: -15px;
                background-color: #ff5722;
                color: white;
                padding: 8px 20px;
                border-radius: 20px;
                font-family: 'Montserrat', sans-serif;
                font-size: 14px;
                font-weight: bold;
                box-shadow: 0 4px 10px rgba(255,87,34,0.3);
            }}
            
            .header-title {{
                font-family: 'Montserrat', sans-serif;
                font-size: 32px;
                color: #006064;
                text-align: center;
                margin-top: 15px;
                margin-bottom: 30px;
                line-height: 1.3;
                text-transform: uppercase;
                text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
            }}
            
            .hero-image {{
                width: 100%;
                max-width: 450px;
                height: auto;
                border-radius: 20px;
                margin: 0 auto 30px auto;
                display: block;
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                border: 4px solid white;
            }}
            
            .cards-wrapper {{
                display: flex;
                flex-direction: column;
                gap: 15px;
            }}
            
            .card {{
                background-color: white;
                border-radius: 15px;
                padding: 20px;
                display: flex;
                align-items: center;
                box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                border-left: 8px solid #00acc1;
            }}
            
            .card-icon {{
                font-size: 40px;
                margin-right: 20px;
                min-width: 50px;
                text-align: center;
            }}
            
            .card-title {{
                font-family: 'Montserrat', sans-serif;
                font-size: 18px;
                color: #00838f;
                margin-bottom: 6px;
                font-weight: 700;
            }}
            
            .card-desc {{
                font-size: 15px;
                color: #455a64;
                line-height: 1.5;
            }}
            
            /* Tombol Download */
            .download-btn {{
                margin-top: 25px;
                background-color: #ff5722;
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 18px;
                font-family: 'Montserrat', sans-serif;
                border-radius: 30px;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(255, 87, 34, 0.4);
                transition: background 0.3s;
                width: 100%;
                max-width: {max_width};
            }}
            .download-btn:hover {{ background-color: #e64a19; }}
            
            .footer-note {{
                text-align: center;
                margin-top: 30px;
                color: #00838f;
                font-weight: 600;
                font-size: 14px;
                letter-spacing: 1px;
            }}
        </style>
    </head>
    <body>

        {all_posters_html}

        <script>
            function downloadPoster(posterId, btnId, slideNum) {{
                const poster = document.getElementById(posterId);
                const btn = document.getElementById(btnId);
                
                // Matikan sementara lencana Slide saat dicapture agar hasil download lebih bersih
                const badge = poster.querySelector('.slide-badge');
                if(badge) badge.style.display = 'none';
                
                btn.innerHTML = '⏳ Sedang Memproses...';
                btn.style.backgroundColor = '#757575';
                
                html2canvas(poster, {{ scale: 2, useCORS: true }}).then(canvas => {{
                    if(badge) badge.style.display = 'block'; // Kembalikan lencana
                    
                    btn.innerHTML = '<span>⬇️</span> Download Slide ' + slideNum + ' Kualitas Tinggi (PNG)';
                    btn.style.backgroundColor = '#ff5722';
                    
                    let link = document.createElement('a');
                    link.download = 'Infografis_Slide_' + slideNum + '.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                }}).catch(err => {{
                    if(badge) badge.style.display = 'block';
                    console.error("Gagal mendownload:", err);
                    alert("Terjadi kesalahan saat memproses gambar.");
                    btn.innerHTML = '<span>⬇️</span> Download Slide ' + slideNum + ' Kualitas Tinggi (PNG)';
                    btn.style.backgroundColor = '#ff5722';
                }});
            }}
        </script>
    </body>
    </html>
    """
    return html_template

# ==========================================
# 🚀 MAIN APP RUNNER
# ==========================================
def run():
    st.title("🎨 Ruang 3: Studio Cetak (Visual & Infografis)")
    st.info("💡 **Ditenagai Groq Llama 3.3 70B & Hugging Face:** Sistem kini mendukung pembuatan **Multi-Slide Carousel** (lebih dari 1 gambar) yang menyatukan teks dan ilustrasi relevan!")

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

    st.markdown("### 🎛️ Pengaturan Sistem & Desain")
    
    col1, col2 = st.columns(2)
    with col1:
        opsi_dimensi = st.selectbox(
            "1. Ukuran Poster / Platform:", 
            [
                "1080 x 1920 px (Vertical / IG Story / TikTok) - DIREKOMENDASIKAN",
                "1080 x 1080 px (Square / IG Feed)"
            ], index=0
        )
        
    with col2:
        # Pilihan langsung untuk mempermudah, opsi custom ditaruh di bawah
        opsi_slide = st.selectbox(
            "2. Mode Format Poster:", 
            [
                "1 Slide (1 Poster Panjang)", 
                "2 Slide (Carousel Pendek)",
                "3 Slide (Carousel Menengah)",
                "5 Slide (Carousel Panjang)",
                "Isi sendiri..."
            ], index=0
        )
        
        jawaban_slide = opsi_slide
        if opsi_slide == "Isi sendiri...":
            jawaban_slide = st.text_input("Instruksi spesifik (contoh: 4 slide):", placeholder="Contoh: 4 slide")

    user_input = st.text_area("Draft Naskah Dasar:", value=naskah_final, height=150)

    if st.button("✨ Hasilkan Infografis Cerdas", use_container_width=True, type="primary"):
        if not jawaban_slide.strip():
            st.warning("⚠️ Mohon lengkapi Mode Format terlebih dahulu!")
            return
            
        if not user_input.strip():
            st.warning("⚠️ Draft naskah tidak boleh kosong!")
            return
            
        with st.spinner("🤖 Groq Llama 3.3 sedang merangkum naskah menjadi Slide presentasi..."):
            try:
                # 1. Analisis Naskah dengan Groq (JSON Setup)
                structured_data = generate_structured_text_groq(user_input, jawaban_slide)
                slides = structured_data.get("slides", [])
                total_slides = len(slides)
                
                b64_images = []
                
                # 2. Looping Gambar Ilustrasi untuk SETIAP Slide
                for idx, slide in enumerate(slides):
                    slide_num = slide.get("slide_number", idx + 1)
                    img_prompt = slide.get("image_prompt", "Professional vector infographic illustration")
                    
                    with st.spinner(f"🎨 AI Pelukis FLUX.1 sedang menggambar ilustrasi untuk Slide {slide_num} dari {total_slides} (Harap tunggu)..."):
                        b64_img = generate_image_with_retry(img_prompt, opsi_dimensi)
                        b64_images.append(b64_img)
                
                with st.spinner("📐 Layout Web Engine sedang menata letak elemen HTML..."):
                    # 3. Merakit HTML/CSS Kualitas Tinggi
                    final_html = render_beautiful_html_poster(structured_data, b64_images, opsi_dimensi)
                    
                    st.success(f"🎉 {total_slides} Slide Infografis berhasil dirender dengan desain memukau!")
                    
                    # 4. Tampilkan HTML yang interaktif langsung ke dalam iframe Streamlit
                    # Kita set height dinamis berdasarkan jumlah slide agar bisa di-scroll dengan lega
                    iframe_height = total_slides * 1000 + 200
                    st.components.v1.html(final_html, height=iframe_height, scrolling=True)
                    
                    with st.expander("🛠️ Lihat Data Struktur Poin (JSON)"):
                        st.json(structured_data)

            except Exception as e:
                st.error(f"❌ Terjadi kesalahan pada proses generasi: {str(e)}")

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
