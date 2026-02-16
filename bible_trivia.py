import streamlit as st
import json, time, os, random

# --- PAGE CONFIG ---
st.set_page_config(page_title="CATG Quiz Pro", layout="centered")

# --- PERFORMANCE OPTIMIZED DESIGN ---
st.markdown("""
    <style>
    audio { display: none; }
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
    
    .floating-container {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }
    .float-item {
        position: absolute;
        bottom: -100px;
        font-size: 40px;
        will-change: transform;
        animation: floatUp 8s linear infinite;
    }
    @keyframes floatUp {
        0% { transform: translate3d(0, 0, 0) rotate(0deg); opacity: 1; }
        100% { transform: translate3d(20px, -120vh, 0) rotate(360deg); opacity: 0; }
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
        transition: all 0.2s ease; position: relative; z-index: 1; 
    }
    .stButton>button:hover { background-color: #1e5631 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

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
    # Save the current player's score to the round leaderboard
    st.session_state.leaderboard.append({"name": st.session_state.current_player_name, "score": st.session_state.score})
    
    # Check if there are more players left
    if st.session_state.game_mode == 'multi' and st.session_state.player_index < st.session_state.total_players - 1:
        st.session_state.player_index += 1
        st.session_state.page = 'next_turn'
    else:
        st.session_state.page = 'summary'

# --- FLOATING EFFECT ---
def show_balloons():
    icons = ["🎈", "🎊", "✨", "⭐", "🎉"]
    html = '<div class="floating-container">'
    for i in range(15):
        left = random.randint(0, 95)
        delay = random.uniform(0, 5)
        icon = random.choice(icons)
        html += f'<div class="float-item" style="left:{left}%; animation-delay:{delay}s;">{icon}</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# --- APP PAGES ---

if st.session_state.page == 'welcome':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists('logo.png'): st.image('logo.png', use_container_width=True)
        else: st.markdown("<h1 style='text-align:center; font-size: 80px;'>🏆</h1>", unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: white;'>WELCOME TO CATG QUIZ</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #f0f0f0; font-size: 18px; font-weight: 600; font-style: italic;'>Win to get to leadership board</p>", unsafe_allow_html=True)
    
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
        pname = st.text_input("Player Name", value="Guest")
        st.session_state.player_names = [pname]
        st.session_state.total_players = 1

    limit = st.selectbox("Time Limit per Player (Seconds)", [30, 60, 120, 300])
    
    if st.button("START GAME"):
        st.session_state.update({
            'page': 'quiz' if st.session_state.game_mode == 'single' else 'next_turn',
            'player_index': 0,
            'time_limit': limit,
            'leaderboard': []
        })
        st.rerun()

elif st.session_state.page == 'next_turn':
    name = st.session_state.player_names[st.session_state.player_index]
    st.markdown(f"<h1 style='text-align:center; color:white;'>Ready, {name}?</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:white;'>Pass the device to the player above.</p>", unsafe_allow_html=True)
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
    st.markdown(f"<p style='color:white; font-weight:bold;'>Player: {st.session_state.current_player_name}</p>", unsafe_allow_html=True)
    q = st.session_state.questions_data[st.session_state.shuffled_indices[st.session_state.current_step]]
    st.markdown(f"<div class='question-box'><p>Question {st.session_state.current_step + 1}</p><h2>{q['question']}</h2></div>", unsafe_allow_html=True)
    
    for opt in q['options']:
        if st.button(opt, key=f"btn_{st.session_state.current_step}_{opt}"):
            if opt == q['answer']: st.session_state.score += 1
            st.session_state.current_step += 1
            if st.session_state.current_step >= len(st.session_state.shuffled_indices):
                finish_round()
            st.rerun()

elif st.session_state.page == 'summary':
    show_balloons()
    st.markdown("<h1 style='text-align:center; color:white;'>🏆 LEADERSHIP BOARD 🏆</h1>", unsafe_allow_html=True)
    
    # Sort scores: Highest first
    sorted_scores = sorted(st.session_state.leaderboard, key=lambda x: x['score'], reverse=True)
    
    for i, entry in enumerate(sorted_scores):
        rank_icon = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "👤"
        st.markdown(f"""
            <div class='question-box' style='padding: 20px; margin-bottom: 10px;'>
                <h3 style='margin:0;'>{rank_icon} {entry['name']}: {entry['score']} Points</h3>
            </div>
        """, unsafe_allow_html=True)

    if st.button("Back to Main Menu"):
        st.session_state.page = 'welcome'
        st.rerun()
