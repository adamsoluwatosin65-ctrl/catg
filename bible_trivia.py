import streamlit as st
import json, time, os, random
from twilio.rest import Client  # You must run 'pip install twilio'

# --- TWILIO SETUP ---
# Replace these with your actual Twilio credentials
TWILIO_SID = 'YOUR_ACCOUNT_SID_HERE'
TWILIO_AUTH_TOKEN = 'YOUR_AUTH_TOKEN_HERE'
TWILIO_PHONE = 'YOUR_TWILIO_NUMBER_HERE'

def send_real_sms(to_phone, code):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Your CATG Quiz verification code is: {code}",
            from_=TWILIO_PHONE,
            to=to_phone
        )
        return True
    except Exception as e:
        st.error(f"SMS Failed: {e}")
        return False

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
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'auth'
if 'user' not in st.session_state: st.session_state.user = None
if 'reg_step' not in st.session_state: st.session_state.reg_step = 1

# --- AUTH & REAL SMS VERIFICATION ---
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
            n_phone = st.text_input("Phone (Include country code e.g., +234...)", key="reg_phone")
            np = st.text_input("Password", type="password", key="reg_p")
            
            if st.button("Register & Send Real SMS"):
                if nu and n_phone and np:
                    code = str(random.randint(1000, 9999))
                    # CALL THE REAL SMS FUNCTION
                    if send_real_sms(n_phone, code):
                        st.session_state.verify_code = code
                        st.session_state.temp_data = {"u": nu, "p": np, "c": n_phone}
                        st.session_state.reg_step = 2
                        st.success("Verification code sent to your phone!")
                        st.rerun()
                else:
                    st.warning("Please fill all fields correctly")
        
        elif st.session_state.reg_step == 2:
            st.info(f"Check your phone {st.session_state.temp_data['c']} for the code.")
            input_code = st.text_input("Enter 4-Digit Code", key="verify_input")
            if st.button("Verify & Login"):
                if input_code == st.session_state.verify_code:
                    save_account(st.session_state.temp_data['u'], st.session_state.temp_data['p'], st.session_state.temp_data['c'])
                    st.session_state.user = st.session_state.temp_data['u']
                    st.session_state.page = 'mode_selection'
                    st.rerun()
                else:
                    st.error("Incorrect code.")

# --- MODE SELECTION ---
elif st.session_state.page == 'mode_selection':
    st.markdown(f"<h1 style='text-align:center; color:white;'>Welcome, {st.session_state.user}!</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    if col1.button("👤 Single Player"):
        st.session_state.page = 'register'
        st.rerun()
    if col2.button("🌐 Online Match"): st.info("Coming Soon!")
    if col3.button("👥 Play Friends"): st.info("Room System Active!")

# --- QUIZ LOGIC (FIXED) ---
elif st.session_state.page == 'register':
    limit = st.selectbox("Time Limit (Seconds)", [30, 60, 120])
    if st.button("START"):
        if os.path.exists('questions.json'):
            all_qs = json.load(open('questions.json'))
            indices = list(range(len(all_qs))); random.shuffle(indices)
            st.session_state.update({'page': 'quiz', 'score': 0, 'current_step': 0, 'start_time': time.time(), 'time_limit': limit, 'questions_data': all_qs, 'shuffled_indices': indices})
            st.rerun()

elif st.session_state.page == 'quiz':
    elapsed = time.time() - st.session_state.start_time
    remaining = int(st.session_state.time_limit - elapsed)
    if remaining <= 0 or st.session_state.current_step >= len(st.session_state.shuffled_indices):
        st.session_state.page = 'summary'; st.rerun()
    
    q_idx = st.session_state.shuffled_indices[st.session_state.current_step]
    q = st.session_state.questions_data[q_idx]
    st.markdown(f"<div class='question-box'><h3>{q['question']}</h3></div>", unsafe_allow_html=True)
    
    for opt in q['options']:
        if st.button(opt, key=f"q_{st.session_state.current_step}_{opt}"):
            if opt == q['answer']: st.session_state.score += 1
            st.session_state.current_step += 1
            st.rerun()

elif st.session_state.page == 'summary':
    st.balloons()
    st.markdown(f"<h1 style='text-align:center; color:white;'>Score: {st.session_state.score}</h1>", unsafe_allow_html=True)
    if st.button("Menu"): st.session_state.page = 'mode_selection'; st.rerun()
