import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
from database import conn, c
from helpers import *
from fee_management import show_fee_management
from exam_management import show_exam_management

def show_admin_portal():
    # 🌟 Added spacer to prevent logo colliding with Menu Button
    st.sidebar.markdown(f"<div style='text-align: center;'><img src='{LOGO_BASE64}' width='90'></div>", unsafe_allow_html=True)
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
                            hashed_pass = hashlib.sha256(t_pass.strip().encode()).hexdigest()
                            c.execute("INSERT INTO teacher_master (teacher_id, name, mobile, password) VALUES (?, ?, ?, ?)", (t_id.strip(), t_name.strip(), t_mob.strip(), hashed_pass))
                            conn.commit(); st.success(f"✅ Teacher '{t_name}' Added Successfully!"); force_rerun()
                        except: st.error("❌ This Teacher ID already exists! Please use a different one.")
                    else: st.warning("⚠️ Name, Login ID, and Password are required fields.")
        with tab2:
            st.write("### 📋 Current Staff List")
            c.execute("SELECT id, teacher_id, name, mobile, password FROM teacher_master ORDER BY id DESC")
            t_data = c.fetchall()
            if t_data:
                safe_t_data = [[t[0], t[1], t[2], t[3], "********"] for t in t_data]
                df_t = pd.DataFrame(safe_t_data, columns=["DB ID", "Teacher ID", "Teacher Name", "Mobile No", "Password"])
                st.dataframe(df_t, use_container_width=True, hide_index=True)
                with st.form("del_teacher_form"):
                    del_id = st.number_input("Enter 'DB ID' to Remove Teacher", min_value=0, step=1)
                    if st.form_submit_button("❌ Remove Teacher"):
                        c.execute("DELETE FROM teacher_master WHERE id=?", (del_id,))
                        conn.commit(); st.error(f"Teacher removed successfully."); force_rerun()
            else:
                st.info("No teachers added to the system yet.")