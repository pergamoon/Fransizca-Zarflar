import streamlit as st
import json
import random

st.set_page_config(page_title="20 Kelime Challenge", layout="centered")

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

# --- 2. OTURUM BAŞLATMA (STATE) ---
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

# --- FONKSİYONLAR ---

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
        st.toast(f"✅ Doğru! ({current_word['fr']} = {current_word['tr']})", icon="🎉")
    else:
        st.toast(f"❌ Yanlış! Doğrusu: {current_word['tr']}", icon="⚠️")

    if st.session_state.q_index < len(st.session_state.batch) - 1:
        st.session_state.q_index += 1
        generate_options()
    else:
        st.session_state.mode = 'result'

# --- ARAYÜZ ---

st.title("🇫🇷 20 Kelime Maratonu")

# --- MOD 1: ÇALIŞMA EKRANI ---
if st.session_state.mode == 'study':
    st.info("Lütfen aşağıdaki 20 kelimeyi incele. Hazır olduğunda teste başla!")
    
    col1, col2 = st.columns(2)
    for i, word in enumerate(st.session_state.batch):
        with (col1 if i < 10 else col2):
            # Kelime ve Anlamı
            st.markdown(f"##### {i+1}. {word['fr']}") 
            st.markdown(f"🇹🇷 **{word['tr']}**")
            
            # !!! DÜZELTİLEN KISIM BURASI !!!
            # Hem Eş (syn) hem Zıt (ant) anlamlıları gösteriyoruz
            synonym = word.get('syn', '-')
            antonym = word.get('ant', '-')
            
            st.caption(f"🔄 Eş: {synonym}")
            st.caption(f"↔️ Zıt: {antonym}")
            
            st.markdown("---")

    if st.button("🧠 Ezberledim, Teste Başla", type="primary", use_container_width=True):
        start_quiz()
        st.rerun()

# --- MOD 2: TEST EKRANI ---
elif st.session_state.mode == 'quiz':
    current_word = st.session_state.batch[st.session_state.q_index]
    progress = (st.session_state.q_index + 1) / len(st.session_state.batch)
    
    st.progress(progress, text=f"Soru {st.session_state.q_index + 1} / 20")
    
    st.markdown(f"""
    <div style="background-color:#f0f2f6; padding:30px; border-radius:15px; text-align:center; margin-bottom:20px;">
        <h1 style="color:#2c3e50; margin:0;">{current_word['fr']}</h1>
        <p style="color:#7f8c8d;">Bu kelimenin Türkçe karşılığı nedir?</p>
    </div>
    """, unsafe_allow_html=True)

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

# --- MOD 3: SONUÇ EKRANI ---
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
    
    if score == total:
        st.success("Harika! Tam puan. 🏆")
    elif score >= 15:
        st.info("Gayet iyi! 👏")
    else:
        st.warning("Tekrar yapman faydalı olabilir. 💪")

    if st.button("🔄 Yeni 20 Kelime Getir", type="primary", use_container_width=True):
        new_batch()
        st.rerun()