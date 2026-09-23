import streamlit as st
import hashlib
from datetime import datetime
from database import conn, c
from helpers import *

def show_landing_and_login():
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
                
        # --- MAIN CONTENT ---
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
        # --- LOGIN SCREEN ---
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
                        hashed_pass = hashlib.sha256(t_pass.strip().encode()).hexdigest()
                        c.execute("SELECT * FROM teacher_master WHERE teacher_id=? AND password=?", (t_id.strip(), hashed_pass))
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