import streamlit as st
import pandas as pd
from database import c
from helpers import *

def show_student_portal():
    stu = st.session_state.user_data
    current_m_idx = get_current_m_idx()
    
    # 🌟 Added spacer to prevent logo colliding with Menu Button
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
        c.execute("SELECT item_name, amount, date FROM student_charges WHERE roll_no=?", (stu[0],))
        for item in c.fetchall(): heads.append((f"{item[0]} (EXTRA)", item[1], get_m_idx_for_date(item[2])))
        heads.extend([('April Tuition', fs[3], 1), ('May Tuition', fs[3], 2), ('June Tuition', fs[3], 3), ('July Tuition', fs[3], 4), ('Quarterly Exam', fs[4], 4), ('August Tuition', fs[3], 5), ('September Tuition', fs[3], 6), ('October Tuition', fs[3], 7), ('Half-Yearly Exam', fs[5], 7), ('November Tuition', fs[3], 8), ('December Tuition', fs[3], 9), ('January Tuition', fs[3], 10), ('February Tuition', fs[3], 11), ('March Tuition', fs[3], 12), ('Yearly Exam', fs[6], 12)])
        heads.sort(key=lambda h: h[2]) 
        
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