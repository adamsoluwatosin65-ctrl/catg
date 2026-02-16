
import streamlit as st
import json, time, os, random

# --- PAGE CONFIG ---
st.set_page_config(page_title="CATG Quiz Pro", layout="centered")

# --- HIGH-END ANIMATED DESIGN ---
st.markdown("""
    <style>
    audio { display: none; }

    .stApp {
        background: linear-gradient(-45deg, #1e5631, #2a7a45, #a8e063, #f0f4f1);
        background-size: 400% 400%;
        animation: activeGradient 12s ease infinite;
        background-attachment: fixed;
    }

    @keyframes activeGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: radial-gradient(circle at 50% 50%, rgba(255,255,255,0.1) 0%, transparent 50%);
        animation: auraMove 8s infinite alternate;
        pointer-events: none;
    }

    @keyframes auraMove {
        from { transform: scale(1) translate(-10%, -10%); }
        to { transform: scale(1.2) translate(10%, 10%); }
    }

    .question-box {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(15px);
        padding: 40px;
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-left: 12px solid #1e5631;
        box-shadow: 0 25px 50px rgba(0,0,0,0.15);
        margin-bottom: 30px;
        color: #1e5631;
    }

    .podium-card {
        padding: 20px; border-radius: 15px; margin: 10px 0;
        text-align: center; font-weight: 900; font-size: 22px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .gold { background: linear-gradient(90deg, #FFD700, #FFFACD); color: #8B4513; border: 3px solid #DAA520; }
    .silver { background: linear-gradient(90deg, #C0C0C0, #F5F5F5); color: #4F4F4F; border: 3px solid #A9A9A9; }
    .bronze { background: linear-gradient(90deg, #CD7F32, #FAEBD7); color: #5D2906; border: 3px solid #8B4513; }
    .standard { background: white; color: #1e5631; border: 1px solid #ddd; font-size: 18px; font-weight: bold; }

    .stButton>button { 
        width: 100%; border-radius: 20px; height: 4.5em; 
        font-size: 18px; font-weight: 800; 
        background: white; color: #1e5631; border: 2px solid #1e5631; 
        transition: all 0.3s ease;
    }
    .stButton>button:hover { background-color: #1e5631 !important; color: white !important; transform: scale(1.02); }

    @keyframes spreadFloat {
        0% { transform: translateY(110vh) rotate(0deg); opacity: 0; }
        10% { opacity: 1; }
        100% { transform: translateY(-20vh) rotate(20deg); opacity: 0; }
    }
    .balloon { position: fixed; font-size: 50px; animation: spreadFloat 10s linear infinite; z-index: 99999 !important; pointer-events: none; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'welcome'
if 'leaderboard' not in st.session_state: st.session_state.leaderboard = []
if 'muted' not in st.session_state: st.session_state.muted = False

def play_audio(file_path, loop=True):
    if not st.session_state.muted and os.path.exists(file_path):
        with open(file_path, "rb") as f:
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
    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        if os.path.exists('logo.png'): st.image('logo.png', use_container_width=True)
    st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px 10px rgba(0,0,0,0.3);'>WELCOME TO CATG QUIZ</h1>", unsafe_allow_html=True)
    if st.button("GET STARTED"): st.session_state.page = 'register'; st.rerun()

elif st.session_state.page == 'register':
    st.markdown("<h2 style='text-align: center; color: white;'>Player Entry</h2>", unsafe_allow_html=True)
    name = st.text_input("Player Name")
    limit = st.selectbox("Time Limit (Seconds)", [30, 60, 120, 300], index=1)
    col1, col2 = st.columns(2)
    if col1.button("START QUIZ"):
        if name:
            all_qs = json.load(open('questions.json')) if os.path.exists('questions.json') else []
            shuffled_indices = list(range(len(all_qs))); random.shuffle(shuffled_indices)
            st.session_state.update({
                'page': 'quiz', 'p_name': name, 'time_limit': limit, 
                'start_time': time.time(), 'score': 0, 
                'shuffled_indices': shuffled_indices, 'current_step': 0, 
                'wrong_answers': [], 'questions_data': all_qs
            })
            st.rerun()
    if col2.button("QUIT"): st.session_state.clear(); st.session_state.page = 'welcome'; st.rerun()

elif st.session_state.page == 'quiz':
    play_audio("background_music.mp3")
    high_speed_timer()
    
    # Validation to ensure questions exist
    if 'questions_data' in st.session_state and st.session_state.current_step < len(st.session_state.shuffled_indices):
        step = st.session_state.current_step
        q_idx = st.session_state.shuffled_indices[step]
        q = st.session_state.questions_data[q_idx]
        
        # UI Container to keep Question + Options together
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
        # Finish quiz if questions are exhausted
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
    play_audio("winner_sound.mp3.mp3", loop=False)
    balloon_list = ["🎈", "🎊", "✨", "⭐"]
    balloons_html = "".join([f'<div class="balloon" style="left:{random.randint(0,95)}%; bottom:{random.randint(-20, 50)}vh; animation-delay:{random.uniform(0,8)}s;">{random.choice(balloon_list)}</div>' for _ in range(40)])
    st.markdown(balloons_html, unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: white;'>🏆 LEADERSHIP BOARD 🏆</h1>", unsafe_allow_html=True)
    
    # Sort scores
    scores = sorted(st.session_state.leaderboard, key=lambda x: x[1], reverse=True)
    for i, (n, s) in enumerate(scores):
        if i == 0: style = "gold"
        elif i == 1: style = "silver"
        elif i == 2: style = "bronze"
        else: style = "standard"
        st.markdown(f"<div class='podium-card {style}'>{i+1}. {n.upper()} — {s} PTS</div>", unsafe_allow_html=True)
        
    c1, c2, c3 = st.columns(3)
    if c1.button("NEXT PLAYER"): st.session_state.page = 'register'; st.rerun()
    if c2.button("RESET ALL"): st.session_state.clear(); st.rerun()
    if c3.button("QUIT"): st.session_state.clear(); st.session_state.page = 'welcome'; st.rerun()