import streamlit as st
import pandas as pd
from datetime import datetime
from database import conn, c
from helpers import *
from fee_management import show_fee_management
from exam_management import show_exam_management

st.set_page_config(page_title="M.S. Public School ERP", layout="wide", page_icon="🏫")

# ==========================================
# 🎨 BULLETPROOF UI CSS (FORCES BROWSER TO APPLY DESIGN)
# ==========================================
page_bg_css = """
<style>
/* 1. MAIN BUTTONS (Solid Blue, Hover Red) - FORCED */
div[data-testid="stButton"] button {
    background-color: #1F497D !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stButton"] button:hover {
    background-color: #ff4b4b !important;
    color: #ffffff !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 15px rgba(255, 75, 75, 0.4) !important;
}

/* 2. SIDEBAR TABS (Hide Radio Circles & Style as 3D Buttons) */
/* This hides the actual circular dot of the radio button */
[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
    display: none !important;
}

/* Styles the label box like a Modern Tab */
[data-testid="stSidebar"] div[role="radiogroup"] label {
    background-color: transparent !important;
    border: 1px solid rgba(128, 128, 128, 0.3) !important;
    padding: 10px 15px !important;
    margin-bottom: 8px !important;
    border-radius: 8px !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    display: block !important;
}

/* Hover effect on tabs (Slides Right slightly) */
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background-color: rgba(255, 75, 75, 0.1) !important;
    border-color: #ff4b4b !important;
    transform: translateX(5px) !important;
}

/* ACTIVE TAB STYLE (Turns Solid Blue and Pushes Forward) */
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background-color: #1F497D !important;
    border-color: #1F497D !important;
    box-shadow: 0 4px 10px rgba(31, 73, 125, 0.4) !important;
    transform: translateX(8px) !important;
}

/* Active Tab Text Color (Forces White text) */
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
    color: #ffffff !important;
    font-weight: 800 !important;
}

/* 3. LOGIN BOX 3D EFFECT */
[data-testid="stForm"] {
    background-color: var(--secondary-background-color);
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
    border: 1px solid rgba(128, 128, 128, 0.2);
    transition: transform 0.3s ease;
}
[data-testid="stForm"]:hover {
    transform: translateY(-2px);
}

/* 4. Input Fields Focus Effect */
.stTextInput input, .stNumberInput input {
    border-radius: 8px;
    transition: all 0.3s ease;
    border: 1px solid rgba(128, 128, 128, 0.3);
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #ff4b4b !important;
    box-shadow: 0 0 10px rgba(255, 75, 75, 0.25) !important;
}
</style>
"""
st.markdown(page_bg_css, unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_data = None
    st.session_state.admin_id = None

# ==========================================
# 🔐 LOGIN SCREEN 
# ==========================================
if not st.session_state.logged_in:
    colA, colB, colC = st.columns([1.5, 2, 1.5])
    
    with colB:
        st.markdown(f"<div style='text-align: center;'><img src='{LOGO_BASE64}' width='140'></div>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>M.S. PUBLIC SCHOOL</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #888; margin-top: 0px;'>Enterprise ERP Portal</h4><br>", unsafe_allow_html=True)
        
        login_type = st.radio("Select Portal Access", ["Student Portal", "Admin Portal"], horizontal=True)
        
        with st.form("login_form"):
            if login_type == "Admin Portal":
                st.info("👨‍💻 Secure Admin Access")
                username = st.text_input("Admin Username / Mobile", placeholder="Enter your ID...")
                password = st.text_input("Password", type="password", placeholder="Enter Password...")
                
                col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                with col_btn2:
                    submit = st.form_submit_button("Secure Login ➔", use_container_width=True)
                    
                if submit:
                    if username in ADMIN_USERS and password == ADMIN_USERS[username]:
                        st.session_state.logged_in = True
                        st.session_state.role = "Admin"
                        st.session_state.admin_id = username  
                        force_rerun()
                    else:
                        st.error("❌ Invalid Admin Credentials!")
            
            else:
                st.info("🎓 Student Dashboard Access")
                s_roll = st.number_input("Roll No", min_value=1, step=1)
                s_dob_obj = st.date_input("Date of Birth", value=datetime(2015, 1, 1), min_value=datetime(1990, 1, 1), max_value=datetime.today())
                
                col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                with col_btn2:
                    submit = st.form_submit_button("View Profile ➔", use_container_width=True)
                    
                if submit:
                    s_dob_str = s_dob_obj.strftime("%d-%m-%Y") 
                    c.execute("SELECT * FROM student_master WHERE roll_no=? AND dob=?", (s_roll, s_dob_str))
                    stu = c.fetchone()
                    if stu:
                        st.session_state.logged_in = True
                        st.session_state.role = "Student"
                        st.session_state.user_data = stu
                        force_rerun()
                    else:
                        st.error("❌ Roll No or Date of Birth is incorrect!")

# ==========================================
# 🎓 STUDENT PORTAL
# ==========================================
elif st.session_state.role == "Student":
    stu = st.session_state.user_data
    current_m_idx = get_current_m_idx()
    
    st.sidebar.markdown(f"### 👨‍🎓 Welcome, {stu[1]}!")
    st.sidebar.markdown(f"**Class:** {stu[2]} | **Roll No:** {stu[0]}")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Secure Logout", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.role = None; st.session_state.user_data = None; force_rerun()

    st.title("🎓 Student Dashboard")
    tab1, tab2 = st.tabs(["💰 Fee Details", "📝 Exam Results"])
    
    with tab1:
        st.subheader("Your Fee Summary")
        pay, paid, due, adv, _ = get_student_financials(stu[0], current_m_idx)
        c1, c2, c3 = st.columns(3)
        c1.info(f"Total Expected: ₹{pay:,}"); c2.success(f"Total Paid: ₹{paid:,}")
        if due > 0: c3.error(f"Current Due: ₹{due:,}")
        else: c3.success(f"Advance Rcvd: ₹{adv:,}")
        
        st.write("---")
        st.write("📋 **Recent Payments**")
        c.execute('''SELECT receipt_no, date, amount, mode, head FROM fee_log WHERE roll_no=? ORDER BY date DESC''', (stu[0],))
        logs = c.fetchall()
        if logs:
            st.dataframe(pd.DataFrame(logs, columns=["Receipt No", "Date", "Amount", "Mode", "Fee Head"]), use_container_width=True, hide_index=True)
        else:
            st.warning("No payments recorded yet.")

        st.write("---")
        st.write("📊 **Detailed Month-by-Month Statement**")
        
        c.execute("SELECT * FROM fee_structure WHERE class=?", (stu[2],))
        fs = c.fetchone()
        heads = [('Registration Fee', fs[1], 1), ('Admission Fee', fs[2], 1), ('Other Fee', fs[9], 1)]
        c.execute("SELECT item_name, amount FROM student_charges WHERE roll_no=?", (stu[0],))
        for item in c.fetchall(): heads.append((f"{item[0]} (EXTRA)", item[1], 1))
        heads.extend([('April Tuition', fs[3], 1), ('May Tuition', fs[3], 2), ('June Tuition', fs[3], 3), ('July Tuition', fs[3], 4), ('Quarterly Exam', fs[4], 4), ('August Tuition', fs[3], 5), ('September Tuition', fs[3], 6), ('October Tuition', fs[3], 7), ('Half-Yearly Exam', fs[5], 7), ('November Tuition', fs[3], 8), ('December Tuition', fs[3], 9), ('January Tuition', fs[3], 10), ('February Tuition', fs[3], 11), ('March Tuition', fs[3], 12), ('Yearly Exam', fs[6], 12)])
        
        pool = paid; table_data = []
        for h_name, base_amt, m_idx in heads:
            amt = base_amt
            if "Tuition" in h_name:
                if stu[4] == "Van": amt += fs[7]
                if stu[5] == "ENGLISH": amt += fs[8]
            paid_here = min(amt, max(0, pool))
            pool -= paid_here
            if amt <= 0: status = "-"
            elif paid_here >= amt: status = "🟢 Paid"
            elif paid_here > 0: status = "🟡 Partial"
            elif m_idx <= current_m_idx: status = "🔴 Due"
            else: status = "⚪ Upcoming"
            curr_due = max(0, amt - paid_here) if m_idx <= current_m_idx else 0
            table_data.append([h_name.upper(), f"₹{amt:,}", f"₹{paid_here:,}", status, f"₹{curr_due:,}"])
            
        st.dataframe(pd.DataFrame(table_data, columns=["Fee Head / Month", "Payable", "Paid", "Status", "Current Due"]), use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Your Exam Marks")
        ordered_subjects = get_subjects_for_class(stu[2])
        marks_data = []
        for subj in ordered_subjects:
            c.execute("SELECT ut1, hy, ut2, annual FROM marks_entry WHERE roll_no=? AND subject=?", (stu[0], subj))
            res = c.fetchone()
            if res:
                row_tot = res[0] + res[1] + res[2] + res[3]
                marks_data.append([subj, res[0], res[1], res[2], res[3], row_tot, get_grade(row_tot)])
        
        if marks_data:
            df_m = pd.DataFrame(marks_data, columns=["Subject", "UT 1", "Half Yearly", "UT 2", "Annual", "Total (100)", "Grade"])
            st.dataframe(df_m, use_container_width=True, hide_index=True)
        else:
            st.info("Exam results are not published yet.")

# ==========================================
# ⚙️ ADMIN PORTAL
# ==========================================
elif st.session_state.role == "Admin":
    st.sidebar.markdown(f"<div style='text-align: center;'><img src='{LOGO_BASE64}' width='80'></div>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<h3 style='text-align:center;'>👨‍💻 Admin: {st.session_state.admin_id}</h3>", unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Secure Logout", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.role = None; st.session_state.admin_id = None; force_rerun()
    st.sidebar.markdown("---")
    
    st.title("🏫 M.S. Public School - Enterprise ERP")
    
    active_module = st.sidebar.radio("Select Active Module:", ["💰 Fee Management", "📝 Result & Admit Card"])
    st.sidebar.markdown("---")
    current_m_idx = get_current_m_idx()

    if active_module == "💰 Fee Management":
        show_fee_management(current_m_idx)
    elif active_module == "📝 Result & Admit Card":
        show_exam_management()