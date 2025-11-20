import streamlit as st
import json
import random
from gtts import gTTS
import io
import base64
import streamlit.components.v1 as components

# Sayfa Ayarları
st.set_page_config(page_title="Fransızca Ustası", layout="wide")

# --- 1. VERİ YÜKLEME ---
@st.cache_data
def load_data():
    try:
        with open('adverbs.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("adverbs.json dosyası bulunamadı.")
        return []

all_data = load_data()

# --- ÖZEL SESLİ BUTON ---
def clickable_audio_word(text, label_text=None, key_suffix=""):
    try:
        tts = gTTS(text=text, lang='fr')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        b64 = base64.b64encode(fp.getvalue()).decode()
        display_text = label_text if label_text else text
        unique_id = f"audio_{key_suffix}_{text.replace(' ', '_')}"
        
        html_code = f"""
            <html>
            <body>
                <audio id="{unique_id}" style="display:none;" preload="auto">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                <button 
                    onclick="var audio = document.getElementById('{unique_id}'); audio.currentTime=0; audio.play();"
                    style="
                        background-color: #ffffff;
                        border: 1px solid #d1d5db;
                        border-radius: 8px;
                        padding: 12px 20px;
                        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
                        font-size: 18px;
                        font-weight: 600;
                        color: #1f2937;
                        cursor: pointer;
                        width: 100%;
                        display: flex;
                        align-items: center;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                        -webkit-appearance: none;
                        margin-bottom: 8px;
                    ">
                    <span style="margin-right: 12px; font-size: 22px;">🔊</span> {display_text}
                </button>
            </body>
            </html>
        """
        components.html(html_code, height=75)
    except Exception:
        st.error("Ses yüklenemedi.")

# --- OTURUM YÖNETİMİ ---
if 'learned_words' not in st.session_state: st.session_state.learned_words = set()
if 'batch' not in st.session_state:
    if len(all_data) >= 20: st.session_state.batch = random.sample(all_data, 20)
    else: st.session_state.batch = all_data 
if 'mode' not in st.session_state: st.session_state.mode = 'study' 
if 'q_index' not in st.session_state: st.session_state.q_index = 0
if 'score' not in st.session_state: st.session_state.score = 0
if 'current_options' not in st.session_state: st.session_state.current_options = []
if 'answer_state' not in st.session_state: st.session_state.answer_state = None

# --- FONKSİYONLAR ---
def start_quiz():
    st.session_state.mode = 'quiz'
    st.session_state.q_index = 0
    st.session_state.score = 0
    st.session_state.answer_state = None
    generate_options()

def new_batch():
    if len(all_data) >= 20: st.session_state.batch = random.sample(all_data, 20)
    st.session_state.mode = 'study'
    st.session_state.q_index = 0
    st.session_state.score = 0
    st.session_state.answer_state = None

def generate_options():
    current_word = st.session_state.batch[st.session_state.q_index]
    correct_answer = current_word['tr']
    distractors = []
    while len(distractors) < 3:
        random_word = random.choice(all_data)
        if random_word['tr'] != correct_answer and random_word['tr'] not in distractors:
            distractors.append(random_word['tr'])
    options = distractors + [correct_answer]
    random.shuffle(options)
    st.session_state.current_options = options

def submit_answer(selected_option):
    current_word = st.session_state.batch[st.session_state.q_index]
    if selected_option == current_word['tr']:
        st.session_state.score += 1
        st.session_state.learned_words.add(current_word['fr'])
        st.session_state.answer_state = 'correct'
    else:
        st.session_state.answer_state = 'wrong'

def next_question():
    st.session_state.answer_state = None
    if st.session_state.q_index < len(st.session_state.batch) - 1:
        st.session_state.q_index += 1
        generate_options()
    else:
        st.session_state.mode = 'result'

# --- YAN MENÜ ---
with st.sidebar:
    st.header("📊 Gelişim Raporu")
    total_words = len(all_data)
    learned_count = len(st.session_state.learned_words)
    
    if total_words > 0: progress_ratio = learned_count / total_words
    else: progress_ratio = 0
        
    st.progress(progress_ratio)
    st.write(f"**{learned_count} / {total_words}** Kelime Öğrenildi")
    
    st.markdown("---")
    st.subheader("🏆 Seviyen")
    if learned_count < 50: st.info("👶 Başlangıç")
    elif learned_count < 200: st.success("🎓 Çırak")
    elif learned_count < 500: st.warning("🔥 Usta")
    else: st.error("👑 Efsane")

# --- ANA SAYFA ---
st.title("🇫🇷 Fransızca Zarf Ustası")

# MOD 1: ÇALIŞMA
if st.session_state.mode == 'study':
    st.info("🔊 Kelimelere tıkla, dinle ve ezberle.")
    
    col1, col2 = st.columns(2)
    for i, word in enumerate(st.session_state.batch):
        with (col1 if i < 10 else col2):
            clickable_audio_word(word['fr'], key_suffix=f"study_{i}")
            
            st.write(f"🇹🇷 **{word['tr']}**")
            
            # --- İŞTE DEĞİŞİKLİK BURADA ---
            # Yeşil Yuvarlak (🟢) ve Kırmızı Yuvarlak (🔴) kullandık.
            st.write(f"🟢 **Eş:** {word.get('syn', '-')} | 🔴 **Zıt:** {word.get('ant', '-')}")
            
            st.divider()

    if st.button("🧠 Hazırım, Testi Başlat", type="primary", use_container_width=True):
        start_quiz()
        st.rerun()

# MOD 2: TEST
elif st.session_state.mode == 'quiz':
    current_word = st.session_state.batch[st.session_state.q_index]
    batch_progress = (st.session_state.q_index + 1) / len(st.session_state.batch)
    st.progress(batch_progress, text=f"Soru {st.session_state.q_index + 1} / 20")
    
    st.header("Bu kelimenin anlamı nedir?")
    clickable_audio_word(current_word['fr'], key_suffix=f"quiz_{st.session_state.q_index}")
    st.write("")

    if st.session_state.answer_state is None:
        opts = st.session_state.current_options
        c1, c2 = st.columns(2)
        with c1:
            if st.button(opts[0], use_container_width=True):
                submit_answer(opts[0])
                st.rerun()
            if st.button(opts[1], use_container_width=True):
                submit_answer(opts[1])
                st.rerun()
        with c2:
            if st.button(opts[2], use_container_width=True):
                submit_answer(opts[2])
                st.rerun()
            if st.button(opts[3], use_container_width=True):
                submit_answer(opts[3])
                st.rerun()

    else:
        if st.session_state.answer_state == 'correct':
            st.success("✅ **Tebrikler! Doğru Bildin.**")
        else:
            st.error("❌ **Yanlış!**")
            
            # Yanlış yapınca da detayları yeşil/kırmızı ile gösterelim
            st.info(f"Doğru Cevap: **{current_word['tr']}**")
            st.write(f"🟢 **Eş:** {current_word.get('syn', '-')} | 🔴 **Zıt:** {current_word.get('ant', '-')}")
        
        if st.button("➡️ Sıradaki Soru", type="primary", use_container_width=True):
            next_question()
            st.rerun()

# MOD 3: SONUÇ
elif st.session_state.mode == 'result':
    score = st.session_state.score
    total = len(st.session_state.batch)
    st.balloons()
    
    st.success(f"🏁 Tur Tamamlandı! Skorun: {score} / {total}")
    st.info("Doğru bildiğin kelimeler sol taraftaki genel ilerlemene eklendi!")
    
    if st.button("➡️ Yeni 20 Kelime Getir", type="primary", use_container_width=True):
        new_batch()
        st.rerun()
