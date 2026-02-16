import streamlit as st
import json, time, os, random, base64

# --- PAGE CONFIG ---
st.set_page_config(page_title="CATG Quiz Pro", layout="centered")

# --- PERFORMANCE OPTIMIZED DESIGN ---
st.markdown("""
    <style>
    .hidden-audio { display: none; height: 0; width: 0; }
    
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
    }
    .stButton>button { 
        width: 100%; border-radius: 20px; height: 3.5em; 
        font-size: 18px; font-weight: 800; 
        background: white; color: #1e5631; border: 2px solid #1e5631; 
    }
    .stButton>button:hover { background-color: #1e5631 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- AUDIO LOGIC ---
if 'mute' not in st.session_state: st.session_state.mute = False
if 'volume' not in st.session_state: st.session_state.volume = 50
if 'audio_initialized' not in st.session_state: st.session_state.audio_initialized = False

def play_sound(file_path, loop=False):
    """Refined audio trigger using components for better browser compatibility"""
    if not st.session_state.mute and st.session_state.audio_initialized and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            vol = st.session_state.volume / 100
            loop_attr = "loop" if loop else ""
            # A unique key ensures the HTML component refreshes and plays every time
            unique_key = f"audio_{file_path}_{time.time()}"
            md = f"""
                <audio autoplay="true" {loop_attr} id="player">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                <script>
                    var audio = document.getElementById("player");
                    audio.volume = {vol};
                </script>
                """
            st.components.v1.html(md, height=0)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Controls")
    st.session_state.mute = st.checkbox("Mute All Sounds", value=st.session_state.mute)
    st.session_state.volume = st.slider("Volume", 0, 100, st.session_state.volume)
    st.markdown("---")
    if st.button("🚪 QUIT GAME"):
        st.session_state.clear()
        st.rerun()

# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'welcome'
if 'leaderboard' not in st.session_state: st.session_state.leaderboard = []

def finish_round():
    st.session_state.leaderboard.append({"name": st.session_state.current_player_name, "score": st.session_state.score})
    if st.session_state.game_mode == 'multi' and st.session_state.player_index < st.session_state.total_players - 1:
        st.session_state.player_index += 1
        st.session_state.page = 'next_turn'
    else:
        st.session_state.page = 'summary'

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

# --- APP PAGES ---

if st.session_state.page == 'welcome':
    # --- LOGO SECTION ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists('logo.png'):
            st.image('logo.png', use_container_width=True)
        else:
            # Fallback if logo.png is missing or named differently
            st.markdown("<h1 style='text-align:center; font-size: 80px;'>🏆</h1>", unsafe_allow_html=True)
            
    st.markdown("<h1 style='text-align: center; color: white;'>WELCOME TO CATG QUIZ</h1>", unsafe_allow_html=True)
    # --- SUBTITLE RESTORED ---
    st.markdown("<p style='text-align: center; color: #f0f0f0; font-size: 18px; font-weight: 600; font-style: italic;'>Win to get to leadership board</p>", unsafe_allow_html=True)
    
    if not st.session_state.audio_initialized:
        st.info("Please enable sound to play with audio experience.")
        if st.button("🔊 CLICK TO ENABLE SOUND & START"):
            st.session_state.audio_initialized = True
            st.session_state.page = 'mode_selection'
            st.rerun()
    else:
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
        st.session_state.player_names = [st.text_input(f"Player {i+1}", key=f"p_{i}") or f"Player {i+1}" for i in range(total_p)]
    else:
        st.session_state.player_names = [st.text_input("Name", value="Player 1")]
        st.session_state.total_players = 1

    limit = st.selectbox("Time (Seconds)", [30, 60, 120])
    if st.button("START"):
        st.session_state.update({'page': 'quiz' if st.session_state.game_mode == 'single' else 'next_turn', 'player_index': 0, 'time_limit': limit, 'leaderboard': []})
        if st.session_state.game_mode == 'single':
            st.session_state.current_player_name = st.session_state.player_names[0]
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
            st.session_state.update({'page': 'quiz', 'score': 0, 'current_step': 0, 'start_time': time.time(), 'questions_data': qs, 'shuffled_indices': idx, 'current_player_name': name})
            st.rerun()

elif st.session_state.page == 'quiz':
    play_sound("background_music.mp3", loop=True)
    timer_display()
    q = st.session_state.questions_data[st.session_state.shuffled_indices[st.session_state.current_step]]
    st.markdown(f"<div class='question-box'><h2>{q['question']}</h2></div>", unsafe_allow_html=True)
    for opt in q['options']:
        if st.button(opt, key=f"btn_{st.session_state.current_step}_{opt}"):
            if opt == q['answer']: st.session_state.score += 1
            st.session_state.current_step += 1
            if st.session_state.current_step >= len(st.session_state.shuffled_indices): finish_round()
            st.rerun()

elif st.session_state.page == 'summary':
    play_sound("winnner_sound.mp3.mp3")
    st.markdown("<h1 style='text-align:center; color:white;'>🏆 LEADERS 🏆</h1>", unsafe_allow_html=True)
    sorted_scores = sorted(st.session_state.leaderboard, key=lambda x: x['score'], reverse=True)
    for entry in sorted_scores:
        st.markdown(f"<div class='question-box'><h3>{entry['name']}: {entry['score']} pts</h3></div>", unsafe_allow_html=True)
    if st.button("Restart"):
        st.session_state.page = 'welcome'
        st.rerun()
