import streamlit as st
import json, time, os, random, base64

# --- PAGE CONFIG ---
st.set_page_config(page_title="CATG Quiz Pro", layout="centered")

# --- PERFORMANCE OPTIMIZED DESIGN ---
st.markdown("""
    <style>
    /* Hiding the actual audio player but keeping it functional */
    .hidden-audio { display: none; }
    
    .stApp {
        background: linear-gradient(-45deg, #1e5631, #2a7a45, #a8e063);
        background-size: 200% 200%;
        animation: activeGradient 15s ease infinite;
        background-attachment: fixed;
    }
    @keyframes activeGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .question-box {
        background: rgba(255, 255, 255, 0.95);
        padding: 40px;
        border-radius: 30px;
        border-left: 12px solid #1e5631;
        box-shadow: 0 15px 30px rgba(0,0,0,0.1);
        margin-bottom: 30px;
        color: #1e5631;
        position: relative;
        z-index: 1;
    }
    .stButton>button { 
        width: 100%; border-radius: 20px; height: 3.5em; 
        font-size: 18px; font-weight: 800; 
        background: white; color: #1e5631; border: 2px solid #1e5631; 
        transition: all 0.2s ease;
    }
    .stButton>button:hover { background-color: #1e5631 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- AUDIO LOGIC ---
if 'mute' not in st.session_state: st.session_state.mute = False
if 'volume' not in st.session_state: st.session_state.volume = 50

def play_sound(file_path):
    if not st.session_state.mute and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            vol = st.session_state.volume / 100
            md = f"""
                <audio autoplay="true" class="hidden-audio">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                <script>
                    var audio = document.querySelector('audio');
                    audio.volume = {vol};
                </script>
                </audio>
                """
            st.markdown(md, unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🔊 Sound Settings")
    st.session_state.mute = st.checkbox("Mute All Sounds", value=st.session_state.mute)
    st.session_state.volume = st.slider("Volume", 0, 100, st.session_state.volume)

# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'welcome'
if 'leaderboard' not in st.session_state: st.session_state.leaderboard = []

# --- TIMER FRAGMENT ---
@st.fragment(run_every=1)
def timer_display():
    if st.session_state.page == 'quiz' and 'start_time' in st.session_state:
        elapsed = time.time() - st.session_state.start_time
        remaining = int(st.session_state.time_limit - elapsed)
        if remaining <= 0:
            finish_round()
            st.rerun()
        st.markdown(f"<div style='text-align:right; font-weight:900; color:white; font-size:24px;'>⏱️ {remaining}s</div>", unsafe_allow_html=True)

def finish_round():
    st.session_state.leaderboard.append({"name": st.session_state.current_player_name, "score": st.session_state.score})
    if st.session_state.game_mode == 'multi' and st.session_state.player_index < st.session_state.total_players - 1:
        st.session_state.player_index += 1
        st.session_state.page = 'next_turn'
    else:
        st.session_state.page = 'summary'

# --- APP PAGES ---

if st.session_state.page == 'welcome':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists('logo.png'): st.image('logo.png', use_container_width=True)
        else: st.markdown("<h1 style='text-align:center; font-size: 80px;'>🏆</h1>", unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: white;'>WELCOME TO CATG QUIZ</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #f0f0f0;'>Win to get to leadership board</p>", unsafe_allow_html=True)
    
    if st.button("GET STARTED"):
        st.session_state.page = 'mode_selection'
        st.rerun()

elif st.session_state.page == 'mode_selection':
    st.markdown("<h1 style='text-align:center; color:white;'>Choose Game Mode</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("👤 Single Player"):
        st.session_state.game_mode = 'single'
        st.session_state.page = 'settings'
        st.rerun()
    if c2.button("👥 Multiple Players"):
        st.session_state.game_mode = 'multi'
        st.session_state.page = 'settings'
        st.rerun()

elif st.session_state.page == 'settings':
    st.markdown("<h2 style='text-align:center; color:white;'>Game Settings</h2>", unsafe_allow_html=True)
    
    if st.session_state.game_mode == 'multi':
        total_p = st.number_input("How many players?", min_value=2, max_value=10, value=2)
        st.session_state.total_players = total_p
        st.session_state.player_names = []
        for i in range(total_p):
            name = st.text_input(f"Player {i+1} Name", key=f"pname_{i}")
            st.session_state.player_names.append(name if name else f"Player {i+1}")
    else:
        pname = st.text_input("Enter Your Name", value="Player 1")
        st.session_state.player_names = [pname]
        st.session_state.total_players = 1

    limit = st.selectbox("Time Limit (Seconds)", [30, 60, 120, 300])
    
    if st.button("START GAME"):
        st.session_state.update({
            'page': 'quiz' if st.session_state.game_mode == 'single' else 'next_turn',
            'player_index': 0,
            'time_limit': limit,
            'leaderboard': [],
            'current_player_name': st.session_state.player_names[0] # Fix for Single Player
        })
        if st.session_state.game_mode == 'single':
            # Initialize question data immediately for single player
            if os.path.exists('questions.json'):
                qs = json.load(open('questions.json'))
                idx = list(range(len(qs)))
                random.shuffle(idx)
                st.session_state.update({'questions_data': qs, 'shuffled_indices': idx, 'score': 0, 'current_step': 0, 'start_time': time.time()})
        st.rerun()

elif st.session_state.page == 'next_turn':
    name = st.session_state.player_names[st.session_state.player_index]
    st.markdown(f"<h1 style='text-align:center; color:white;'>Ready, {name}?</h1>", unsafe_allow_html=True)
    if st.button("START MY TURN"):
        if os.path.exists('questions.json'):
            qs = json.load(open('questions.json'))
            idx = list(range(len(qs)))
            random.shuffle(idx)
            st.session_state.update({
                'page': 'quiz', 'score': 0, 'current_step': 0, 
                'start_time': time.time(), 'questions_data': qs, 
                'shuffled_indices': idx, 'current_player_name': name
            })
            st.rerun()

elif st.session_state.page == 'quiz':
    timer_display()
    st.markdown(f"<p style='color:white;'>Playing: **{st.session_state.current_player_name}**</p>", unsafe_allow_html=True)
    q = st.session_state.questions_data[st.session_state.shuffled_indices[st.session_state.current_step]]
    st.markdown(f"<div class='question-box'><p>Question {st.session_state.current_step + 1}</p><h2>{q['question']}</h2></div>", unsafe_allow_html=True)
    
    for opt in q['options']:
        if st.button(opt, key=f"btn_{st.session_state.current_step}_{opt}"):
            if opt == q['answer']:
                st.session_state.score += 1
                play_sound("correct.mp3")
            else:
                play_sound("wrong.mp3")
            
            st.session_state.current_step += 1
            if st.session_state.current_step >= len(st.session_state.shuffled_indices):
                finish_round()
            st.rerun()

elif st.session_state.page == 'summary':
    play_sound("victory.mp3")
    st.markdown("<h1 style='text-align:center; color:white;'>🏆 LEADERSHIP BOARD 🏆</h1>", unsafe_allow_html=True)
    sorted_scores = sorted(st.session_state.leaderboard, key=lambda x: x['score'], reverse=True)
    for i, entry in enumerate(sorted_scores):
        st.markdown(f"<div class='question-box'><h3>{i+1}. {entry['name']}: {entry['score']} pts</h3></div>", unsafe_allow_html=True)
    if st.button("Restart"):
        st.session_state.page = 'welcome'
        st.rerun()
