import streamlit as st
import json, time, os, random

# --- PAGE CONFIG ---
st.set_page_config(page_title="CATG Quiz Pro", layout="centered")

# --- DATABASE FUNCTIONS ---
def load_accounts():
    if os.path.exists('accounts.json'):
        with open('accounts.json', 'r') as f: return json.load(f)
    return {}

def save_account(username, password):
    accounts = load_accounts()
    # Storing only what is necessary for immediate access
    accounts[username] = {"password": password, "high_score": 0}
    with open('accounts.json', 'w') as f: json.dump(accounts, f)

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
    .stButton>button { width: 100%; border-radius: 20px; height: 3.5em; font-size: 18px; font-weight: 800; background: white; color: #1e5631; border: 2px solid #1e5631; transition: all 0.2s ease; position: relative; z-index: 1; }
    .stButton>button:hover { background-color: #1e5631 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'auth'
if 'user' not in st.session_state: st.session_state.user = None

# --- TIMER FRAGMENT ---
@st.fragment(run_every=1)
def timer_display():
    if st.session_state.page == 'quiz' and 'start_time' in st.session_state:
        elapsed = time.time() - st.session_state.start_time
        remaining = int(st.session_state.time_limit - elapsed)
        if remaining <= 0:
            st.session_state.page = 'summary'
            st.rerun()
        st.markdown(f"<div style='text-align:right; font-weight:900; color:white; font-size:24px;'>⏱️ {remaining}s</div>", unsafe_allow_html=True)

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
if st.session_state.page == 'auth':
    st.markdown("<h1 style='text-align: center; color: white;'>CATG QUIZ</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("Login"):
            accs = load_accounts()
            if u in accs and accs[u]['password'] == p:
                st.session_state.user, st.session_state.page = u, 'mode_selection'
                st.rerun()
            else: st.error("Invalid Login")
    with tab2:
        nu = st.text_input("Choose Username", key="reg_u")
        np = st.text_input("Choose Password", type="password", key="reg_p")
        if st.button("Create Account"):
            if nu and np:
                save_account(nu, np)
                st.success("Account Created! You can now login.")
            else:
                st.warning("Please enter a username and password.")

elif st.session_state.page == 'mode_selection':
    st.markdown(f"<h1 style='text-align:center; color:white;'>Welcome, {st.session_state.user}!</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("👤 Single Player"): st.session_state.page = 'register'; st.rerun()
    if c2.button("🌐 Online"): st.info("Coming Soon")
    if c3.button("👥 Friends"): st.info(f"Room: {random.randint(1000, 9999)}")

elif st.session_state.page == 'register':
    st.markdown("<h2 style='text-align:center; color:white;'>Settings</h2>", unsafe_allow_html=True)
    limit = st.selectbox("Time Limit (Seconds)", [30, 60, 120])
    if st.button("START"):
        if os.path.exists('questions.json'):
            qs = json.load(open('questions.json'))
            idx = list(range(len(qs)))
            random.shuffle(idx)
            st.session_state.update({'page':'quiz', 'score':0, 'current_step':0, 'start_time':time.time(), 'time_limit':limit, 'questions_data':qs, 'shuffled_indices':idx})
            st.rerun()

elif st.session_state.page == 'quiz':
    timer_display()
    q = st.session_state.questions_data[st.session_state.shuffled_indices[st.session_state.current_step]]
    st.markdown(f"<div class='question-box'><p>Question {st.session_state.current_step + 1}</p><h2>{q['question']}</h2></div>", unsafe_allow_html=True)
    
    for opt in q['options']:
        if st.button(opt, key=f"btn_{st.session_state.current_step}_{opt}"):
            if opt == q['answer']:
                st.session_state.score += 1
            st.session_state.current_step += 1
            if st.session_state.current_step >= len(st.session_state.shuffled_indices):
                st.session_state.page = 'summary'
            st.rerun()

elif st.session_state.page == 'summary':
    show_balloons()
    st.markdown(f"<h1 style='text-align:center; color:white; position:relative; z-index:1;'>Score: {st.session_state.score}</h1>", unsafe_allow_html=True)
    if st.button("Menu"): st.session_state.page = 'mode_selection'; st.rerun()
