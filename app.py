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
# 🎨 ADAPTIVE CSS & HOVER EFFECTS (LIGHT/DARK COMPATIBLE)
# ==========================================
page_bg_css = """
<style>
/* Reset Padding */
.block-container { max-width: 1300px; padding-top: 1rem !important; padding-left: 1rem; padding-right: 1rem; }

/* Top Bar (Adapts to Theme) */
.topbar { 
    background-color: var(--secondary-background-color); 
    color: var(--text-color); 
    display: flex; justify-content: space-between; 
    padding: 10px 30px; font-size: 13px; 
    margin: -30px -5rem 0 -5rem; 
    border-bottom: 1px solid var(--border-color);
}
.topbar-left span { margin-right: 20px; display: inline-block; opacity: 0.8; font-weight: 500;}

/* Navbar Area */
.nav-links { display: flex; gap: 25px; color: var(--text-color); font-weight: 600; font-size: 15px; margin-top: 25px; justify-content: center;}
.nav-links span { cursor: pointer; transition: color 0.3s; opacity: 0.9;}
.nav-links span:hover { color: #0ea5e9; opacity: 1;}

/* Official Buttons */
div[data-testid="stButton"] button {
    background-color: var(--primary-color) !important; color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: bold !important; padding: 0.5rem 1.5rem !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important; transition: all 0.3s ease !important;
    margin-top: 15px;
}
div[data-testid="stButton"] button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 15px rgba(0,0,0,0.2) !important;
    filter: brightness(1.1);
}

/* 🌟 UNIVERSAL HOVER EFFECT (Shading & Movement) */
.hover-card {
    transition: all 0.3s ease-in-out;
    background-color: var(--secondary-background-color);
    border: 1px solid var(--border-color);
    border-radius: 12px;
}
.hover-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 25px rgba(0,0,0,0.15);
    border-color: var(--primary-color);
}

/* Hero Section */
.hero-section { padding: 30px 20px 40px 20px; text-align: left; }
.hero-welcome { color: #0ea5e9; font-weight: bold; font-size: 16px; letter-spacing: 2px; margin-bottom: 5px; text-transform: uppercase;}
.hero-title { font-size: 50px; color: var(--text-color); font-weight: 900; margin: 0; line-height: 1.1;}
.hero-subtitle { font-size: 24px; color: var(--text-color); margin: 15px 0 20px 0; font-weight: 500; opacity: 0.9;}
.hero-desc { font-size: 16px; color: var(--text-color); max-width: 650px; line-height: 1.6; margin-bottom: 25px; opacity: 0.7;}

/* Features Row */
.feature-card { text-align: left; padding: 15px; display: flex; align-items: center; gap: 15px; margin-bottom: 15px;}
.f-icon-wrap { min-width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 22px; color: white;}
.f-title { font-size: 16px; font-weight: 800; color: var(--text-color); margin: 0 0 2px 0;}
.f-text { font-size: 13px; color: var(--text-color); opacity: 0.7; margin: 0; line-height: 1.3;}

/* Side Cards (Notices & Admin) */
.side-card { padding: 25px; margin-bottom: 20px; }
.side-card-header { border-bottom: 2px solid var(--border-color); padding-bottom: 12px; margin-bottom: 20px;}
.side-card-header h3 { color: var(--text-color); margin:0; font-size: 18px; font-weight: bold;}

/* Notice Items */
.notice-item { display: flex; gap: 15px; margin-bottom: 15px; align-items: flex-start; border-bottom: 1px dashed var(--border-color); padding-bottom: 15px; transition: all 0.3s ease;}
.notice-item:hover { transform: translateX(5px); }
.notice-item:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0;}
.notice-date { background: var(--background-color); border: 1px solid var(--border-color); border-radius: 6px; padding: 6px; text-align: center; min-width: 55px;}
.nd-day { font-size: 16px; font-weight: 900; color: var(--text-color); margin:0; line-height:1;}
.nd-mon { font-size: 11px; color: #dc2626; margin:0; text-transform: uppercase; font-weight: bold;}
.nt-title { font-weight: bold; color: var(--text-color); margin: 0 0 4px 0; font-size: 14px;}
.nt-desc { font-size: 13px; color: var(--text-color); opacity:0.8; margin:0; line-height: 1.4;}

/* Admin Contact Details */
.admin-title { font-size: 15px; font-weight: 800; color: var(--text-color); opacity:0.9; margin: 0 0 5px 0; }
.admin-text { font-size: 14px; color: var(--text-color); opacity:0.8; margin: 0 0 5px 0; font-weight: 500;}
.wa-btn {
    display: inline-block; background-color: #25D366; color: white !important; font-weight: bold;
    padding: 10px 15px; border-radius: 8px; text-decoration: none; text-align: center; width: 100%;
    margin-top: 10px; transition: all 0.3s;
}
.wa-btn:hover { background-color: #128C7E; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(37, 211, 102, 0.3); }

/* Login Form Styling */
[data-testid="stForm"] {
    background-color: var(--secondary-background-color); padding: 30px; border-radius: 12px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1) !important; border: 1px solid var(--border-color); transition: transform 0.3s ease;
}
[data-testid="stForm"]:hover { transform: translateY(-3px); }
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
        
        # --- 1. TOP BAR ---
        st.markdown("""
        <div class="topbar">
            <div class="topbar-left">
                <span>📞 +91 6307210754</span>
                <span>✉️ mspslarawak@gmail.com</span>
                <span>📍 Larawak, Kachhwa, Mirzapur</span>
            </div>
            <div class="topbar-right">
                <span>f &nbsp; 📸 &nbsp; ▶ &nbsp; 𝕏</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # --- 2. LOGO, NAV & BUTTON ROW ---
        col_logo, col_nav, col_btn = st.columns([3, 5, 2])
        with col_logo:
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-top: 15px;">
                <img src='{LOGO_BASE64}' width='65' style='margin-right: 15px;'>
                <div>
                    <h2 style='margin:0; font-weight:900; font-size:24px; color: var(--text-color);'>M.S. PUBLIC SCHOOL</h2>
                    <p style='margin:0; color:#0ea5e9; font-size:12px; font-weight:bold; letter-spacing: 2px;'>LEARN | LEAD | GROW</p>
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
                
        st.markdown("<hr style='border:1px solid var(--border-color); margin: 15px 0 30px 0;'>", unsafe_allow_html=True)
                
        # --- 3. MAIN CONTENT (HERO LEFT, NOTICES RIGHT) ---
        col_main, col_space, col_side = st.columns([1.6, 0.1, 1])
        
        with col_main:
            # Hero Section with Hover Effect
            st.markdown("""
            <div class="hero-section hover-card">
                <p class="hero-welcome">WELCOME TO</p>
                <h1 class="hero-title">M.S. PUBLIC SCHOOL</h1>
                <h2 class="hero-subtitle">Building Bright Futures Through Quality Education</h2>
                <p class="hero-desc">We provide a safe, supportive and inspiring environment where every child can learn, grow and achieve their dreams under expert guidance. Our institution stands as a pillar of excellence in academics and character building.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # --- FEATURES IN TWO COLUMNS UNDER HERO ---
            f1, f2 = st.columns(2)
            features = [
                ("👨‍🏫", "#2563eb", "Qualified Teachers", "Experienced and dedicated faculty members guiding students."),
                ("📚", "#16a34a", "Modern Curriculum", "Focus on academics, moral values, and essential life skills."),
                ("🏛️", "#eab308", "Safe & Secure Campus", "A highly protective and nurturing environment for every child."),
                ("⭐", "#dc2626", "Excellent Results", "Consistent top performance and a pathway to a bright future.")
            ]
            
            for i, (icon, color, title, text) in enumerate(features):
                target_col = f1 if i % 2 == 0 else f2
                with target_col:
                    st.markdown(f"""
                    <div class="feature-card hover-card">
                        <div class="f-icon-wrap" style="background-color: {color};">{icon}</div>
                        <div>
                            <p class="f-title">{title}</p>
                            <p class="f-text">{text}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        with col_side:
            # --- NOTICE BOARD (SAFE HTML, NO INDENTATION ERROR) ---
            notices_html = '<div class="side-card hover-card" style="border-top: 4px solid #dc2626;">'
            notices_html += '<div class="side-card-header"><h3>📢 Latest News & Updates</h3></div>'
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
                            
                        notices_html += '<div class="notice-item">'
                        notices_html += f'<div class="notice-date"><p class="nd-day">{day}</p><p class="nd-mon">{mon}</p></div>'
                        notices_html += f'<div><p class="nt-title">{n[1]}</p><p class="nt-desc">{n[2]}</p></div>'
                        notices_html += '</div>'
                else:
                    notices_html += '<p style="color:#16a34a; font-weight:bold;">✨ No new notices at the moment.</p>'
            except:
                notices_html += '<p style="color:#eab308;">Notice board is currently being initialized.</p>'
            
            notices_html += '</div>'
            st.markdown(notices_html, unsafe_allow_html=True)
            
            # --- ADMINISTRATION CONTACT (SAFE HTML) ---
            admin_html = '<div class="side-card hover-card" style="border-top: 4px solid var(--primary-color);">'
            admin_html += '<div class="side-card-header"><h3>📞 Administration</h3></div>'
            admin_html += '<p class="admin-title">👨‍💼 School Manager</p>'
            admin_html += '<p class="admin-text" style="color:#0ea5e9; font-weight:bold;">Mr. Ram Prasad Patel</p>'
            admin_html += '<p class="admin-text">📞 +91 6307210754</p>'
            admin_html += '<p class="admin-text" style="margin-bottom:15px;">📞 +91 9455587731</p>'
            admin_html += '<p class="admin-title">✉️ Official Email</p>'
            admin_html += '<p class="admin-text" style="margin-bottom:15px;">mspslarawak@gmail.com</p>'
            admin_html += '<a href="https://whatsapp.com/channel/0029VbBKarY8fewxeFBwEy1A" target="_blank" class="wa-btn">🟢 Join Official WhatsApp</a>'
            admin_html += '</div>'
            st.markdown(admin_html, unsafe_allow_html=True)

        # --- FOOTER ---
        st.markdown(
            '<div style="text-align:center; margin-top:40px; padding: 20px; background-color: var(--secondary-background-color); border-top: 1px solid var(--border-color); opacity: 0.8; font-size:14px;">'
            '<p style="margin:0;">© 2026 M.S. Public School. All Rights Reserved. | Designed for Enterprise ERP System</p></div>', 
            unsafe_allow_html=True
        )

    else:
        # ==========================================
        # 🔐 BULLETPROOF LOGIN SYSTEM
        # ==========================================
        if st.button("⬅️ Back to Home"):
            st.session_state.show_login = False
            force_rerun()
            
        colA, colB, colC = st.columns([1.5, 2, 1.5])
        with colB:
            st.markdown(f"<div style='text-align: center;'><img src='{LOGO_BASE64}' width='120'></div>", unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center; color: var(--text-color); margin-bottom: 0px;'>OFFICIAL LOGIN PORTAL</h2><br>", unsafe_allow_html=True)
            
            login_type = st.radio("Select Portal Access", ["Student Portal", "Teacher Portal", "Admin Portal"], horizontal=True)
            
            with st.form("login_form"):
                if login_type == "Admin Portal":
                    st.info("👨‍💻 Secure Admin Access")
                    username = st.text_input("Admin Username / Mobile", placeholder="Enter your ID...")
                    password = st.text_input("Password", type="password", placeholder="Enter Password...")
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                    with col_btn2: submit = st.form_submit_button("Secure Login ➔", use_container_width=True)
                    if submit:
                        if username in ADMIN_USERS and password == ADMIN_USERS[username]:
                            st.session_state.logged_in = True; st.session_state.role = "Admin"; st.session_state.admin_id = username; force_rerun()
                        else: st.error("❌ Invalid Admin Credentials!")
                
                elif login_type == "Teacher Portal":
                    st.info("👨‍🏫 Teacher Dashboard Access")
                    t_id = st.text_input("Teacher ID", placeholder="Enter your Login ID...")
                    t_pass = st.text_input("Password", type="password", placeholder="Enter Password...")
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                    with col_btn2: submit = st.form_submit_button("Secure Login ➔", use_container_width=True)
                    if submit:
                        c.execute("SELECT * FROM teacher_master WHERE teacher_id=? AND password=?", (t_id.strip(), t_pass.strip()))
                        tch = c.fetchone()
                        if tch:
                            st.session_state.logged_in = True; st.session_state.role = "Teacher"; st.session_state.user_data = tch; force_rerun()
                        else: st.error("❌ Invalid Teacher ID or Password!")
                
                else:
                    st.info("🎓 Student Dashboard Access")
                    s_roll = st.number_input("Roll No", min_value=1, step=1)
                    s_dob_obj = st.date_input("Date of Birth", value=datetime(2015, 1, 1), min_value=datetime(1990, 1, 1), max_value=datetime.today())
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                    with col_btn2: submit = st.form_submit_button("View Profile ➔", use_container_width=True)
                    if submit:
                        s_dob_str = s_dob_obj.strftime("%d-%m-%Y") 
                        c.execute("SELECT * FROM student_master WHERE roll_no=? AND dob=?", (s_roll, s_dob_str))
                        stu = c.fetchone()
                        if stu:
                            st.session_state.logged_in = True; st.session_state.role = "Student"; st.session_state.user_data = stu; force_rerun()
                        else: st.error("❌ Roll No or Date of Birth is incorrect!")

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
    st.sidebar.markdown(f"<h3 style='text-align:center;'>👨‍🏫 {tch[2]}</h3>", unsafe_allow_html=True)
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
# ⚙️ ADMIN PORTAL (FULL ACCESS)
# ==========================================
elif st.session_state.role == "Admin":
    st.sidebar.markdown(f"<div style='text-align: center;'><img src='{LOGO_BASE64}' width='80'></div>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<h3 style='text-align:center;'>👨‍💻 Admin: {st.session_state.admin_id}</h3>", unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Secure Logout", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.role = None; st.session_state.admin_id = None; force_rerun()
    st.sidebar.markdown("---")
    
    st.title("🏫 M.S. Public School - Enterprise ERP")
    
    active_module = st.sidebar.radio("Select Active Module:", ["💰 Fee Management", "📝 Result & Admit Card", "📢 Manage Notices", "👨‍🏫 Manage Teachers"])
    st.sidebar.markdown("---")
    current_m_idx = get_current_m_idx()

    if active_module == "💰 Fee Management":
        show_fee_management(current_m_idx)
    elif active_module == "📝 Result & Admit Card":
        show_exam_management()
    elif active_module == "📢 Manage Notices":
        st.subheader("📢 Publish & Manage School Notices")
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
        st.subheader("👨‍🏫 Add & Manage Teaching Staff")
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