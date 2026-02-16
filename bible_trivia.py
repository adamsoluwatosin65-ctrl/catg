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

# --- STYLING ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(-45deg, #1e5631, #2a7a45, #a8e063); background-size: 400% 400%; animation: activeGradient 15s ease infinite; }
    @keyframes activeGradient { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .question-box { background: white; padding: 30px; border-radius: 20px; border-left: 10px solid #1e5631; color: #1e5631; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 15px; height: 3.5em; font-weight: bold; }
    /* Alert style for the simulated SMS */
    .sms-alert { background: #fff3cd; color: #856404; padding: 15px; border-radius: 10px; border: 1px solid #ffeeba; margin-bottom: 20px; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'auth'
if 'user' not in st.session_state: st.session_state.user = None
if 'verify_code' not in st.session_state: st.session_state.verify_code = None
if 'reg_step' not in st.session_state: st.session_state.reg_step = 1

# --- AUTH & VERIFICATION ---
if st.session_state.page == 'auth':
    st.markdown("<h1 style='text-align: center; color: white;'>CATG QUIZ</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("Login"):
            accs = load_accounts()
            if u in accs and accs[u]['password'] == p:
                st.session_state.user = u
                st.session_state.page = 'mode_selection'
                st.rerun()
            else: st.error("Invalid Login")

    with tab2:
        if st.session_state.reg_step == 1:
            nu = st.text_input("Username", key="reg_u")
            n_phone = st.text_input("Phone Number", key="reg_phone")
            np = st.text_input("Password", type="password", key="reg_p")
            
            if st.button("Register & Send Code"):
                if nu and n_phone and np:
                    # SIMULATING THE SMS SENDING
                    st.session_state.verify_code = str(random.randint(1000, 9999))
                    st.session_state.temp_data = {"u": nu, "p": np, "c": n_phone}
                    st.session_state.reg_step = 2
                    st.rerun()
                else:
                    st.warning("Please fill all fields")
        
        elif st.session_state.reg_step == 2:
            # SHOWING THE "SMS" TO THE USER
            st.markdown(f"""<div class="sms-alert">📱 SMS RECEIVED: Your CATG verification code is: {st.session_state.verify_code}</div>""", unsafe_allow_html=True)
            
            input_code = st.text_input("Enter 4-Digit Code", key="verify_input")
            if st.button("Verify & Login"):
                if input_code == st.session_state.verify_code:
                    save_account(st.session_state.temp_data['u'], st.session_state.temp_data['p'], st.session_state.temp_data['c'])
                    st.success("Verification Successful!")
                    time.sleep(1)
                    st.session_state.user = st.session_state.temp_data['u']
                    st.session_state.page = 'mode_selection'
                    st.rerun()
                else:
                    st.error("Incorrect code. Please try again.")
            
            if st.button("Back"):
                st.session_state.reg_step = 1
                st.rerun()

# --- MODE SELECTION ---
elif st.session_state.page == 'mode_selection':
    st.markdown(f"<h1 style='text-align:center; color:white;'>Welcome, {st.session_state.user}!</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("👤 Single Player"):
            st.session_state.page = 'register'
            st.rerun()
    with col2:
        if st.button("🌐 Online Match"):
            st.info("Searching for opponents...")
    with col3:
        if st.button("👥 Play Friends"):
            room_id = random.randint(1000, 9999)
            st.success(f"Room Created! ID: {room_id}")
            st.code(f"Invite Link: https://catg-quiz.streamlit.app/?room={room_id}")

# --- THE QUIZ LOGIC ---
elif st.session_state.page == 'register':
    limit = st.selectbox("Time Limit (Seconds)", [30, 60, 120])
    if st.button("START"):
        # Ensure questions.json exists
        if os.path.exists('questions.json'):
            all_qs = json.load(open('questions.json'))
            indices = list(range(len(all_qs)))
            random.shuffle(indices)
            st.session_state.update({
                'page': 'quiz', 'score': 0, 'current_step': 0,
                'start_time': time.time(), 'time_limit': limit,
                'questions_data': all_qs, 'shuffled_indices': indices
            })
            st.rerun()
        else:
            st.error("Error: questions.json not found!")

elif st.session_state.page == 'quiz':
    elapsed = time.time() - st.session_state.start_time
    remaining = int(st.session_state.time_limit - elapsed)
    
    if remaining <= 0 or st.session_state.current_step >= len(st.session_state.shuffled_indices):
        st.session_state.page = 'summary'
        st.rerun()

    st.markdown(f"<h2 style='text-align:right; color:white;'>⏱️ {remaining}s</h2>", unsafe_allow_html=True)
    
    q_idx = st.session_state.shuffled_indices[st.session_state.current_step]
    q = st.session_state.questions_data[q_idx]

    st.markdown(f"<div class='question-box'><h3>{q['question']}</h3></div>", unsafe_allow_html=True)

    # DISPLAY THE QUESTIONS AS BUTTONS (FIXED)
    for opt in q['options']:
        if st.button(opt, key=f"q_{st.session_state.current_step}_{opt}"):
            if opt == q['answer']:
                st.session_state.score += 1
            st.session_state.current_step += 1
            st.rerun()

elif st.session_state.page == 'summary':
    st.balloons()
    st.markdown(f"<div class='question-box' style='text-align:center;'><h1>Final Score: {st.session_state.score}</h1></div>", unsafe_allow_html=True)
    if st.button("Menu"):
        st.session_state.page = 'mode_selection'
        st.rerun()
