import streamlit as st
from helpers import *
from fee_management import show_fee_management
from exam_management import show_exam_management

def show_teacher_portal():
    tch = st.session_state.user_data
    
    # 🌟 Added spacer to prevent logo colliding with Menu Button
    st.sidebar.markdown(f"<div style='text-align: center;'><img src='{LOGO_BASE64}' width='90'></div>", unsafe_allow_html=True)
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