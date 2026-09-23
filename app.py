import streamlit as st
from css_config import apply_custom_css
from landing_login import show_landing_and_login
from student_portal import show_student_portal
from teacher_portal import show_teacher_portal
from admin_portal import show_admin_portal

# ⚙️ Page Config MUST be the very first Streamlit command
st.set_page_config(page_title="M.S. Public School ERP", layout="wide", page_icon="🏫", initial_sidebar_state="expanded")

# 🎨 Apply our modular CSS (Includes the fixed Native Menu!)
apply_custom_css()

# 🔄 INITIALIZE SESSION STATE
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_data = None
    st.session_state.admin_id = None
    st.session_state.show_login = False

# 🚦 ROUTING LOGIC (Directing users to correct file)
if not st.session_state.logged_in:
    show_landing_and_login()
elif st.session_state.role == "Student":
    show_student_portal()
elif st.session_state.role == "Teacher":
    show_teacher_portal()
elif st.session_state.role == "Admin":
    show_admin_portal()