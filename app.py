import streamlit as st
import pandas as pd
from datetime import datetime
from database import conn, c
from helpers import *
from fee_management import show_fee_management
from exam_management import show_exam_management

# Page Config (Make sure to set layout="wide")
st.set_page_config(page_title="M.S. Public School ERP", layout="wide", page_icon="🏫")

# ==========================================
# 🎨 ADAPTIVE CSS: 3D GLOW HOVER & FIXED GAPS
# ==========================================
page_bg_css = """
<style>
/* 🌟 SMART HEADER: HIDE ON LAPTOP, SHOW ONLY MENU ON MOBILE 🌟 */
#MainMenu { display: none !important; }
footer { display: none !important; }
/* Share, Deploy aur 3-dots wale faltu toolbar ko hamesha ke liye chupayein */
[data-testid="stToolbar"] { display: none !important; visibility: hidden !important; } 

/* Laptop/Desktop ke liye (Header poori tarah hide jisse clean look aaye) */
@media (min-width: 769px) {
    [data-testid="stHeader"] { display: none !important; visibility: hidden !important; }
}

/* Mobile/Tablet ke liye (Sirf transparent background taaki menu khul sake) */
@media (max-width: 768px) {
    [data-testid="stHeader"] { background-color: transparent !important; }
}

/* 🌟 UNIFIED APP BACKGROUND (Dark Blue) 🌟 */
.stApp { background-color: #0b214a !important; }
[data-testid="stSidebar"] { background-color: #0b214a !important; border-right: 1px solid rgba(255,255,255,0.1) !important; }
.block-container { max-width: 1350px; padding-top: 2rem !important; padding-left: 2rem; padding-right: 2rem; }

/* Force General Text to White */
.stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp span, .stApp label, .stApp div { color: #f8fafc; }

/* Navbar Area */
.nav-links { display: flex; gap: 30px; font-weight: 600; font-size: 16px; margin-top: 25px; justify-content: center;}
.nav-links span { cursor: pointer; transition: all 0.3s; opacity: 0.9; color: white; padding-bottom: 5px;}
.nav-links span:hover { color: #0ea5e9; opacity: 1; transform: translateY(-2px);}

/* 🌟 STANDARD BUTTONS 🌟 */
div[data-testid="stButton"] button, 
div[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(45deg, #e11d48, #be123c) !important; color: #ffffff !important; 
    border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 8px !important; 
    font-weight: 700 !important; letter-spacing: 0.5px; padding: 0.6rem 1.5rem !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important; transition: all 0.3s ease !important; margin-top: 10px; 
}
div[data-testid="stButton"] button:hover, 
div[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-4px) !important; 
    box-shadow: 0 10px 25px rgba(225, 29, 72, 0.7) !important; /* Glowing Red Shadow */
    background: linear-gradient(45deg, #be123c, #9f1239) !important; border-color: #ff4d6d !important;
}

/* 🌟 FIXED INPUT FIELDS (Black Text & Bright Cells) 🌟 */
.stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea, div[data-baseweb="select"] > div {
    background-color: #ffffff !important; 
    border: 2px solid rgba(255, 255, 255, 0.3) !important; 
    border-radius: 8px !important;
    color: #000000 !important; 
    font-weight: 800 !important; 
    box-shadow: inset 0 2px 5px rgba(0,0,0,0.1) !important;
    transition: all 0.3s ease !important;
    padding: 10px !important;
}
.stTextInput input:focus, .stNumberInput input:focus, div[data-baseweb="select"] > div:focus-within {
    border-color: #0ea5e9 !important;
    box-shadow: 0 0 15px rgba(14, 165, 233, 0.8) !important;
}
.st-emotion-cache-1104ue2, .st-emotion-cache-16idsys p { color: rgba(255,255,255,0.7) !important; }

/* 🌟 FORMS & CARDS (3D Edges & Glowing Hover) 🌟 */
[data-testid="stForm"], .content-box, .dash-card, [data-testid="stDataFrame"] {
    background-color: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 12px !important;
    padding: 30px !important;
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.4) !important; /* Base shadow */
    backdrop-filter: blur(10px);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important; /* Bouncy smooth transition */
    margin-bottom: 25px !important; /* Extra gap below cards */
}
[data-testid="stForm"]:hover, .content-box:hover, .dash-card:hover {
    transform: translateY(-8px) !important; /* Move up clearly */
    box-shadow: 0 15px 35px rgba(14, 165, 233, 0.45) !important; /* Glowing Blue Shadow */
    border-color: #0ea5e9 !important; /* Bright Blue Edge */
}
[data-testid="stForm"] { border-top: 4px solid #e11d48 !important; margin-top: 15px !important; }

/* Typography */
.hero-title { font-size: 50px; font-weight: 800; margin: 0; line-height: 1.2; color: #ffffff !important; text-shadow: 0 2px 10px rgba(0,0,0,0.5);}
.hero-subtitle { font-size: 24px; margin: 15px 0 20px 0; font-weight: 600; opacity: 0.95; color: #0ea5e9 !important;}
.side-card-header h3 { color: #ffffff !important; margin:0; font-size: 20px; font-weight: 800; border-bottom: 2px solid rgba(255,255,255,0.1); padding-bottom: 12px;}

/* Sidebar & Radio Buttons */
div[role="radiogroup"] { justify-content: center; margin-bottom: 20px; margin-top: 10px; gap: 15px; }
div[role="radiogroup"] label {
    background-color: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.2) !important;
    padding: 12px 25px !important; border-radius: 8px !important; transition: all 0.3s ease !important; cursor: pointer !important;
}
div[role="radiogroup"] label:hover { border-color: #0ea5e9 !important; box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4) !important; transform: translateY(-2px) !important; }
.main div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(45deg, #e11d48, #be123c) !important; border-color: #ff4d6d !important; transform: translateY(-4px) !important; box-shadow: 0 8px 25px rgba(225, 29, 72, 0.6) !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(45deg, #0ea5e9, #0284c7) !important; border-color: #38bdf8 !important; transform: translateX(8px) !important; box-shadow: 0 6px 20px rgba(14, 165, 233, 0.5) !important;
}
div[role="radiogroup"] label:has(input:checked) p { color: #ffffff !important; font-weight: 800 !important; letter-spacing: 0.5px;}

.stTextInput label, .stNumberInput label, .stDateInput label { font-weight: 700 !important; font-size: 15px !important; opacity: 0.9; color: #ffffff !important; margin-bottom: 5px !important;}

/* 🔥 ABSOLUTE FINAL FIX FOR DATE OF BIRTH WHITE TEXT ISSUE 🔥 */
div[data-baseweb="input"],
div[data-baseweb="input"] *,
div[data-baseweb="input"] span,
div[data-baseweb="base-input"] *,
div[data-baseweb="calendar"] *,
div[data-baseweb="calendar"] span {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}
/* 🔥 SPECIFIC FIX FOR DATE OF BIRTH TEXT 🔥 */
div[data-testid="stDateInput"] div[data-baseweb="input"] *,
div[data-testid="stDateInput"] input {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    font-weight: 900 !important;
}
div[data-baseweb="calendar"] * {
    color: #000000 !important;
}
/* 🔥 CLEAN LIGHT THEME TABLE (Halka White BG, Black Text, No Thick Border) 🔥 */
[data-testid="stDataFrame"] {
    padding: 0px !important; /* मोटा बॉर्डर/गैप हमेशा के लिए ख़त्म */
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    margin-bottom: 25px !important;
}
[data-testid="stDataFrame"] > div {
    border-radius: 8px !important;
    overflow: hidden !important;
    border: 1px solid #94a3b8 !important; /* बहुत ही पतला और क्लीन ग्रे बॉर्डर */
    box-shadow: 0 6px 15px rgba(0,0,0,0.3) !important;
    /* डार्क कैनवास को क्लीन वाइट बैकग्राउंड और ब्लैक टेक्स्ट में बदलने की ट्रिक */
    filter: invert(0.95) hue-rotate(180deg) brightness(1.05) !important;
}
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
                <img src='{LOGO_BASE64}' width='75' style='margin-right: 15px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));'>
                <div>
                    <h2 style='margin:0; font-weight:900; font-size:24px; color: #ffffff; letter-spacing: 1px;'>M.S. PUBLIC SCHOOL</h2>
                    <p style='margin:0; color:#0ea5e9; font-size:12px; font-weight:800; letter-spacing: 3px;'>LEARN | LEAD | GROW</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_nav:
            st.markdown("""
            <div class="nav-links">
                <span style="border-bottom: 3px solid #0ea5e9; padding-bottom: 3px; color: #0ea5e9;">Home</span>
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
                
        st.markdown("<hr style='border:1px solid rgba(255,255,255,0.15); margin: 25px 0 35px 0;'>", unsafe_allow_html=True)
                
        # --- MAIN CONTENT (FIXED GAP USING gap="large") ---
        col_main, col_side = st.columns([1.5, 1], gap="large")
        
        with col_main:
            st.markdown("""
            <div class="content-box">
                <p style="color: #0ea5e9; font-weight: 800; font-size: 16px; letter-spacing: 3px; margin-bottom: 5px;">WELCOME TO</p>
                <h1 class="hero-title">M.S. PUBLIC SCHOOL</h1>
                <h2 class="hero-subtitle">Building Bright Futures Through Quality Education</h2>
                <p style="font-size: 16px; opacity: 0.8; max-width: 650px; line-height: 1.7;">We provide a safe, supportive and inspiring environment where every child can learn, grow and achieve their dreams under expert guidance. Experience a modern approach to holistic development.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Sub-columns for features also use gap="large"
            f1, f2 = st.columns(2, gap="large")
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
                    <div class="content-box" style="padding: 20px; display: flex; align-items: center; gap: 15px;">
                        <div style="background-color: {color}; width: 55px; height: 55px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; flex-shrink: 0; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">{icon}</div>
                        <div>
                            <p style="font-size: 17px; font-weight: 800; margin: 0 0 4px 0; color: #ffffff;">{title}</p>
                            <p style="font-size: 14px; opacity: 0.8; margin: 0; color: #ffffff; line-height: 1.4;">{text}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        with col_side:
            notices_html = '<div class="content-box" style="border-top: 4px solid #e11d48;">'
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
                        notices_html += f'<div style="display:flex; gap:15px; border-bottom:1px dashed rgba(255,255,255,0.1); padding:15px 0; transition: transform 0.3s ease;" onmouseover="this.style.transform=\'translateX(8px)\'" onmouseout="this.style.transform=\'translateX(0)\'">'
                        notices_html += f'<div style="background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.15); border-radius:8px; padding:8px 10px; text-align:center; min-width:60px; box-shadow: inset 0 2px 5px rgba(0,0,0,0.2);"><p style="margin:0; font-weight:900; font-size:18px; color:#ffffff;">{day}</p><p style="margin:0; font-size:12px; color:#e11d48; font-weight:900; letter-spacing: 1px;">{mon}</p></div>'
                        notices_html += f'<div><p style="margin:0 0 5px 0; font-weight:800; font-size:15px; color:#ffffff;">{n[1]}</p><p style="margin:0; font-size:13px; opacity:0.8; color:#ffffff; line-height: 1.4;">{n[2]}</p></div>'
                        notices_html += '</div>'
                else:
                    notices_html += '<p style="color:#10b981; font-weight:800; font-size: 15px;">✨ No new notices at the moment.</p>'
            except:
                notices_html += '<p style="color:#eab308;">Notice board is currently being initialized.</p>'
            notices_html += '</div>'
            st.markdown(notices_html, unsafe_allow_html=True)
            
            admin_html = '<div class="content-box" style="border-top: 4px solid #0ea5e9;">'
            admin_html += '<div class="side-card-header"><h3>📞 Administration</h3></div>'
            admin_html += '<p style="font-size:15px; font-weight:800; opacity:0.9; margin:0 0 4px 0;">👨‍💼 School Manager</p>'
            admin_html += '<p style="font-size:16px; color:#0ea5e9; font-weight:800; margin:0 0 18px 0;">Mr. Ram Prasad Patel</p>'
            admin_html += '<p style="font-size:15px; font-weight:800; opacity:0.9; margin:0 0 4px 0;">📱 Contact Numbers</p>'
            admin_html += '<p style="font-size:16px; opacity:0.9; margin:0 0 18px 0; font-weight:600;">+91 6307210754 <br> +91 9455587731</p>'
            admin_html += '<p style="font-size:15px; font-weight:800; opacity:0.9; margin:0 0 4px 0;">✉️ Official Email</p>'
            admin_html += '<p style="font-size:16px; opacity:0.9; margin:0 0 20px 0; font-weight:600;">mspslarawak@gmail.com</p>'
            admin_html += '<a href="https://whatsapp.com/channel/0029VbBKarY8fewxeFBwEy1A" target="_blank" style="display: block; background: linear-gradient(45deg, #128C7E, #25D366); color: white !important; font-weight: 800; padding: 12px 15px; border-radius: 8px; text-decoration: none; text-align: center; width: 100%; box-shadow: 0 4px 15px rgba(37, 211, 102, 0.4); transition: all 0.3s;" onmouseover="this.style.transform=\'translateY(-3px)\'; this.style.boxShadow=\'0 8px 20px rgba(37, 211, 102, 0.6)\';" onmouseout="this.style.transform=\'translateY(0)\'; this.style.boxShadow=\'0 4px 15px rgba(37, 211, 102, 0.4)\';">🟢 Join Official WhatsApp</a>'
            admin_html += '</div>'
            st.markdown(admin_html, unsafe_allow_html=True)

        st.markdown(
            '<div style="text-align:center; margin-top:50px; padding: 25px; border-top: 1px solid rgba(255,255,255,0.1); opacity: 0.6; font-size:14px; font-weight:600;">'
            '<p style="margin:0;">© 2026 M.S. Public School. All Rights Reserved. | Designed for Enterprise ERP System</p></div>', 
            unsafe_allow_html=True
        )

    else:
        # ==========================================
        # 🔐 BUG-FREE PREMIUM LOGIN SCREEN
        # ==========================================
        col_back, col_space = st.columns([1, 8])
        with col_back:
            if st.button("⬅️ Home", key="back_btn"):
                st.session_state.show_login = False
                force_rerun()
                
        colA, colB, colC = st.columns([1, 1.2, 1])
        with colB:
            st.markdown("<div style='text-align: center; margin-top: 10px;'><h1 style='font-size: 60px; margin-bottom: 0px; filter: drop-shadow(0 4px 10px rgba(0,0,0,0.5));'>🎓</h1></div>", unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center; color: #ffffff; margin-top: 0px; margin-bottom: 5px; font-weight: 900; letter-spacing: 2px;'>OFFICIAL PORTAL</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 16px; font-weight: 600; margin-bottom: 15px;'>Please login to continue to your account</p>", unsafe_allow_html=True)
            
            login_type = st.radio("Select Portal Access", ["Student Portal", "Teacher Portal", "Admin Portal"], horizontal=True, label_visibility="collapsed")
            
            with st.form("login_form"):
                if login_type == "Student Portal":
                    s_roll = st.number_input("👤 Roll No", min_value=1, step=1)
                    s_dob_obj = st.date_input("📅 Date of Birth (Click Calendar Icon 👉)", value=datetime(2015, 1, 1), min_value=datetime(1990, 1, 1), max_value=datetime.today(), format="DD/MM/YYYY")
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

    st.markdown("<h2 style='margin-bottom:25px; color:#ffffff; font-weight:800;'>🎓 Student Dashboard</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["💰 Fee Details", "📝 Exam Results"])
    
    with tab1:
        pay, paid, due, adv, _ = get_student_financials(stu[0], current_m_idx)
        
        c1, c2, c3 = st.columns(3, gap="large")
        with c1:
            st.markdown(f'<div class="content-box" style="border-left: 5px solid #3b82f6; display:flex; gap:20px; align-items:center;"><div style="width:65px; height:65px; background:rgba(59, 130, 246, 0.2); color:#3b82f6; border-radius:50%; display:flex; justify-content:center; align-items:center; font-size:28px; box-shadow:0 4px 10px rgba(0,0,0,0.2);">📊</div><div><p style="margin:0; font-size:15px; font-weight:800; opacity:0.8;">Total Expected</p><p style="margin:0; font-size:30px; font-weight:900;">₹ {pay:,}</p></div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="content-box" style="border-left: 5px solid #10b981; display:flex; gap:20px; align-items:center;"><div style="width:65px; height:65px; background:rgba(16, 185, 129, 0.2); color:#10b981; border-radius:50%; display:flex; justify-content:center; align-items:center; font-size:28px; box-shadow:0 4px 10px rgba(0,0,0,0.2);">✅</div><div><p style="margin:0; font-size:15px; font-weight:800; opacity:0.8;">Total Paid</p><p style="margin:0; font-size:30px; font-weight:900;">₹ {paid:,}</p></div></div>', unsafe_allow_html=True)
        with c3:
            if due > 0:
                st.markdown(f'<div class="content-box" style="border-left: 5px solid #ef4444; display:flex; gap:20px; align-items:center;"><div style="width:65px; height:65px; background:rgba(239, 68, 68, 0.2); color:#ef4444; border-radius:50%; display:flex; justify-content:center; align-items:center; font-size:28px; box-shadow:0 4px 10px rgba(0,0,0,0.2);">⚠</div><div><p style="margin:0; font-size:15px; font-weight:800; opacity:0.8;">Current Due</p><p style="margin:0; font-size:30px; font-weight:900; color:#ff4d6d;">₹ {due:,}</p></div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="content-box" style="border-left: 5px solid #10b981; display:flex; gap:20px; align-items:center;"><div style="width:65px; height:65px; background:rgba(16, 185, 129, 0.2); color:#10b981; border-radius:50%; display:flex; justify-content:center; align-items:center; font-size:28px; box-shadow:0 4px 10px rgba(0,0,0,0.2);">🌟</div><div><p style="margin:0; font-size:15px; font-weight:800; opacity:0.8;">Advance Rcvd</p><p style="margin:0; font-size:30px; font-weight:900; color:#10b981;">₹ {adv:,}</p></div></div>', unsafe_allow_html=True)

        st.write("### 📋 Recent Payments")
        c.execute('''SELECT f.receipt_no, f.date, f.amount, f.mode, f.head FROM fee_log f WHERE f.roll_no=? ORDER BY f.date DESC''', (stu[0],))
        logs = c.fetchall()
        if logs: st.dataframe(pd.DataFrame(logs, columns=["Receipt No", "Date", "Amount", "Mode", "Fee Head"]), use_container_width=True, hide_index=True)
        else: st.warning("No payments recorded yet.")

        st.write("### 📊 Month-by-Month Statement")
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
    st.sidebar.markdown(f"<h3 style='text-align:center; color:white; font-weight:800;'>👨‍🏫 {tch[2]}</h3>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align:center; color:rgba(255,255,255,0.7); font-weight:700;'>ID: {tch[1]}</p>", unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Secure Logout", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.role = None; st.session_state.user_data = None; force_rerun()
    st.sidebar.markdown("---")
    
    st.markdown("<h2 style='margin-bottom:20px; color:#ffffff; font-weight:800;'>👨‍🏫 Teacher Dashboard</h2>", unsafe_allow_html=True)
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
    st.sidebar.markdown(f"<h3 style='text-align:center; color:white; font-weight:800;'>👨‍💻 Admin: {st.session_state.admin_id}</h3>", unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Secure Logout", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.role = None; st.session_state.admin_id = None; force_rerun()
    st.sidebar.markdown("---")
    
    active_module = st.sidebar.radio("Select Active Module:", ["📊 Dashboard", "💰 Fee Management", "📝 Result & Admit Card", "📢 Manage Notices", "👨‍🏫 Manage Teachers"])
    st.sidebar.markdown("---")
    current_m_idx = get_current_m_idx()

    if active_module == "📊 Dashboard":
        st.markdown("<h2 style='margin-bottom:0; color:#ffffff; font-weight:800;'>🏫 M.S. Public School - Enterprise ERP</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: rgba(255,255,255,0.7); font-size:16px; font-weight:600;'>Welcome to M.S. Public School Analytics Dashboard! 📈</p>", unsafe_allow_html=True)
        
        c.execute("SELECT COUNT(*) FROM student_master")
        tot_stu = c.fetchone()[0] or 0
        
        c.execute("SELECT SUM(amount) FROM fee_log")
        tot_fee = c.fetchone()[0] or 0
        
        # 🔥 CALCULATE TOTAL PENDING DUE DYNAMICALLY 🔥
        c.execute("SELECT roll_no FROM student_master")
        all_students = c.fetchall()
        tot_expected = sum([get_student_financials(s[0], current_m_idx)[0] for s in all_students]) if all_students else 0
        tot_pending = max(0, tot_expected - tot_fee)
        
        m1, m2, m3 = st.columns(3, gap="large")
        with m1:
            st.markdown(f'<div class="content-box" style="border-left: 5px solid #3b82f6; display:flex; gap:20px; align-items:center;"><div style="width:65px; height:65px; background:rgba(59, 130, 246, 0.2); color:#3b82f6; border-radius:50%; display:flex; justify-content:center; align-items:center; font-size:28px; box-shadow:0 4px 10px rgba(0,0,0,0.2);">👥</div><div><p style="margin:0; font-size:15px; font-weight:800; opacity:0.8;">Total Students</p><p style="margin:0; font-size:30px; font-weight:900;">{tot_stu}</p><p style="margin:5px 0 0 0; font-size:13px; font-weight:800; color:#10b981;">↑ Updated Live</p></div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="content-box" style="border-left: 5px solid #10b981; display:flex; gap:20px; align-items:center;"><div style="width:65px; height:65px; background:rgba(16, 185, 129, 0.2); color:#10b981; border-radius:50%; display:flex; justify-content:center; align-items:center; font-size:28px; box-shadow:0 4px 10px rgba(0,0,0,0.2);">₹</div><div><p style="margin:0; font-size:15px; font-weight:800; opacity:0.8;">Total Collected</p><p style="margin:0; font-size:30px; font-weight:900;">₹ {tot_fee:,}</p><p style="margin:5px 0 0 0; font-size:13px; font-weight:800; color:#10b981;">↑ Updated Live</p></div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="content-box" style="border-left: 5px solid #ef4444; display:flex; gap:20px; align-items:center;"><div style="width:65px; height:65px; background:rgba(239, 68, 68, 0.2); color:#ef4444; border-radius:50%; display:flex; justify-content:center; align-items:center; font-size:28px; box-shadow:0 4px 10px rgba(0,0,0,0.2);">⚠</div><div><p style="margin:0; font-size:15px; font-weight:800; opacity:0.8;">Total Pending Due</p><p style="margin:0; font-size:30px; font-weight:900;">₹ {tot_pending:,}</p><p style="margin:5px 0 0 0; font-size:13px; font-weight:800; color:#ef4444;">↓ Action Required</p></div></div>', unsafe_allow_html=True)
            
        st.info("💡 **Tip:** Switch to the 'Fee Management' or 'Result & Admit Card' tabs from the left sidebar to manage core operations.")
        with m1:
            st.markdown(f'<div class="content-box" style="border-left: 5px solid #3b82f6; display:flex; gap:20px; align-items:center;"><div style="width:65px; height:65px; background:rgba(59, 130, 246, 0.2); color:#3b82f6; border-radius:50%; display:flex; justify-content:center; align-items:center; font-size:28px; box-shadow:0 4px 10px rgba(0,0,0,0.2);">👥</div><div><p style="margin:0; font-size:15px; font-weight:800; opacity:0.8;">Total Students</p><p style="margin:0; font-size:30px; font-weight:900;">{tot_stu}</p><p style="margin:5px 0 0 0; font-size:13px; font-weight:800; color:#10b981;">↑ Updated Live</p></div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="content-box" style="border-left: 5px solid #10b981; display:flex; gap:20px; align-items:center;"><div style="width:65px; height:65px; background:rgba(16, 185, 129, 0.2); color:#10b981; border-radius:50%; display:flex; justify-content:center; align-items:center; font-size:28px; box-shadow:0 4px 10px rgba(0,0,0,0.2);">₹</div><div><p style="margin:0; font-size:15px; font-weight:800; opacity:0.8;">Total Collected</p><p style="margin:0; font-size:30px; font-weight:900;">₹ {tot_fee:,}</p><p style="margin:5px 0 0 0; font-size:13px; font-weight:800; color:#10b981;">↑ Updated Live</p></div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="content-box" style="border-left: 5px solid #ef4444; display:flex; gap:20px; align-items:center;"><div style="width:65px; height:65px; background:rgba(239, 68, 68, 0.2); color:#ef4444; border-radius:50%; display:flex; justify-content:center; align-items:center; font-size:28px; box-shadow:0 4px 10px rgba(0,0,0,0.2);">⚠</div><div><p style="margin:0; font-size:15px; font-weight:800; opacity:0.8;">Total Pending Due</p><p style="margin:0; font-size:30px; font-weight:900;">₹ --</p><p style="margin:5px 0 0 0; font-size:13px; font-weight:800; color:#ef4444;">↓ Action Required</p></div></div>', unsafe_allow_html=True)
            
        st.info("💡 **Tip:** Switch to the 'Fee Management' or 'Result & Admit Card' tabs from the left sidebar to manage core operations.")

    elif active_module == "💰 Fee Management":
        st.markdown("<h2 style='color:#ffffff; font-weight:800;'>💰 Fee Management System</h2>", unsafe_allow_html=True)
        show_fee_management(current_m_idx)
        
    elif active_module == "📝 Result & Admit Card":
        st.markdown("<h2 style='color:#ffffff; font-weight:800;'>📝 Result & Admit Card</h2>", unsafe_allow_html=True)
        show_exam_management()
        
    elif active_module == "📢 Manage Notices":
        st.markdown("<h2 style='color:#ffffff; font-weight:800;'>📢 Manage Notices</h2>", unsafe_allow_html=True)
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
        st.markdown("<h2 style='color:#ffffff; font-weight:800;'>👨‍🏫 Add & Manage Teaching Staff</h2>", unsafe_allow_html=True)
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