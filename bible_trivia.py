import streamlit as st
import json, time, os, random

# --- PAGE CONFIG ---
st.set_page_config(page_title="CATG Quiz Pro", layout="centered")

# --- DATABASE & PERSISTENCE FUNCTIONS ---
def load_accounts():
    if os.path.exists('accounts.json'):
        with open('accounts.json', 'r') as f:
            return json.load(f)
    return {}

def save_account(username, password, contact, high_score=0):
    accounts = load_accounts()
    # Preserve existing high score if not provided
    if username in accounts and high_score == 0:
        high_score = accounts[username].get("high_score", 0)
    
    accounts[username] = {
        "password": password, 
        "contact": contact, 
        "high_score": high_score
    }
    with open('accounts.json', 'w') as f:
        json.dump(accounts, f)

def update_high_score(username, new_score):
    accounts = load_accounts()
    if username in accounts:
        current_best = accounts[username].get("high_score", 0)
        if new_score > current_best:
            accounts[username]["high_score"] = new_score
            with open('accounts.json', 'w') as f:
                json.dump(accounts, f)
            return True
    return False

def get_remembered_user():
    if os.path.exists('remember_me.json'):
        with open('remember_me.json', 'r') as f:
            return json.load(f).get("username")
    return None

def set_remembered_user(username):
    with open('remember_me.json', 'w') as f:
        json.dump({"username": username}, f)

def clear_remembered_user():
    if os.path.exists('remember_me.json'):
        os.remove('remember_me.json')

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
    .question-box {
        background: rgba(255, 255, 255, 0.95);
        padding: 40px;
        border-radius: 30px;
        border-left: 12px solid #1e5631;
        box-shadow: 0 15px 30px rgba(0,0,0,0.1);
        margin-bottom: 30px;
        color: #1e5631;
    }
    .podium-card { padding: 20px; border-radius: 15px; margin: 10px 0; text-align: center; font-weight: 900; font-size: 22px; }
    .gold { background: #FFD700; color: #8B4513; border: 3px solid #DAA520; }
    .silver { background: #C0C0C0; color: #4F4F4F; border: 3px solid #A9A9A9; }
    .bronze { background: #CD7F32; color: #FAEBD7; border: 3px solid #8B4513; }
    .standard { background: white; color: #1e5631; border: 1px solid #ddd; }
    .stButton>button { width: 100%; border-radius: 20px; height: 4.5em; font-size: 18px; font-weight: 800; background: white; color: #1e5631; border: 2px solid #1e5631; transition: all 0.2s ease; }
    .stButton>button:hover { background-color: #1e5631 !important; color: white !important; }
    .balloon { position: fixed; will-change: transform; font-size: 50px; animation: spreadFloat 10s linear infinite; z-index: 99999; pointer-events: none; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'page' not in st.session_state:
    remembered = get_remembered_user()
    if remembered:
        st.session_state.user = remembered
        st.session_state.page = 'welcome'
    else:
        st.session_state.page = 'auth'
        st.session_state.user = None

if 'leaderboard' not in st.session_state: st.session_state.leaderboard = []
if 'muted' not in st.session_state: st.session_state.muted = False
if 'volume' not in st.session_state: st.session_state.volume = 50

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("Settings")
    if st.session_state.user:
        accs = load_accounts()
        personal_best = accs.get(st.session_state.user, {}).get("high_score", 0)
        st.write(f"Logged in as: **{st.session_state.user}**")
        st.write(f"🏆 Personal Best: **{personal_best}**")
        if st.button("Logout & Forget Me"):
            st.session_state.user = None
            st.session_state.page = 'auth'
            clear_remembered_user()
            st.rerun()
    st.session_state.muted = st.checkbox("Mute Sound", value=st.session_state.muted)

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
            update_high_score(st.session_state.user, st.session_state.score)
            if (st.session_state.p_name, st.session_state.score) not in st.session_state.leaderboard:
                st.session_state.leaderboard.append((st.session_state.p_name, st.session_state.score))
            st.session_state.page = 'summary'
            st.rerun()
        st.markdown(f"<div style='text-align:right; font-weight:900; color:white; font-size:24px; text-shadow: 1px 1px 5px black;'>⏱️ {remaining}s</div>", unsafe_allow_html=True)

# --- APP PAGES ---

if st.session_state.page == 'auth':
    st.markdown("<h1 style='text-align: center; color: white;'>CATG ACCOUNT</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    
    with tab1:
        login_user = st.text_input("Username (or Gmail)")
        login_pass = st.text_input("Password", type="password")
        remember_me = st.checkbox("Remember Me")
        if st.button("Login"):
            accounts = load_accounts()
            if login_user in accounts and accounts[login_user]['password'] == login_pass:
                st.session_state.user = login_user
                if remember_me:
                    set_remembered_user(login_user)
                st.session_state.page = 'welcome'
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        new_user = st.text_input("Choose Username/Gmail")
        new_contact = st.text_input("Gmail or Phone Number")
        new_pass = st.text_input("Create Password", type="password")
        if st.button("Sign Up"):
            if new_user and new_pass:
                save_account(new_user, new_pass, new_contact)
                st.success("Account Created! You can now Login.")
            else:
                st.warning("Please fill all fields")

elif st.session_state.page == 'welcome':
    col1, col2, col3 = st.columns([0.5, 3, 0.5])
    with col2:
        if os.path.exists('logo.png'):
            st.image('logo.png', use_container_width=True)
        else:
            st.markdown("<h1 style='text-align:center; font-size:80px;'>🎮</h1>", unsafe_allow_html=True)
    
    st.markdown(f"<h1 style='text-align: center; color: white;'>WELCOME, {st.session_state.user.upper()}!</h1>", unsafe_allow_html=True)
    
    accs = load_accounts()
    pb = accs.get(st.session_state.user, {}).get("high_score", 0)
    st.markdown(f"<p style='text-align: center; color: #FFD700; font-size: 24px; font-weight: bold;'>Your Record: {pb} PTS</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: white; font-size: 18px; opacity: 0.9;'>Win to get to leadership board</p>", unsafe_allow_html=True)
    
    if st.button("GET STARTED"): 
        st.session_state.page = 'register'
        st.rerun()

elif st.session_state.page == 'register':
    st.markdown("<h2 style='text-align: center; color: white;'>Player Entry</h2>", unsafe_allow_html=True)
    name = st.text_input("Display Name", value=st.session_state.user)
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
    if col2.button("BACK"): 
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
                    if opt == q['answer']: st.session_state.score += 1
                    else: st.session_state.wrong_answers.append({'question': q['question'], 'correct': q['answer'], 'yours': opt})
                    st.session_state.current_step += 1
                    st.rerun()
    else:
        update_high_score(st.session_state.user, st.session_state.score)
        if (st.session_state.p_name, st.session_state.score) not in st.session_state.leaderboard:
            st.session_state.leaderboard.append((st.session_state.p_name, st.session_state.score))
        st.session_state.page = 'summary'
        st.rerun()

# --- SUMMARY & FINAL PAGES (Remain same with update_high_score calls) ---
elif st.session_state.page == 'summary':
    st.markdown(f"<h1 style='text-align: center; color: white;'>Round Over, {st.session_state.p_name}!</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='question-box' style='text-align:center;'><h2>Final Score: {st.session_state.score}</h2></div>", unsafe_allow_html=True)
    cA, cB, cC = st.columns(3)
    if cA.button("RETRY"): st.session_state.page = 'register'; st.rerun()
    if cB.button("LEADERBOARD"): st.session_state.page = 'final'; st.rerun()
    if cC.button("QUIT"): st.session_state.page = 'welcome'; st.rerun()

elif st.session_state.page == 'final':
    play_audio("winner_sound.mp3", loop=False)
    st.markdown("<h1 style='text-align: center; color: white;'>🏆 LEADERSHIP BOARD 🏆</h1>", unsafe_allow_html=True)
    scores = sorted(st.session_state.leaderboard, key=lambda x: x[1], reverse=True)
    for i, (n, s) in enumerate(scores):
        style = "gold" if i == 0 else "silver" if i == 1 else "bronze" if i == 2 else "standard"
        st.markdown(f"<div class='podium-card {style}'>{i+1}. {n.upper()} — {s} PTS</div>", unsafe_allow_html=True)
    if st.button("BACK TO HOME"): st.session_state.page = 'welcome'; st.rerun()
