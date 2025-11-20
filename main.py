import streamlit as st
import json
import random
from gtts import gTTS
import io
import base64
import streamlit.components.v1 as components

st.set_page_config(page_title="Sesli Kartlar", layout="centered")

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

# --- ÖZEL SESLİ BUTON FONKSİYONU ---
def clickable_audio_word(text, label_text=None, key_suffix=""):
    """
    Bu fonksiyon gizli bir ses dosyası oluşturur ve 
    üzerine tıklandığında bu sesi çalan bir HTML butonu basar.
    """
    try:
        # 1. Sesi hafızada oluştur
        tts = gTTS(text=text, lang='fr')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        
        # 2. Sesi Base64 formatına çevir (HTML içine gömmek için)
        b64 = base64.b64encode(fp.getvalue()).decode()
        
        # Görünecek metin (Eğer özel bir etiket yoksa kelimenin kendisi)
        display_text = label_text if label_text else text
        
        # 3. HTML/CSS/JS Bloğu
        # Benzersiz ID oluşturuyoruz ki kelimeler karışmasın
        unique_id = f"audio_{key_suffix}_{text.replace(' ', '_')}"
        
        html_code = f"""
            <html>
            <head>
            <style>
                .audio-btn {{
                    background-color: #ffffff;
                    border: 1px solid #d1d5db;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-family: sans-serif;
                    font-size: 18px;
                    font-weight: bold;
                    color: #1f2937;
                    cursor: pointer;
                    width: 100%;
                    transition: all 0.2s;
                    text-align: left;
                    display: flex;
                    align-items: center;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                }}
                .audio-btn:hover {{
                    background-color: #f3f4f6;
                    border-color: #4F46E5;
                    color: #4F46E5;
                }}
                .icon {{
                    margin-right: 10px;
                    font-size: 20px;
                }}
            </style>
            </head>
            <body>
                <audio id="{unique_id}" src="data:audio/mp3;base64,{b64}"></audio>
                
                <button class="audio-btn" onclick="document.getElementById('{unique_id}').play()">
                    <span class="icon">🔊</span> {display_text}
                </button>
            </body>
            </html>
        """
        
        # Streamlit içinde HTML'i göster
        components.html(html_code, height=60)
        
    except Exception as e:
        st.error("Ses oluşturulamadı.")

# --- OTURUM YÖNETİMİ ---
if 'batch' not in st.session_state:
    if len(all_data) >= 20:
        st.session_state.batch = random.sample(all_data, 20)
    else:
        st.session_state.batch = all_data 

if 'mode' not in st.session_state:
    st.session_state.mode = 'study' 

if 'q_index' not in st.session_state:
    st.session_state.q_index = 0

if 'score' not in st.session_state:
    st.session_state.score = 0

if 'current_options' not in st.session_state:
    st.session_state.current_options = []

# --- DİĞER FONKSİYONLAR ---
def start_quiz():
    st.session_state.mode = 'quiz'
    st.session_state.q_index = 0
    st.session_state.score = 0
    generate_options()

def new_batch():
    if len(all_data) >= 20:
        st.session_state.batch = random.sample(all_data, 20)
    st.session_state.mode = 'study'
    st.session_state.q_index = 0
    st.session_state.score = 0

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

def check_answer(selected_option):
    current_word = st.session_state.batch[st.session_state.q_index]
    if selected_option == current_word['tr']:
        st.session_state.score += 1
        st.toast(f"✅ Doğru! ({current_word['fr']})", icon="🎉")
    else:
        st.toast(f"❌ Yanlış! Doğrusu: {current_word['tr']}", icon="⚠️")

    if st.session_state.q_index < len(st.session_state.batch) - 1:
        st.session_state.q_index += 1
        generate_options()
    else:
        st.session_state.mode = 'result'

# --- ARAYÜZ ---

st.title("🇫🇷 İnteraktif Kelime Kartları")

# --- MOD 1: ÇALIŞMA ---
if st.session_state.mode == 'study':
    st.info("🔊 Kelimenin üzerine tıklayarak okunuşunu dinle!")
    
    col1, col2 = st.columns(2)
    for i, word in enumerate(st.session_state.batch):
        with (col1 if i < 10 else col2):
            
            # --- YENİ TIKLANABİLİR KELİME ---
            # Burada text_to_speech yerine yeni fonksiyonu çağırıyoruz
            clickable_audio_word(word['fr'], key_suffix=f"study_{i}")
            
            st.markdown(f"🇹🇷 **{word['tr']}**")
            syn = word.get('syn', '-')
            ant = word.get('ant', '-')
            st.caption(f"🔄 {syn} | ↔️ {ant}")
            st.divider()

    if st.button("🧠 Ezberledim, Teste Başla", type="primary", use_container_width=True):
        start_quiz()
        st.rerun()

# --- MOD 2: TEST ---
elif st.session_state.mode == 'quiz':
    current_word = st.session_state.batch[st.session_state.q_index]
    progress = (st.session_state.q_index + 1) / len(st.session_state.batch)
    
    st.progress(progress, text=f"Soru {st.session_state.q_index + 1} / 20")
    
    # Soru Kısmında Büyük Buton
    st.markdown("### Bu kelimenin anlamı ne?")
    
    # Burada da kelimeyi tıklanabilir yapıyoruz
    clickable_audio_word(current_word['fr'], key_suffix=f"quiz_{st.session_state.q_index}")
    
    st.write("") # Boşluk

    opts = st.session_state.current_options
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button(opts[0], use_container_width=True):
            check_answer(opts[0])
            st.rerun()
        if st.button(opts[1], use_container_width=True):
            check_answer(opts[1])
            st.rerun()
    with c2:
        if st.button(opts[2], use_container_width=True):
            check_answer(opts[2])
            st.rerun()
        if st.button(opts[3], use_container_width=True):
            check_answer(opts[3])
            st.rerun()

# --- MOD 3: SONUÇ ---
elif st.session_state.mode == 'result':
    score = st.session_state.score
    total = len(st.session_state.batch)
    
    st.balloons()
    st.markdown(f"""
    <div style="text-align:center; padding: 50px;">
        <h1>🏁 Test Bitti!</h1>
        <h2>Skorun: <span style="color:#2ecc71">{score}</span> / {total}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Yeni 20 Kelime Getir", type="primary", use_container_width=True):
        new_batch()
        st.rerun()