import streamlit as st
import pandas as pd
from datetime import datetime
from database import conn, c
from helpers import *
from fee_management import show_fee_management
from exam_management import show_exam_management

# Page Config
st.set_page_config(page_title="M.S. Public School ERP", layout="wide", page_icon="🏫")

# ==========================================
# 🎨 ADAPTIVE CSS: ENTERPRISE ERP DESIGN
# ==========================================
page_bg_css = """
<style>
/* Remove Streamlit Default Header Border & Gap */
[data-testid="stHeader"] { 
    background-color: transparent !important; 
    box-shadow: none !important; 
    border-bottom: none !important; 
}
.block-container { max-width: 1300px; padding-top: 1.5rem !important; padding-left: 1rem; padding-right: 1rem; }

/* Navbar Area */
.nav-links { display: flex; gap: 25px; color: var(--text-color); font-weight: 600; font-size: 15px; margin-top: 25px; justify-content: center;}
.nav-links span { cursor: pointer; transition: color 0.3s; opacity: 0.9;}
.nav-links span:hover { color: #0ea5e9; opacity: 1;}

/* 🌟 STANDARD BUTTONS 🌟 */
div[data-testid="stButton"] button {
    background-color: #0b214a !important; 
    color: #ffffff !important; 
    border: none !important;
    border-radius: 8px !important; 
    font-weight: 700 !important; 
    letter-spacing: 0.5px;
    padding: 0.6rem 1.5rem !important;
    box-shadow: 0 4px 10px rgba(11, 33, 74, 0.2) !important; 
    transition: all 0.3s ease !important;
    margin-top: 10px; 
}
div[data-testid="stButton"] button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 15px rgba(11, 33, 74, 0.4) !important;
    background-color: #17366e !important;
}

/* 🌟 CONTENT BOXES (For Landing Page) 🌟 */
.content-box {
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(130, 130, 130, 0.2); 
    border-radius: 12px;
    padding: 25px;
    transition: all 0.3s ease;
    margin-bottom: 20px;
}
.content-box:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    border-color: #0ea5e9; 
}

/* 🌟 DARK SIDEBAR (ENTERPRISE LOOK) 🌟 */
[data-testid="stSidebar"] {
    background-color: #0b214a !important;
}
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.1) !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label {
    background-color: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    padding: 10px 15px !important;
    margin-bottom: 8px !important;
    transition: all 0.3s ease !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background-color: rgba(255,255,255,0.15) !important;
    border-color: #0ea5e9 !important;
    transform: translateX(5px) !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(45deg, #0ea5e9, #0284c7) !important;
    border-color: #0ea5e9 !important;
    transform: translateX(8px) !important;
    box-shadow: 0 4px 10px rgba(14, 165, 233, 0.4) !important;
}

/* 🌟 DASHBOARD METRIC CARDS (Transforms st.metric into UI Cards) 🌟 */
div[data-testid="metric-container"] {
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(130, 130, 130, 0.2);
    padding: 20px 25px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border-left: 5px solid #0ea5e9; /* Default Accent */
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}
div[data-testid="stMetricLabel"] { font-size: 14px; font-weight: 700; opacity: 0.8; }
div[data-testid="stMetricValue"] { font-size: 28px; font-weight: 900; }

/* Custom Dashboard KPI HTML Cards */
.dash-card {
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(130, 130, 130, 0.2);
    border-radius: 12px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    transition: transform 0.3s ease;
    margin-bottom: 15px;
}
.dash-card:hover { transform: translateY(-4px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); border-color: #0ea5e9;}
.dash-icon { width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold; }
.dash-title { margin: 0; font-size: 14px; font-weight: 700; color: var(--text-color); opacity: 0.8;}
.dash-val { margin: 0; font-size: 28px; font-weight: 900; color: var(--text-color);}
.dash-trend { margin: 5px 0 0 0; font-size: 12px; font-weight: 700;}

/* Login Form Styling */
.login-card-container {
    background-color: var(--secondary-background-color);
    padding: 40px 30px;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    border: 1px solid rgba(130, 130, 130, 0.15);
    margin-top: 20px; margin-bottom: 20px;
}
[data-testid="stForm"] { background-color: transparent; padding: 0; border: none; box-shadow: none !important; }
div[role="radiogroup"] { justify-content: center; margin-bottom: 20px; margin-top: 10px; }
.stTextInput label, .stNumberInput label, .stDateInput label { font-weight: 700 !important; opacity: 0.8; }
</style>
"""
st.markdown(page_bg_css, unsafe_allow_html=True)

# 🔄 SESSION STATE INIT
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_data = None
    st.session_state.admin_id = None
    st.session_state.show_login = False

# ==========================================
# 🏠 PUBLIC LANDING PAGE & 🔐 LOGIN SCREEN
# ==========================================
if not st.session_state.logged_in:
    if not st.session_state.show_login:
        
        # --- LOGO, NAV & BUTTON ROW ---
        col_logo, col_nav, col_btn = st.columns([3, 5, 2])
        with col_logo:
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-top: 10px;">
                <img src='{LOGO_BASE64}' width='65' style='margin-right: 15px;'>
                <div>
                    <h2 style='margin:0; font-weight:800; font-size:22px; color: var(--text-color);'>M.S. PUBLIC SCHOOL</h2>
                    <p style='margin:0; color:#0ea5e9; font-size:11px; font-weight:700; letter-spacing: 2px;'>LEARN | LEAD | GROW</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_nav:
            st.markdown("""
            <div class="nav-links">
                <span style="border-bottom: 2px solid #0ea5e9; padding-bottom: 3px;">Home</span>
                <span>About Us</span>
                <span>Academics</span>
                <span>Facilities</span>
                <span>Contact Us</span>
            </div>
            """, unsafe_allow_html=True)
            
        with col_btn:
            if st.button("🧑‍💻 Portal Login", use_container_width=True):
                st.session_state.show_login = True
                force_rerun()
                
        st.markdown("<hr style='border:1px solid rgba(130,130,130,0.2); margin: 15px 0 30px 0;'>", unsafe_allow_html=True)
                
        # --- MAIN CONTENT ---
        col_main, col_space, col_side = st.columns([1.6, 0.1, 1])
        
        with col_main:
            st.markdown("""
            <div class="content-box">
                <p class="hero-welcome">WELCOME TO</p>
                <h1 class="hero-title">M.S. PUBLIC SCHOOL</h1>
                <h2 class="hero-subtitle" style="margin-top:10px;">Building Bright Futures Through Quality Education</h2>
                <p class="hero-desc">We provide a safe, supportive and inspiring environment where every child can learn, grow and achieve their dreams under expert guidance.</p>
            </div>
            """, unsafe_allow_html=True)
            
            f1, f2 = st.columns(2)
            features = [
                ("👨‍🏫", "#2563eb", "Qualified Teachers", "Experienced and dedicated faculty members."),
                ("📚", "#16a34a", "Modern Curriculum", "Focus on academics, moral values, and skills."),
                ("🏛️", "#eab308", "Safe & Secure Campus", "A highly protective environment for every child."),
                ("⭐", "#dc2626", "Excellent Results", "Consistent top performance and bright future.")
            ]
            
            for i, (icon, color, title, text) in enumerate(features):
                target_col = f1 if i % 2 == 0 else f2
                with target_col:
                    st.markdown(f"""
                    <div class="content-box feature-card" style="padding: 15px; margin-bottom: 15px;">
                        <div class="f-icon-wrap" style="background-color: {color}; min-width: 50px; height: 50px;">{icon}</div>
                        <div>
                            <p style="font-size: 16px; font-weight: 700; margin: 0 0 2px 0;">{title}</p>
                            <p style="font-size: 13px; opacity: 0.7; margin: 0;">{text}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        with col_side:
            notices_html = '<div class="content-box" style="border-top: 3px solid #e11d48;">'
            notices_html += '<h3 style="margin-top:0; border-bottom: 2px solid rgba(130,130,130,0.2); padding-bottom: 10px;">📢 Latest News & Updates</h3>'
            try:
                c.execute("SELECT n.date, n.title, n.content FROM school_notices n WHERE n.is_active=1 ORDER BY n.id DESC LIMIT 4")
                notices = c.fetchall()
                if notices:
                    for n in notices:
                        try:
                            d_obj = datetime.strptime(n[0], "%Y-%m-%d")
                            day = d_obj.strftime("%d")
                            mon = d_obj.strftime("%b")
                        except:
                            day, mon = "00", "---"
                        notices_html += f'<div style="display:flex; gap:15px; border-bottom:1px dashed rgba(130,130,130,0.3); padding:10px 0;">'
                        notices_html += f'<div style="background:var(--background-color); border:1px solid rgba(130,130,130,0.3); border-radius:6px; padding:5px; text-align:center; min-width:50px;"><p style="margin:0; font-weight:900; font-size:16px;">{day}</p><p style="margin:0; font-size:11px; color:#e11d48; font-weight:bold;">{mon}</p></div>'
                        notices_html += f'<div><p style="margin:0 0 4px 0; font-weight:700; font-size:14px;">{n[1]}</p><p style="margin:0; font-size:12px; opacity:0.8;">{n[2]}</p></div>'
                        notices_html += '</div>'
                else:
                    notices_html += '<p style="color:#16a34a; font-weight:700;">✨ No new notices at the moment.</p>'
            except:
                notices_html += '<p style="color:#eab308;">Notice board is currently being initialized.</p>'
            notices_html += '</div>'
            st.markdown(notices_html, unsafe_allow_html=True)

        st.markdown(
            '<div style="text-align:center; margin-top:40px; padding: 20px; border-top: 1px solid rgba(130,130,130,0.2); opacity: 0.7; font-size:14px;">'
            '<p style="margin:0;">© 2026 M.S. Public School. All Rights Reserved. | Designed for Enterprise ERP System</p></div>', 
            unsafe_allow_html=True
        )

    else:
        # ==========================================
        # 🔐 PREMIUM OFFICIAL LOGIN SCREEN
        # ==========================================
        col_back, col_space = st.columns([1, 8])
        with col_back:
            if st.button("⬅️ Home", key="back_btn"):
                st.session_state.show_login = False
                force_rerun()
                
        colA, colB, colC = st.columns([1, 1.2, 1])
        with colB:
            st.markdown("<div class='login-card-container'>", unsafe_allow_html=True)
            
            st.markdown("<div style='text-align: center; margin-top: -10px;'><h1 style='font-size: 55px; margin-bottom: 0px;'>🎓</h1></div>", unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center; color: var(--text-color); margin-top: 0px; margin-bottom: 5px; font-weight: 900; letter-spacing: 1px;'>OFFICIAL PORTAL</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748b; font-size: 15px; margin-bottom: 10px;'>Please login to continue to your account</p>", unsafe_allow_html=True)
            
            # Sorted Order: Student -> Teacher -> Admin
            login_type = st.radio("Select Portal Access", ["Student Portal", "Teacher Portal", "Admin Portal"], horizontal=True, label_visibility="collapsed")
            
            with st.form("login_form"):
                if login_type == "Student Portal":
                    s_roll = st.number_input("👤 Roll No", min_value=1, step=1)
                    s_dob_obj = st.date_input("🔒 Date of Birth", value=datetime(2015, 1, 1), min_value=datetime(1990, 1, 1), max_value=datetime.today())
                    st.markdown("<br>", unsafe_allow_html=True)
                    submit = st.form_submit_button("Login ➔", use_container_width=True)
                    if submit:
                        s_dob_str = s_dob_obj.strftime("%d-%m-%Y") 
                        c.execute("SELECT * FROM student_master WHERE roll_no=? AND dob=?", (s_roll, s_dob_str))
                        stu = c.fetchone()
                        if stu:
                            st.session_state.logged_in = True; st.session_state.role = "Student"; st.session_state.user_data = stu; force_rerun()
                        else: st.error("❌ Roll No or Date of Birth is incorrect!")
                
                elif login_type == "Teacher Portal":
                    t_id = st.text_input("👤 Teacher ID", placeholder="Enter your Teacher ID")
                    t_pass = st.text_input("🔒 Password", type="password", placeholder="Enter your Password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    submit = st.form_submit_button("Login ➔", use_container_width=True)
                    if submit:
                        c.execute("SELECT * FROM teacher_master WHERE teacher_id=? AND password=?", (t_id.strip(), t_pass.strip()))
                        tch = c.fetchone()
                        if tch:
                            st.session_state.logged_in = True; st.session_state.role = "Teacher"; st.session_state.user_data = tch; force_rerun()
                        else: st.error("❌ Invalid Teacher ID or Password!")
                        
                else: 
                    username = st.text_input("👤 Admin ID / Mobile", placeholder="Enter your Admin ID")
                    password = st.text_input("🔒 Password", type="password", placeholder="Enter your Password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    submit = st.form_submit_button("Login ➔", use_container_width=True)
                    if submit:
                        if username in ADMIN_USERS and password == ADMIN_USERS[username]:
                            st.session_state.logged_in = True; st.session_state.role = "Admin"; st.session_state.admin_id = username; force_rerun()
                        else: st.error("❌ Invalid Admin Credentials!")
            
            st.markdown("</div>", unsafe_allow_html=True)

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
        
        c.execute('''SELECT f.receipt_no, f.date, f.amount, f.mode, f.head FROM fee_log f WHERE f.roll_no=? ORDER BY f.date DESC''', (stu[0],))
        logs = c.fetchall()
        if logs: st.dataframe(pd.DataFrame(logs, columns=["Receipt No", "Date", "Amount", "Mode", "Fee Head"]), use_container_width=True, hide_index=True)
        else: st.warning("No payments recorded yet.")

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
        if marks_data: st.dataframe(pd.DataFrame(marks_data, columns=["Subject", "UT 1", "Half Yearly", "UT 2", "Annual", "Total (100)", "Grade"]), use_container_width=True, hide_index=True)
        else: st.info("Exam results are not published yet.")

# ==========================================
# 👨‍🏫 TEACHER PORTAL (RESTRICTED ACCESS)
# ==========================================
elif st.session_state.role == "Teacher":
    tch = st.session_state.user_data
    st.sidebar.markdown(f"<div style='text-align: center;'><img src='{LOGO_BASE64}' width='80'></div>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<h3 style='text-align:center; color:white;'>👨‍🏫 {tch[2]}</h3>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align:center; color:gray;'>ID: {tch[1]}</p>", unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Secure Logout", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.role = None; st.session_state.user_data = None; force_rerun()
    st.sidebar.markdown("---")
    
    st.title("👨‍🏫 Teacher Dashboard")
    active_module = st.sidebar.radio("Select Active Module:", ["💰 Fee Module", "📝 Exam Module"])
    st.sidebar.markdown("---")
    current_m_idx = get_current_m_idx()

    if active_module == "💰 Fee Module":
        show_fee_management(current_m_idx)
    elif active_module == "📝 Exam Module":
        show_exam_management()

# ==========================================
# ⚙️ ADMIN PORTAL (FULL ACCESS - ENTERPRISE ERP)
# ==========================================
elif st.session_state.role == "Admin":
    st.sidebar.markdown(f"<div style='text-align: center;'><img src='{LOGO_BASE64}' width='80'></div>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<h3 style='text-align:center; color:white;'>👨‍💻 Admin: {st.session_state.admin_id}</h3>", unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Secure Logout", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.role = None; st.session_state.admin_id = None; force_rerun()
    st.sidebar.markdown("---")
    
    # 🌟 Added "📊 Dashboard" as the first option to show the ERP Analytics UI 🌟
    active_module = st.sidebar.radio("Select Active Module:", ["📊 Dashboard", "💰 Fee Management", "📝 Result & Admit Card", "📢 Manage Notices", "👨‍🏫 Manage Teachers"])
    st.sidebar.markdown("---")
    current_m_idx = get_current_m_idx()

    if active_module == "📊 Dashboard":
        # Build the exact Dashboard UI from the reference image
        st.markdown("<h2 style='margin-bottom:0;'>🏫 M.S. Public School - Enterprise ERP</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; font-size:15px;'>Welcome to M.S. Public School Analytics Dashboard! 📈</p>", unsafe_allow_html=True)
        
        # Calculate real data dynamically
        c.execute("SELECT COUNT(*) FROM student_master")
        tot_stu = c.fetchone()[0] or 0
        c.execute("SELECT SUM(amount) FROM fee_log")
        tot_fee = c.fetchone()[0] or 0
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div class="dash-card" style="border-left: 5px solid #3b82f6;">
                <div class="dash-icon" style="background:#eff6ff; color:#3b82f6;">👥</div>
                <div>
                    <p class="dash-title">Total Students</p>
                    <p class="dash-val">{tot_stu}</p>
                    <p class="dash-trend" style="color:#10b981;">↑ +12% vs last month</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="dash-card" style="border-left: 5px solid #10b981;">
                <div class="dash-icon" style="background:#ecfdf5; color:#10b981;">₹</div>
                <div>
                    <p class="dash-title">Total Collected</p>
                    <p class="dash-val">₹ {tot_fee:,}</p>
                    <p class="dash-trend" style="color:#10b981;">↑ +5% vs last month</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="dash-card" style="border-left: 5px solid #ef4444;">
                <div class="dash-icon" style="background:#fef2f2; color:#ef4444;">⚠</div>
                <div>
                    <p class="dash-title">Total Pending Due</p>
                    <p class="dash-val">₹ --</p>
                    <p class="dash-trend" style="color:#ef4444;">↓ Action Required</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.info("💡 **Tip:** Switch to the 'Fee Management' or 'Result & Admit Card' tabs from the left sidebar to manage core operations.")

    elif active_module == "💰 Fee Management":
        st.title("💰 Fee Management System")
        show_fee_management(current_m_idx)
        
    elif active_module == "📝 Result & Admit Card":
        st.title("📝 Result & Admit Card")
        show_exam_management()
        
    elif active_module == "📢 Manage Notices":
        st.title("📢 Manage Notices")
        st.subheader("Publish & Manage School Notices")
        with st.form("add_notice_form", clear_on_submit=True):
            st.write("**Post a new announcement**")
            n_title = st.text_input("Notice Title (e.g., Holiday Alert, Exam Dates)")
            n_content = st.text_area("Notice Details (Description)")
            if st.form_submit_button("🚀 Publish Notice"):
                if n_title and n_content:
                    c.execute("INSERT INTO school_notices (date, title, content, is_active) VALUES (?, ?, ?, 1)", (str(datetime.today().date()), n_title.strip(), n_content.strip()))
                    conn.commit(); st.success("✅ Notice Published!"); force_rerun()
                else: st.error("Please fill in both fields.")
        st.write("---")
        st.write("### 🗑️ Manage Old Notices")
        c.execute("SELECT id, date, title, content FROM school_notices ORDER BY id DESC")
        n_data = c.fetchall()
        if n_data:
            st.dataframe(pd.DataFrame(n_data, columns=["ID", "Date", "Title", "Content"]), use_container_width=True, hide_index=True)
            del_id = st.number_input("Enter Notice ID to Delete", min_value=0, step=1)
            if st.button("❌ Delete Notice"):
                c.execute("DELETE FROM school_notices WHERE id=?", (del_id,))
                conn.commit(); st.error(f"Notice Deleted!"); force_rerun()
                
    elif active_module == "👨‍🏫 Manage Teachers":
        st.title("👨‍🏫 Manage Teachers")
        tab1, tab2 = st.tabs(["➕ Add New Teacher", "📋 View / Delete Teachers"])
        with tab1:
            with st.form("add_teacher_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                t_name = c1.text_input("Teacher Full Name")
                t_mob = c2.text_input("Mobile Number")
                t_id = c1.text_input("Create Teacher Login ID")
                t_pass = c2.text_input("Create Password")
                if st.form_submit_button("💾 Save Teacher Details"):
                    if t_name and t_id and t_pass:
                        try:
                            c.execute("INSERT INTO teacher_master (teacher_id, name, mobile, password) VALUES (?, ?, ?, ?)", (t_id.strip(), t_name.strip(), t_mob.strip(), t_pass.strip()))
                            conn.commit(); st.success(f"✅ Teacher '{t_name}' Added Successfully!"); force_rerun()
                        except: st.error("❌ This Teacher ID already exists! Please use a different one.")
                    else: st.warning("⚠️ Name, Login ID, and Password are required fields.")
        with tab2:
            st.write("### 📋 Current Staff List")
            c.execute("SELECT id, teacher_id, name, mobile, password FROM teacher_master ORDER BY id DESC")
            t_data = c.fetchall()
            if t_data:
                df_t = pd.DataFrame(t_data, columns=["DB ID", "Teacher ID", "Teacher Name", "Mobile No", "Password"])
                st.dataframe(df_t, use_container_width=True, hide_index=True)
                with st.form("del_teacher_form"):
                    del_id = st.number_input("Enter 'DB ID' to Remove Teacher", min_value=0, step=1)
                    if st.form_submit_button("❌ Remove Teacher"):
                        c.execute("DELETE FROM teacher_master WHERE id=?", (del_id,))
                        conn.commit(); st.error(f"Teacher removed successfully."); force_rerun()
            else:
                st.info("No teachers added to the system yet.")