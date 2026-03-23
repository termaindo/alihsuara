import streamlit as st
import re
import os
import json
import base64
import io
import random
import google.generativeai as genai
import time
from PIL import Image

# ==========================================
# 🧩 1. GOOGLE GEMINI (2.5 FLASH) JSON WRAPPER
# ==========================================
def generate_structured_text_gemini(prompt_text, opsi_slide, detail_topik, opsi_gaya):
    """Menghasilkan struktur JSON yang rapi untuk diolah ke HTML."""
    if "Realistik" in opsi_gaya:
        style_instruction = f"ultra-realistic photography, 8k resolution, cinematic lighting, conceptual aesthetic, completely textless, [KIASAN VISUAL UNTUK '{detail_topik}']"
    else:
        style_instruction = f"professional premium 2d vector illustration, modern colors, completely textless, [KIASAN VISUAL UNTUK '{detail_topik}']"

    slide_rule = ""
    if "1 Slide" in opsi_slide:
        slide_rule = "\n[ATURAN KHUSUS 1 SLIDE]: Rangkum menjadi SANGAT SINGKAT (Maks 4 poin utama)."

    system_prompt = f"""Kamu adalah Ahli Desain Visual Profesional.
TOPIK: {detail_topik}

Format output HARUS JSON valid dengan struktur:
{{
  "slides": [
    {{
      "slide_number": 1,
      "infographic_title": "Judul (Maks 6 Kata)",
      "image_prompt": "{style_instruction}",
      "items": [
        {{
          "icon_emoji": "💡",
          "title": "Sub Judul",
          "content": "Penjelasan maksimal 2 baris."
        }}
      ]
    }}
  ]
}}
ATURAN MUTLAK: 
1. Buat jumlah slide: {opsi_slide}.
2. image_prompt WAJIB berbahasa Inggris. {slide_rule}
3. DILARANG menyuruh AI menggambar teks/huruf pada image_prompt.
4. Gunakan MURNI BENDA MATI ESTETIK yang fokus HANYA pada KEMASAN FISIK produk."""

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    try:
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=system_prompt,
            generation_config={"response_mime_type": "application/json", "temperature": 0.4},
            safety_settings=safety_settings
        )
        response = model.generate_content(f"Teks Dasar:\n{prompt_text}")
        return json.loads(response.text)
    except Exception as e:
        err_msg = str(e).lower()
        if "429" in err_msg or "quota" in err_msg:
            raise Exception(f"QUOTA_TEKS_HABIS|{str(e)}")
        raise Exception("FORMAT_JSON_RUSAK|Gagal memproses struktur visual.")

# ==========================================
# 🧩 2. WEB-BASED LAYOUT ENGINE (HTML/CSS MULTI-TEMA)
# ==========================================
def render_beautiful_html_poster(data_json, b64_images, opsi_dimensi, tema="minimalist"):
    w_px, h_px = 1080, 1920
    if "Square" in opsi_dimensi:
        w_px, h_px = 1080, 1080
    elif "Landscape" in opsi_dimensi:
        w_px, h_px = 1920, 1080

    slides = data_json.get("slides", [])
    all_posters_html = ""
    
    if tema == "elegant_dark":
        css_colors = """
            .poster-container { background-color: #0f172a; }
            .slide-indicator { color: #d4af37; border-bottom: 2px solid #d4af37; padding-bottom: 5px; display: inline-block; }
            .main-title { color: #f8fafc; }
            .item-title { color: #f8fafc; }
            .item-desc { color: #cbd5e1; }
            .stamp-footer { background-color: #020617; border-top: 2px solid #d4af37; }
            .stamp-line { color: #d4af37; }
            .stamp-spacer { color: #334155; }
        """
    elif tema == "modern_gradient":
        css_colors = """
            .poster-container { background: linear-gradient(135deg, #f0fdfa 0%, #e0f2fe 100%); }
            .slide-indicator { color: #0284c7; background-color: #bae6fd; padding: 6px 16px; border-radius: 20px; display: inline-block; }
            .main-title { color: #0369a1; }
            .minimalist-item { background: rgba(255, 255, 255, 0.7); padding: 25px; border-radius: 20px; box-shadow: 0 8px 20px rgba(0,0,0,0.04); border: 1px solid #ffffff; }
            .item-icon { background: #ffffff; padding: 15px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.02); margin-top: -10px; }
            .item-title { color: #0f172a; }
            .item-desc { color: #334155; }
            .stamp-footer { background-color: #0284c7; }
            .stamp-line { color: #ffffff; }
            .stamp-spacer { color: #7dd3fc; }
        """
    elif tema == "earthy_nature":
        css_colors = """
            .poster-container { background-color: #fdf8f5; }
            .slide-indicator { color: #15803d; background-color: #dcfce7; padding: 6px 20px; border-radius: 30px; display: inline-block; font-weight: 800; border: 1px solid #bbf7d0; }
            .main-title { color: #14532d; }
            .minimalist-item { background: #ffffff; padding: 25px; border-radius: 20px; border-left: 6px solid #16a34a; box-shadow: 0 10px 25px rgba(20, 83, 45, 0.05); }
            .item-icon { background: #f0fdf4; padding: 15px; border-radius: 50%; color: #16a34a; margin-top: -5px; }
            .item-title { color: #166534; }
            .item-desc { color: #4b5563; }
            .stamp-footer { background-color: #14532d; }
            .stamp-line { color: #fcfdf8; }
            .stamp-spacer { color: #86efac; }
        """
    elif tema == "vibrant_pop":
        css_colors = """
            .poster-container { background-color: #fef08a; border: 3px solid #0f172a; border-radius: 24px; }
            .slide-indicator { color: #ffffff; background-color: #ec4899; padding: 6px 20px; border-radius: 25px; display: inline-block; border: 2px solid #0f172a; font-weight: 800; transform: rotate(-2deg); box-shadow: 3px 3px 0px #0f172a; }
            .main-title { color: #0f172a; text-transform: uppercase; text-shadow: 3px 3px 0px #f472b6; }
            .minimalist-item { background: #ffffff; padding: 25px; border-radius: 20px; border: 3px solid #0f172a; box-shadow: 6px 6px 0px #0f172a; }
            .item-icon { font-size: 45px; margin-top: -5px; }
            .item-title { color: #0f172a; font-weight: 900; }
            .item-desc { color: #334155; font-weight: 700; }
            .stamp-footer { background-color: #ec4899; border-top: 3px solid #0f172a; }
            .stamp-line { color: #ffffff; font-weight: 800; }
            .stamp-spacer { color: #fbcfe8; }
        """
    else: # minimalist (default)
        css_colors = """
            .poster-container { background-color: #ffffff; }
            .slide-indicator { color: #64748b; }
            .main-title { color: #0f172a; }
            .item-title { color: #1e293b; }
            .item-desc { color: #475569; }
            .stamp-footer { background-color: #0f172a; }
            .stamp-line { color: #ffffff; }
            .stamp-spacer { color: #475569; }
        """

    for idx, slide in enumerate(slides):
        slide_num = slide.get("slide_number", idx + 1)
        b64_img = b64_images[idx] if idx < len(b64_images) else ""
        
        img_element = f'<img src="{b64_img}" class="hero-image" alt="Visual">' if b64_img else ""
            
        items_html = ""
        for item in slide.get("items", []):
            icon = item.get("icon_emoji", "✨")
            title = item.get("title", "Judul Poin")
            content = item.get("content", "Deskripsi poin.")
            items_html += f"""
            <div class="minimalist-item">
                <div class="item-icon">{icon}</div>
                <div class="item-text">
                    <div class="item-title">{title}</div>
                    <div class="item-desc">{content}</div>
                </div>
            </div>
            """
            
        poster_id = f"poster-container-{slide_num}"
        btn_id = f"btn-{slide_num}"
        
        if w_px > h_px:
            layout_html = f"""
            <div class="content-row">
                <div class="image-col">{img_element}</div>
                <div class="text-col">{items_html}</div>
            </div>
            """
        else:
            layout_html = f"""
            {img_element}
            <div class="text-col-vertical">{items_html}</div>
            """
        
        all_posters_html += f"""
        <div class="slide-wrapper">
            <div id="{poster_id}" class="poster-container">
                <div class="poster-body">
                    <div class="slide-indicator">SLIDE {slide_num}</div>
                    <h1 class="main-title">{slide.get("infographic_title", f"Slide {slide_num}")}</h1>
                    {layout_html}
                </div>
                
                <div class="stamp-footer">
                    <div class="stamp-line">Studio Kreatif Pro - KTB UKM JATIM</div>
                    <div class="stamp-line">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="stamp-icon"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg>
                        @ktbukm.jatim
                        <span class="stamp-spacer">&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;</span>
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="stamp-icon"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
                        https://ktbukm-jatim.store
                    </div>
                </div>
            </div>
            <button id="{btn_id}" class="download-btn" onclick="downloadPoster('{poster_id}', '{btn_id}', {slide_num})">
                <span>⬇️</span> Download Slide {slide_num} (Kualitas Tinggi)
            </button>
        </div>
        """

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800;900&display=swap" rel="stylesheet">
        <style>
            body {{ margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; background-color: #f4f6f8; font-family: 'Plus Jakarta Sans', sans-serif; }}
            .slide-wrapper {{ margin-bottom: 50px; display: flex; flex-direction: column; align-items: center; width: 100%; }}
            .poster-container {{ width: {w_px}px; min-height: {h_px}px; display: flex; flex-direction: column; box-shadow: 0 20px 40px rgba(0,0,0,0.08); overflow: hidden; position: relative; }}
            .poster-body {{ padding: 60px; flex: 1; display: flex; flex-direction: column; }}
            .slide-indicator {{ font-weight: 800; font-size: 20px; letter-spacing: 2px; margin-bottom: 15px; text-transform: uppercase; }}
            .main-title {{ font-size: 54px; font-weight: 800; line-height: 1.2; margin: 0 0 40px 0; letter-spacing: -1px; }}
            .content-row {{ display: flex; gap: 60px; align-items: center; flex: 1; }}
            .image-col {{ flex: 1; }}
            .text-col {{ flex: 1.2; display: flex; flex-direction: column; gap: 30px; }}
            .text-col-vertical {{ display: flex; flex-direction: column; gap: 30px; margin-top: 20px; }}
            .hero-image {{ width: 100%; height: auto; max-height: 800px; object-fit: contain; border-radius: 24px; filter: drop-shadow(0px 25px 35px rgba(0,0,0,0.25)); }}
            .minimalist-item {{ display: flex; align-items: flex-start; gap: 20px; }}
            .item-icon {{ font-size: 45px; line-height: 1; }}
            .item-title {{ font-size: 28px; font-weight: 800; margin-bottom: 8px; }}
            .item-desc {{ font-size: 22px; font-weight: 500; line-height: 1.6; }}
            .stamp-footer {{ width: 100%; padding: 30px 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; margin-top: auto; }}
            .stamp-line {{ font-size: 24px; font-weight: 700; display: flex; align-items: center; justify-content: center; }}
            .stamp-icon {{ margin-right: 8px; }}
            .download-btn {{ margin-top: 25px; background-color: #0f172a; color: #ffffff; border: none; padding: 18px 35px; font-size: 18px; font-weight: 700; font-family: 'Plus Jakarta Sans', sans-serif; border-radius: 50px; cursor: pointer; transition: 0.2s; box-shadow: 0 10px 20px rgba(0,0,0,0.1); }}
            .download-btn:hover {{ background-color: #334155; transform: translateY(-2px); }}
            {css_colors}
        </style>
    </head>
    <body>
        {all_posters_html}
        <script>
            function downloadPoster(posterId, btnId, slideNum) {{
                const poster = document.getElementById(posterId);
                const btn = document.getElementById(btnId);
                btn.innerHTML = '⏳ Sedang Memproses...';
                
                html2canvas(poster, {{ scale: 1.5, useCORS: true, backgroundColor: "#ffffff" }}).then(canvas => {{
                    btn.innerHTML = '<span>⬇️</span> Download Slide ' + slideNum + ' (Kualitas Tinggi)';
                    let link = document.createElement('a');
                    link.download = 'Infografis_Kreatif_' + slideNum + '.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                }}).catch(err => {{
                    btn.innerHTML = '<span>⬇️</span> Download Slide ' + slideNum;
                }});
            }}
        </script>
    </body>
    </html>
    """
    return html_template

# ==========================================
# 🧩 3. GENERATOR PROMPT MANUAL (COPTER UNTUK GEMINI PRIBADI)
# ==========================================
def create_manual_prompt(structured_data, topik, opsi_slide):
    """Menghasilkan prompt cerdas untuk di-copy paste ke Gemini oleh user gaptek."""
    slides = structured_data.get("slides", [])
    jumlah_slide = len(slides)
    
    prompt = "🌟 **LANGKAH 1: Berikan instruksi ini ke Gemini Anda:**\n\n```text\n"
    prompt += f"Halo Gemini, saya ingin membuat infografis tentang {topik}.\nSaya punya materi strukturnya. Tolong pahami dulu teks di bawah ini, tapi JANGAN buatkan gambarnya dulu. Cukup jawab 'Paham' jika kamu sudah membacanya.\n\n"
    
    for slide in slides:
        prompt += f"[SLIDE {slide.get('slide_number', '')}]\nJudul Utama: {slide.get('infographic_title', '')}\n"
        for item in slide.get("items", []):
            prompt += f"• {item.get('title', '')}: {item.get('content', '')}\n"
        prompt += "\nWajib ada teks stempel persis 2 baris ini di bagian paling bawah desain:\nBaris 1: Studio Kreatif Pro - KTB UKM Jatim\nBaris 2: [Ikon IG] @ktbukm.jatim   [Ikon Website] [https://ktbukm-jatim.store](https://ktbukm-jatim.store)\n------------------------\n"
    prompt += "
