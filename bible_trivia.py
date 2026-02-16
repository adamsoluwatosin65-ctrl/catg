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

    /* REMOVED backdrop-filter blur for performance on mobile */
    .question-box {
        background: rgba(255, 255, 255, 0.95);
        padding: 40px;
        border-radius: 30px;
        border-left: 12px solid #1e5631;
        box-shadow: 0 15px 30px rgba(0,0,0,0.1);
        margin-bottom: 30px;
        color: #1e5631;
    }

    .podium-card {
        padding: 20px; border-radius: 15px; margin: 10px 0;
        text-align: center; font-weight: 900; font-size: 22px;
    }
    .gold { background: #FFD700; color: #8B4513; border: 3px solid #DAA520; }
    .silver { background: #C0C0C0; color: #4F4F4F; border: 3px solid #A9A9A9; }
    .bronze { background: #CD7F32; color: #FAEBD7; border: 3px solid #8B4513; }
    .standard { background: white; color: #1e5631; border: 1px solid #ddd; }

    .stButton>button { 
        width: 100%; border-radius: 20px; height: 4.5em; 
        font-size: 18px; font-weight: 800; 
        background: white; color: #1e5631; border: 2px solid #1e5631; 
        transition: all 0.2s ease;
    }
    .stButton>button:hover { background-color: #1e5631 !important; color: white !important; }

    .balloon { position: fixed; will-change: transform; font-size: 50px; animation: spreadFloat 10s linear infinite; z-index: 99999; pointer-events: none; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'welcome'
if 'leaderboard' not in st.session_state: st.session_state.leaderboard = []
if 'muted' not in st.session_state: st.session_state.muted = False
if 'volume' not in st.session_state: st.session_state.volume = 50

# --- SIDEBAR CONTROLS (Sound) ---
with st.sidebar:
    st.title("Settings")
    st.session_state.muted = st.checkbox("Mute Sound", value=st.session_state.muted)
    st.session_state.volume = st.slider("Volume", 0, 100, st.session_state.volume)

def play_audio(file_path, loop=True):
    if not st.session_state.muted and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            # Note: Standard st.audio doesn't support volume control directly via Python, 
            # but muting works perfectly here.
            st.audio(f.read(), format="audio/mp3", loop=loop, autoplay=True)

@st.fragment(run_every=1)
def high_speed_timer():
    if st.session_state.page == 'quiz' and 'start_time' in st.session_state:
        elapsed = time.time() - st.session_state.start_time
        remaining = int(st.session_state.time_limit - elapsed)
        if remaining <= 0:
            if (st.session_state.p_name, st.session_state.score) not in st.session_state.leaderboard:
                st.session_state.leaderboard.append((st.session_state.p_name, st.session_state.score))
            st.session_state.page = 'summary'
            st.rerun()
        st.markdown(f"<div style='text-align:right; font-weight:900; color:white; font-size:24px; text-shadow: 1px 1px 5px black;'>⏱️ {remaining}s</div>", unsafe_allow_html=True)

# --- APP PAGES ---

if st.session_state.page == 'welcome':
    # Added Logo centered
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists('logo.png'):
            st.image('logo.png', use_container_width=True)
        else:
            st.markdown("<h1 style='text-align:center;'>🖼️</h1>", unsafe_allow_html=True) # Placeholder
    
    st.markdown("<h1 style='text-align: center; color: white;'>WELCOME TO CATG QUIZ</h1>", unsafe_allow_html=True)
    # Added Subtitle
    st.markdown("<p style='text-align: center; color: white; font-size: 20px; opacity: 0.9;'>Win to get to leadership board</p>", unsafe_allow_html=True)
    
    if st.button("GET STARTED"): 
        st.session_state.page = 'register'
        st.rerun()

elif st.session_state.page == 'register':
    st.markdown("<h2 style='text-align: center; color: white;'>Player Entry</h2>", unsafe_allow_html=True)
    name = st.text_input("Player Name")
    limit = st.selectbox("Time Limit (Seconds)", [30, 60, 120, 300], index=1)
    col1, col2 = st.columns(2)
    if col1.button("START QUIZ"):
        if name:
            all_qs = json.load(open('questions.json')) if os.path.exists('questions.json') else []
            shuffled_indices = list(range(len(all_qs)))
            random.shuffle(shuffled_indices)
            st.session_state.update({
                'page': 'quiz', 'p_name': name, 'time_limit': limit, 
                'start_time': time.time(), 'score': 0, 
                'shuffled_indices': shuffled_indices, 'current_step': 0, 
                'wrong_answers': [], 'questions_data': all_qs
            })
            st.rerun()
    if col2.button("QUIT"): 
        st.session_state.clear()
        st.session_state.page = 'welcome'
        st.rerun()

elif st.session_state.page == 'quiz':
    play_audio("background_music.mp3")
    high_speed_timer()
    
    if 'questions_data' in st.session_state and st.session_state.current_step < len(st.session_state.shuffled_indices):
        step = st.session_state.current_step
        q_idx = st.session_state.shuffled_indices[step]
        q = st.session_state.questions_data[q_idx]
        
        with st.container():
            st.markdown(f"""<div class="question-box">
                <p style="opacity:0.6; font-size:14px; margin:0;">QUESTION {step+1} OF {len(st.session_state.shuffled_indices)}</p>
                <h2 style="margin-top:10px;">{q['question']}</h2>
            </div>""", unsafe_allow_html=True)
            
            for opt in q['options']:
                if st.button(opt, key=f"q{step}_{opt}"):
                    if opt == q['answer']: 
                        st.session_state.score += 1
                    else: 
                        st.session_state.wrong_answers.append({'question': q['question'], 'correct': q['answer'], 'yours': opt})
                    st.session_state.current_step += 1
                    st.rerun()
    else:
        if (st.session_state.p_name, st.session_state.score) not in st.session_state.leaderboard:
            st.session_state.leaderboard.append((st.session_state.p_name, st.session_state.score))
        st.session_state.page = 'summary'
        st.rerun()

elif st.session_state.page == 'summary':
    st.markdown(f"<h1 style='text-align: center; color: white;'>Round Over, {st.session_state.p_name}!</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='question-box' style='text-align:center;'><h2>Final Score: {st.session_state.score}</h2></div>", unsafe_allow_html=True)
    
    if st.session_state.wrong_answers:
        with st.expander("🔍 Review Mistakes"):
            for item in st.session_state.wrong_answers:
                st.markdown(f"<div style='background:white; color:black; padding:10px; border-radius:10px; margin-bottom:5px;'><b>Q: {item['question']}</b><br><span style='color:red;'>Your: {item['yours']}</span> | <span style='color:green;'>Correct: {item['correct']}</span></div>", unsafe_allow_html=True)
    
    cA, cB, cC = st.columns(3)
    if cA.button("NEXT PLAYER"): st.session_state.page = 'register'; st.rerun()
    if cB.button("LEADERBOARD"): st.session_state.page = 'final'; st.rerun()
    if cC.button("QUIT"): st.session_state.clear(); st.session_state.page = 'welcome'; st.rerun()

elif st.session_state.page == 'final':
    play_audio("winner_sound.mp3", loop=False)
    
    # Balloons
    balloon_list = ["🎈", "🎊", "✨", "⭐"]
    balloons_html = "".join([f'<div class="balloon" style="left:{random.randint(0,95)}%; bottom:{random.randint(-20, 50)}vh; animation-delay:{random.uniform(0,8)}s;">{random.choice(balloon_list)}</div>' for _ in range(25)])
    st.markdown(balloons_html, unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: white;'>🏆 LEADERSHIP BOARD 🏆</h1>", unsafe_allow_html=True)
    
    scores = sorted(st.session_state.leaderboard, key=lambda x: x[1], reverse=True)
    for i, (n, s) in enumerate(scores):
        style = "gold" if i == 0 else "silver" if i == 1 else "bronze" if i == 2 else "standard"
        st.markdown(f"<div class='podium-card {style}'>{i+1}. {n.upper()} — {s} PTS</div>", unsafe_allow_html=True)
        
    c1, c2, c3 = st.columns(3)
    if c1.button("NEXT PLAYER"): st.session_state.page = 'register'; st.rerun()
    if c2.button("RESET ALL"): st.session_state.clear(); st.rerun()
    if c3.button("QUIT"): st.session_state.clear(); st.session_state.page = 'welcome'; st.rerun()
