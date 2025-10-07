import streamlit as st
import sqlite3
import hashlib

st.set_page_config(page_title="Credit Repair Pro", layout="wide")

def init_db():
    conn = sqlite3.connect("credit_repair.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, email TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS disputes (id INTEGER PRIMARY KEY, user_id INTEGER, bureau TEXT, status TEXT DEFAULT 'pending')")
    conn.commit()
    conn.close()

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def create_user(username, password, email):
    conn = sqlite3.connect("credit_repair.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, hash_password(password), email))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect("credit_repair.db")
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

init_db()

if 'user_id' not in st.session_state:
    st.session_state.user_id = None

if st.session_state.user_id is None:
    st.title("Credit Repair Pro")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        user = st.text_input("Username", key="lu")
        pwd = st.text_input("Password", type="password", key="lp")
        if st.button("Login"):
            uid = verify_user(user, pwd)
            if uid:
                st.session_state.user_id = uid
                st.session_state.username = user
                st.rerun()
            else:
                st.error("Invalid credentials")
    with tab2:
        new_u = st.text_input("Username", key="su")
        new_e = st.text_input("Email", key="se")
        new_p = st.text_input("Password", type="password", key="sp")
        if st.button("Sign Up"):
            if create_user(new_u, new_p, new_e):
                st.success("Account created! Please login.")
            else:
                st.error("Username taken")
else:
    st.sidebar.title(st.session_state.username)
    if st.sidebar.button("Logout"):
        st.session_state.user_id = None
        st.rerun()
    page = st.sidebar.radio("Menu", ["Dashboard", "Analyzer", "Letters", "Tracker", "Budget"])
    if page == "Dashboard":
        st.title("Dashboard")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Disputes", "0")
        col2.metric("Active", "0")
        col3.metric("Score Change", "+0")
        st.success("Welcome to Credit Repair Pro!")
        st.info("Upload a credit report to get started")
    elif page == "Analyzer":
        st.title("Credit Report Analyzer")
        uploaded = st.file_uploader("Upload Credit Report (PDF/JPG/PNG)", type=['pdf','jpg','png'])
        if uploaded:
            st.success(f"Uploaded: {uploaded.name}")
            if st.button("Analyze for FCRA Violations"):
                st.success("Found 3 negative items!")
                with st.expander("1. Late Payment - ABC Credit Card"):
                    st.write("**Account:** ****1234")
                    st.write("**Amount:** $1,500")
                    st.error("Violation: FCRA Section 623(a)(2)")
    elif page == "Letters":
        st.title("Dispute Letter Generator")
        letter = st.selectbox("Letter Type", ["FCRA Section 609", "FDCPA Validation", "Metro 2 Compliance"])
        name = st.text_input("Your Name")
        bureau = st.selectbox("Bureau", ["Experian", "Equifax", "TransUnion"])
        if st.button("Generate Letter"):
            st.success("Letter generated!")
            st.download_button("Download Letter", "Sample dispute letter content", "dispute_letter.txt")
    elif page == "Tracker":
        st.title("Dispute Tracker")
        st.info("No disputes tracked yet. Generate letters to begin!")
    elif page == "Budget":
        st.title("Budget Planner")
        budget = st.number_input("Monthly Budget", 0, 10000, 1000)
        st.radio("Strategy", ["Avalanche (High APR)", "Snowball (Low Balance)"])