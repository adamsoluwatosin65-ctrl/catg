import streamlit as st
import json, time, os, random

# --- PAGE CONFIG ---
st.set_page_config(page_title="CATG Quiz Pro", layout="centered")

# --- DATABASE & PERSISTENCE ---
def load_accounts():
    if os.path.exists('accounts.json'):
        with open('accounts.json', 'r') as f:
            return json.load(f)
    return {}

def save_account(username, password, contact, high_score=0):
    accounts = load_accounts()
    if username in accounts and high_score == 0:
        high_score = accounts[username].get("high_score", 0)
    accounts[username] = {"password": password, "contact": contact, "high_score": high_score}
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

def get_global_top_10():
    accounts = load_accounts()
    # Create list of (username, score) and sort it
    score_list = [(u, info.get('high_score', 0)) for u, info in accounts.items()]
    return sorted(score_list, key=lambda x: x[1], reverse=True)[:10]

# --- PERFORMANCE DESIGN ---
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
        padding: 40px; border-radius: 30px; border-left: 12px solid #1e5631;
        box-shadow: 0 15px 30px rgba(0,0,0,0.1); margin-bottom: 30px; color: #1e5631;
    }
    .podium-card { padding: 15px; border-radius: 15px; margin: 8px 0; text-align: center; font-weight: 800; }
    .gold { background: #FFD700; color: #8B4513; border: 2px solid #DAA520; }
    .silver { background: #C0C0C0; color: #4F4F4F; border: 2px solid #A9A9A9; }
    .bronze { background: #CD7F32; color: #FAEBD7; border: 2px solid #8B4513; }
    .standard { background: white; color: #1e5631; border: 1px solid #ddd; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3.5em; font-weight: 800; background: white; color: #1e5631; border: 2px solid #1e5631; }
    .stButton>button:hover { background-color: #1e5631 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'auth'
if 'user' not in st.session_state: st.session_state.user = None

# --- APP PAGES ---

if st.session_state.page == 'auth':
    st.markdown("<h1 style='text-align: center; color: white;'>CATG ACCOUNT</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            accs = load_accounts()
            if u in accs and accs[u]['password'] == p:
                st.session_state.user = u
                st.session_state.page = 'welcome'
                st.rerun()
            else: st.error("Try again!")
    with tab2:
        nu = st.text_input("New Username")
        nc = st.text_input("Contact")
        np = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            save_account(nu, np, nc)
            st.success("Account Created!")

elif st.session_state.page == 'welcome':
    st.markdown(f"<h1 style='text-align: center; color: white;'>WELCOME, {st.session_state.user.upper()}!</h1>", unsafe_allow_html=True)
    
    # Global Leaderboard Preview on Front Page
    st.markdown("<div style='background:rgba(255,255,255,0.1); padding:20px; border-radius:20px;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:white;'>🏆 GLOBAL TOP 3</h3>", unsafe_allow_html=True)
    top_3 = get_global_top_10()[:3]
    for i, (name, score) in enumerate(top_3):
        style = "gold" if i == 0 else "silver" if i == 1 else "bronze"
        st.markdown(f"<div class='podium-card {style}' style='font-size:16px;'>{i+1}. {name} — {score} PTS</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("START NEW QUIZ"): 
        st.session_state.page = 'register'
        st.rerun()

elif st.session_state.page == 'register':
    # This page now just handles the time limit and starts the game
    st.markdown("<h2 style='text-align: center; color: white;'>Game Setup</h2>", unsafe_allow_html=True)
    limit = st.selectbox("Time Limit", [30, 60, 120])
    if st.button("GO!"):
        all_qs = json.load(open('questions.json')) if os.path.exists('questions.json') else []
        indices = list(range(len(all_qs))); random.shuffle(indices)
        st.session_state.update({'page': 'quiz', 'p_name': st.session_state.user, 'time_limit': limit, 'start_time': time.time(), 'score': 0, 'shuffled_indices': indices, 'current_step': 0, 'questions_data': all_qs})
        st.rerun()

elif st.session_state.page == 'quiz':
    # Simple logic to update high score at the end of the quiz
    # (Rest of quiz logic remains same...)
    elapsed = time.time() - st.session_state.start_time
    if elapsed >= st.session_state.time_limit:
        update_high_score(st.session_state.user, st.session_state.score)
        st.session_state.page = 'final'
        st.rerun()
    # Display quiz...
    st.write(f"Score: {st.session_state.score}")
    if st.button("Finish Early"):
        update_high_score(st.session_state.user, st.session_state.score)
        st.session_state.page = 'final'
        st.rerun()

elif st.session_state.page == 'final':
    st.markdown("<h1 style='text-align: center; color: white;'>GLOBAL RANKINGS</h1>", unsafe_allow_html=True)
    top_10 = get_global_top_10()
    for i, (name, score) in enumerate(top_10):
        style = "gold" if i == 0 else "silver" if i == 1 else "bronze" if i == 2 else "standard"
        st.markdown(f"<div class='podium-card {style}'>{i+1}. {name.upper()} — {score} PTS</div>", unsafe_allow_html=True)
    
    if st.button("HOME"): 
        st.session_state.page = 'welcome'
        st.rerun()
