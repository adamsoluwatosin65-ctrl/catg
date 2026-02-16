import streamlit as st
import json, time, os, random, base64

# --- PAGE CONFIG ---
st.set_page_config(page_title="CATG Quiz Pro", layout="centered")

# --- STYLE ---
st.markdown("""
    <style>
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

# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'welcome'
if 'leaderboard' not in st.session_state: st.session_state.leaderboard = []
if 'mute' not in st.session_state: st.session_state.mute = False
if 'volume' not in st.session_state: st.session_state.volume = 50
if 'audio_initialized' not in st.session_state: st.session_state.audio_initialized = False
if 'currently_playing' not in st.session_state: st.session_state.currently_playing = None

# --- AUDIO LOGIC ---
def get_audio_player(file_path, loop=True):
    """Generates the hidden audio tag"""
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            loop_attr = "loop" if loop else ""
            # We set an initial volume here based on the slider state
            init_vol = 0 if st.session_state.mute else st.session_state.volume / 100
            return f"""
                <audio autoplay="true" {loop_attr} id="quiz-audio-player" style="display:none;">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                <script>
                    document.getElementById('quiz-audio-player').volume = {init_vol};
                </script>
                """
    return ""

def update_volume_js():
    """JavaScript bridge to update volume without re-rendering the audio tag"""
    vol = 0 if st.session_state.mute else st.session_state.volume / 100
    return f"""
        <script>
            // Target the audio element in the parent or current document
            var aud = window.parent.document.getElementById('quiz-audio-player') || document.getElementById('quiz-audio-player');
            if(aud) {{
                aud.volume = {vol};
            }}
        </script>
        """

# --- SIDEBAR & VOLUME CONTROL ---
with st.sidebar:
    st.header("⚙️ Controls")
    st.session_state.mute = st.checkbox("Mute All Sounds", value=st.session_state.mute)
    st.session_state.volume = st.slider("Volume", 0, 100, st.session_state.volume)
    
    # DETERMINE WHAT SHOULD PLAY
    target_audio = None
    if st.session_state.audio_initialized and not st.session_state.mute:
        if st.session_state.page in ['quiz', 'next_turn', 'settings', 'mode_selection']:
            target_audio = "background_music.mp3"
        elif st.session_state.page == 'summary':
            target_audio = "winner_sound.mp3.mp3"

    # 1. ONLY INJECT AUDIO TAG IF THE SONG ACTUALLY CHANGES
    if target_audio != st.session_state.currently_playing:
        if target_audio:
            st.components.v1.html(get_audio_player(target_audio, loop=(target_audio=="background_music.mp3")), height=0)
        st.session_state.currently_playing = target_audio
    
    # 2. ALWAYS INJECT THE VOLUME UPDATE SCRIPT
    # This script runs on every slider movement but doesn't contain the audio file, so it doesn't reset the music.
    st.components.v1.html(update_volume_js(), height=0)

    st.markdown("---")
    if st.button("🚪 QUIT GAME"):
        st.session_state.clear()
        st.rerun()

# --- THE REST OF YOUR GAME LOGIC (Unchanged) ---
def finish_round():
    if 'current_player_name' in st.session_state:
        st.session_state.leaderboard.append({"name": st.session_state.current_player_name, "score": st.session_state.score})
    if st.session_state.get('game_mode') == 'multi' and st.session_state.player_index < st.session_state.total_players - 1:
        st.session_state.player_index += 1
        st.session_state.page = 'next_turn'
    else:
        st.session_state.page = 'summary'

@st.fragment(run_every=1)
def timer_display():
    if st.session_state.page == 'quiz' and 'start_time' in st.session_state:
        elapsed = time.time() - st.session_state.start_time
        remaining = int(st.session_state.time_limit - elapsed)
        if remaining <= 0:
            finish_round()
            st.rerun()
        st.markdown(f"<div style='text-align:right; font-weight:900; color:white; font-size:24px;'>⏱️ {remaining}s</div>", unsafe_allow_html=True)

if st.session_state.page == 'welcome':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists('logo.png'): st.image('logo.png', use_container_width=True)
        else: st.markdown("<h1 style='text-align:center; font-size: 80px;'>🏆</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: white;'>WELCOME TO CATG QUIZ</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #f0f0f0; font-size: 18px; font-weight: 600; font-style: italic;'>Win to get to leadership board</p>", unsafe_allow_html=True)
    if st.button("🔊 CLICK TO ENABLE SOUND & START"):
        st.session_state.audio_initialized = True
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
        p_name = st.text_input("Name", value="Player 1")
        st.session_state.player_names = [p_name]
        st.session_state.total_players = 1
    limit = st.selectbox("Time (Seconds)", [30, 60, 120])
    if st.button("START"):
        st.session_state.update({'page': 'quiz' if st.session_state.game_mode == 'single' else 'next_turn', 'player_index': 0, 'time_limit': limit, 'leaderboard': [], 'current_player_name': st.session_state.player_names[0]})
        if st.session_state.game_mode == 'single' and os.path.exists('questions.json'):
            qs = json.load(open('questions.json'))
            idx = list(range(len(qs))); random.shuffle(idx)
            st.session_state.update({'questions_data': qs, 'shuffled_indices': idx, 'score': 0, 'current_step': 0, 'start_time': time.time()})
        st.rerun()

elif st.session_state.page == 'next_turn':
    name = st.session_state.player_names[st.session_state.player_index]
    st.markdown(f"<h1 style='text-align:center; color:white;'>Ready, {name}?</h1>", unsafe_allow_html=True)
    if st.button("START MY TURN"):
        if os.path.exists('questions.json'):
            qs = json.load(open('questions.json'))
            idx = list(range(len(qs))); random.shuffle(idx)
            st.session_state.update({'page': 'quiz', 'score': 0, 'current_step': 0, 'start_time': time.time(), 'questions_data': qs, 'shuffled_indices': idx, 'current_player_name': name})
            st.rerun()

elif st.session_state.page == 'quiz':
    timer_display()
    if 'questions_data' in st.session_state:
        q = st.session_state.questions_data[st.session_state.shuffled_indices[st.session_state.current_step]]
        st.markdown(f"<div class='question-box'><h2>{q['question']}</h2></div>", unsafe_allow_html=True)
        for opt in q['options']:
            if st.button(opt, key=f"btn_{st.session_state.current_step}_{opt}"):
                if opt == q['answer']: st.session_state.score += 1
                st.session_state.current_step += 1
                if st.session_state.current_step >= len(st.session_state.shuffled_indices): finish_round()
                st.rerun()

elif st.session_state.page == 'summary':
    st.markdown("<h1 style='text-align:center; color:white;'>🏆 LEADERS 🏆</h1>", unsafe_allow_html=True)
    sorted_scores = sorted(st.session_state.leaderboard, key=lambda x: x['score'], reverse=True)
    for entry in sorted_scores:
        st.markdown(f"<div class='question-box'><h3>{entry['name']}: {entry['score']} pts</h3></div>", unsafe_allow_html=True)
    if st.button("Restart"):
        st.session_state.page = 'welcome'
        st.session_state.currently_playing = None 
        st.rerun()
