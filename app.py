import streamlit as st
import pandas as pd
from datetime import datetime
from database import conn, c
from helpers import *
from fee_management import show_fee_management
from exam_management import show_exam_management

st.set_page_config(page_title="M.S. Public School ERP", layout="wide", page_icon="🏫")

# ==========================================
# 🎨 PREMIUM CSS & GLOWING EFFECTS
# ==========================================
page_bg_css = """
<style>
/* Button Styling */
div[data-testid="stButton"] button {
    background-color: #1F497D !important; color: #ffffff !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important; padding: 0.5rem 1.5rem !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important; transition: all 0.3s ease !important;
}
div[data-testid="stButton"] button:hover {
    background-color: #ff4b4b !important; transform: translateY(-3px) !important;
    box-shadow: 0 8px 15px rgba(255, 75, 75, 0.4) !important;
}

/* WhatsApp Custom Button */
.wa-btn {
    display: inline-block; background-color: #25D366; color: white !important; font-weight: bold;
    padding: 10px 20px; border-radius: 8px; text-decoration: none; text-align: center; width: 100%;
    box-shadow: 0 4px 6px rgba(37, 211, 102, 0.3); transition: all 0.3s ease; margin-bottom: 10px;
}
.wa-btn:hover { background-color: #128C7E; transform: translateY(-3px); box-shadow: 0 6px 12px rgba(37, 211, 102, 0.4); }

/* Sidebar Tabs */
[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display: none !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label {
    background-color: transparent !important; border: 1px solid rgba(128, 128, 128, 0.3) !important;
    padding: 10px 15px !important; margin-bottom: 8px !important; border-radius: 8px !important;
    width: 100% !important; transition: all 0.3s ease !important; display: block !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background-color: rgba(255, 75, 75, 0.1) !important; border-color: #ff4b4b !important; transform: translateX(5px) !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background-color: #1F497D !important; border-color: #1F497D !important; transform: translateX(8px) !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p { color: #ffffff !important; font-weight: 800 !important; }

/* 🌟 GLOWING ANIMATED HERO BANNER 🌟 */
.glowing-wrapper {
    position: relative;
    z-index: 0;
    margin-bottom: 40px;
    margin-top: 10px;
    border-radius: 15px;
}
.glowing-wrapper:before {
    content: '';
    background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000);
    position: absolute;
    top: -3px; left: -3px;
    background-size: 400%;
    z-index: -1;
    filter: blur(8px);
    width: calc(100% + 6px);
    height: calc(100% + 6px);
    animation: glowing 20s linear infinite;
    opacity: 0.8;
    border-radius: 15px;
}
.hero-inner {
    background: linear-gradient(135deg, #183e6b, #2a5d91);
    border-radius: 14px;
    padding: 30px 20px;
    text-align: center;
    color: white;
    border: 1px solid rgba(255,255,255,0.1);
}
@keyframes glowing {
    0% { background-position: 0 0; }
    50% { background-position: 400% 0; }
    100% { background-position: 0 0; }
}

/* Notice & Contact Cards */
.modern-card {
    background-color: #ffffff; padding: 20px; margin-bottom: 15px; 
    border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    border: 1px solid #eee; transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.modern-card:hover { 
    transform: translateY(-3px); 
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}
.notice-border { border-left: 5px solid #ff4b4b; }
.admin-border { border-top: 4px solid #1F497D; }

/* Hide Streamlit Header elements slightly */
header {visibility: hidden;}
#MainMenu {visibility: hidden;}
</style>
"""
st.markdown(page_bg_css, unsafe_allow_html=True)

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
        
        # --- 1. TOP NAVBAR ---
        col_logo, col_space, col_btn = st.columns([1, 7, 1.2])
        with col_logo:
            st.markdown(f"<img src='{LOGO_BASE64}' width='80' style='margin-top:-25px;'>", unsafe_allow_html=True)
        with col_btn:
            if st.button("Sign In ➔", use_container_width=True):
                st.session_state.show_login = True
                force_rerun()
                
        # --- 2. GLOWING HERO BANNER ---
        st.markdown("""
        <div class="glowing-wrapper">
            <div class="hero-inner">
                <h1 style='font-size: 50px; margin: 0; font-weight: 900; letter-spacing: 2px; text-shadow: 2px 2px 4px rgba(0,0,0,0.4);'>M.S. PUBLIC SCHOOL</h1>
                <p style='margin: 10px 0 0 0; font-weight: 400; opacity: 0.9; font-size: 20px;'>Learn. Lead. Grow. | Welcome to our Official Portal.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # --- 3. NOTICE BOARD & CONTACT INFO ---
        col_notices, col_space, col_contact = st.columns([2.2, 0.1, 1.2])
        
        with col_notices:
            st.markdown("<h3 style='color:#1F497D;'>📢 Latest Notices & Updates</h3>", unsafe_allow_html=True)
            
            try:
                c.execute("SELECT n.date, n.title, n.content FROM school_notices n WHERE n.is_active=1 ORDER BY n.id DESC")
                notices = c.fetchall()
                if notices:
                    for n in notices:
                        st.markdown(f"""
                        <div class="modern-card notice-border">
                            <h4 style='color: #1F497D; margin-top: 0; margin-bottom: 8px;'>🗓️ {n[0]} | {n[1]}</h4>
                            <p style='color: #444; margin-bottom: 0; font-size: 15px; line-height: 1.5;'>{n[2]}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""<div class="modern-card" style="border-left: 5px solid #28a745;"><p style="margin:0; color:#28a745; font-weight:bold;">✨ No new notices at the moment. Have a great day!</p></div>""", unsafe_allow_html=True)
            except:
                st.warning("Notice board is currently being initialized.")

        with col_contact:
            st.markdown("<h3 style='color:#1F497D;'>📞 Administration</h3>", unsafe_allow_html=True)
            
            st.markdown("""
            <div class="modern-card admin-border">
                <h4 style='margin:0 0 10px 0; color:#1F497D;'>👨‍💼 School Manager</h4>
                <p style='margin:0 0 5px 0; font-weight:bold;'>Mr. Ram Prasad Patel</p>
                <p style='margin:0 0 5px 0; color:#555;'>📞 +91 6307210754</p>
                <p style='margin:0 0 15px 0; color:#555;'>📞 +91 9455587731</p>
                
                <h4 style='margin:0 0 10px 0; color:#1F497D;'>✉️ Email Us</h4>
                <p style='margin:0 0 15px 0; color:#555;'>mspslarawak@gmail.com</p>
                
                <a href="https://whatsapp.com/channel/0029VbBKarY8fewxeFBwEy1A" target="_blank" class="wa-btn">
                    🟢 Join WhatsApp Channel
                </a>
            </div>
            """, unsafe_allow_html=True)

        # --- 4. FOOTER ---
        st.markdown("""
        <div style='text-align: center; margin-top: 40px; padding-top: 15px; border-top: 1px solid #eee; color: #aaa; font-size: 14px;'>
            <p>© 2026 M.S. Public School. All Rights Reserved. | Designed with ❤️</p>
        </div>
        """, unsafe_allow_html=True)

    else:
        if st.button("⬅️ Back to Home"):
            st.session_state.show_login = False
            force_rerun()
            
        colA, colB, colC = st.columns([1.5, 2, 1.5])
        with colB:
            st.markdown(f"<div style='text-align: center;'><img src='{LOGO_BASE64}' width='140'></div>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>PORTAL LOGIN</h1><br>", unsafe_allow_html=True)
            
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