import streamlit as st
import json, time, os, random

# --- PAGE CONFIG ---
st.set_page_config(page_title="CATG Quiz Pro", layout="centered")

# --- DATABASE FUNCTIONS ---
def load_accounts():
    if os.path.exists('accounts.json'):
        with open('accounts.json', 'r') as f: return json.load(f)
    return {}

def save_account(username, password, contact):
    accounts = load_accounts()
    accounts[username] = {"password": password, "contact": contact, "high_score": 0}
    with open('accounts.json', 'w') as f: json.dump(accounts, f)

# --- APP STYLING ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(-45deg, #1e5631, #2a7a45, #a8e063); background-size: 400% 400%; animation: activeGradient 15s ease infinite; }
    @keyframes activeGradient { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .question-box { background: white; padding: 30px; border-radius: 20px; border-left: 10px solid #1e5631; color: #1e5631; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 15px; height: 3.5em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'auth'
if 'user' not in st.session_state: st.session_state.user = None
if 'verify_code' not in st.session_state: st.session_state.verify_code = None

# --- AUTHENTICATION & SMS SIMULATION ---
if st.session_state.page == 'auth':
    st.markdown("<h1 style='text-align: center; color: white;'>CATG QUIZ</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            accs = load_accounts()
            if u in accs and accs[u]['password'] == p:
                st.session_state.user = u
                st.session_state.page = 'mode_selection'
                st.rerun()
            else: st.error("Invalid Login")

    with tab2:
        if 'step' not in st.session_state: st.session_state.step = 1
        
        if st.session_state.step == 1:
            nu = st.text_input("New Username")
            n_phone = st.text_input("Phone Number")
            np = st.text_input("New Password", type="password")
            if st.button("Send Verification Code"):
                st.session_state.temp_user = (nu, np, n_phone)
                st.session_state.verify_code = str(random.randint(1000, 9999))
                st.info(f"📱 SMS SENT! (Simulated Code: {st.session_state.verify_code})")
                st.session_state.step = 2
                st.rerun()
        
        elif st.session_state.step == 2:
            code = st.text_input("Enter 4-Digit Code")
            if st.button("Confirm & Create Account"):
                if code == st.session_state.verify_code:
                    save_account(*st.session_state.temp_user)
                    st.success("Verified! Please Login.")
                    st.session_state.step = 1
                    time.sleep(1)
                    st.rerun()
                else: st.error("Wrong Code")

# --- MODE SELECTION ---
elif st.session_state.page == 'mode_selection':
    st.markdown(f"<h1 style='text-align:center; color:white;'>Welcome, {st.session_state.user}!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:white;'>Select Your Game Mode</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    if col1.button("👤 Single Player"):
        st.session_state.mode = 'Single'
        st.session_state.page = 'register'
        st.rerun()
    if col2.button("🌐 Play Online"):
        st.warning("Searching for global match...")
    if col3.button("👥 Play with Friends"):
        st.session_state.room = str(random.randint(100, 999))
        st.info(f"Share this Link: `https://catg-quiz.streamlit.app/?room={st.session_state.room}`")

elif st.session_state.page == 'register':
    limit = st.selectbox("Time Limit", [30, 60, 120])
    if st.button("START QUIZ"):
        all_qs = json.load(open('questions.json')) if os.path.exists('questions.json') else []
        indices = list(range(len(all_qs))); random.shuffle(indices)
        st.session_state.update({
            'page': 'quiz', 'score': 0, 'current_step': 0,
            'start_time': time.time(), 'time_limit': limit,
            'questions_data': all_qs, 'shuffled_indices': indices
        })
        st.rerun()

# --- THE QUIZ (FIXED) ---
elif st.session_state.page == 'quiz':
    elapsed = time.time() - st.session_state.start_time
    remaining = int(st.session_state.time_limit - elapsed)
    
    if remaining <= 0 or st.session_state.current_step >= len(st.session_state.shuffled_indices):
        st.session_state.page = 'summary'
        st.rerun()

    st.markdown(f"<h3 style='text-align:right; color:white;'>⏱️ {remaining}s</h3>", unsafe_allow_html=True)
    
    # LOAD QUESTION
    q_idx = st.session_state.shuffled_indices[st.session_state.current_step]
    q = st.session_state.questions_data[q_idx]

    st.markdown(f"<div class='question-box'><h2>{q['question']}</h2></div>", unsafe_allow_html=True)

    # DISPLAY OPTIONS AS BUTTONS
    for opt in q['options']:
        if st.button(opt, key=f"btn_{st.session_state.current_step}_{opt}"):
            if opt == q['answer']:
                st.session_state.score += 1
            st.session_state.current_step += 1
            st.rerun()

    if st.button("Finish Early", type="secondary"):
        st.session_state.page = 'summary'
        st.rerun()

elif st.session_state.page == 'summary':
    st.balloons()
    st.markdown(f"<h1 style='text-align:center; color:white;'>Finished!</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='question-box' style='text-align:center;'><h2>Score: {st.session_state.score}</h2></div>", unsafe_allow_html=True)
    if st.button("Back to Menu"):
        st.session_state.page = 'mode_selection'
        st.rerun()
