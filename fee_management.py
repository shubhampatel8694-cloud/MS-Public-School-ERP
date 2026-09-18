import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components
import plotly.express as px
from database import conn, c, c_list
from helpers import *

def show_fee_management(current_m_idx):
    
    role = st.session_state.get('role')
    
    # 👇 TEACHER KO SIRF STATEMENTS & PRINT RECEIPT DIKHEGA
    if role == 'Teacher':
        menu = st.sidebar.radio("Teacher Fee Menu", ["🔍 Student Statement", "📈 Class Statement", "🖨️ Print Receipts"])
    else:
        menu = st.sidebar.radio("Fee Menu", ["📊 Dashboard", "⚙️ Setup Fee Structure", "👥 Student Master", "🎒 Assign Extra Items", "📝 Fee Collection & Print", "🔍 Student Statement", "📈 Class Statement", "📅 Daily Collection"])
    
    if menu == "📊 Dashboard":
        st.subheader("Welcome to M.S. Public School Analytics Dashboard! 📈")
        c.execute("SELECT SUM(amount) FROM fee_log")
        tot_col = c.fetchone()[0] or 0
        c.execute("SELECT roll_no FROM student_master")
        all_students = c.fetchall()
        tot_expected = sum([get_student_financials(s[0], current_m_idx)[0] for s in all_students])
        tot_pending = max(0, tot_expected - tot_col)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("👥 Total Students", f"{len(all_students)}")
        c2.metric("🟢 Total Collected", f"₹ {tot_col:,}")
        c3.metric("🔴 Total Pending Due", f"₹ {tot_pending:,}")
        
        st.markdown("---")
        colA, colB = st.columns(2)
        with colA:
            st.markdown("#### 💰 Fee Collection Status")
            pie_data = pd.DataFrame({'Status': ['Collected', 'Pending Due'], 'Amount': [tot_col, tot_pending]})
            if tot_col > 0 or tot_pending > 0:
                fig_pie = px.pie(pie_data, values='Amount', names='Status', hole=0.5, color='Status', color_discrete_map={'Collected':'#28a745', 'Pending Due':'#dc3545'})
                fig_pie.update_layout(margin=dict(t=20, b=20, l=0, r=0))
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No fee data available yet.")
                
        with colB:
            st.markdown("#### 📈 Last 7 Days Collection Trend")
            c.execute('''SELECT date, SUM(amount) as daily_total FROM fee_log GROUP BY date ORDER BY date DESC LIMIT 7''')
            trend_data = c.fetchall()
            if trend_data:
                df_trend = pd.DataFrame(trend_data, columns=['Date', 'Amount'])
                df_trend['Date'] = pd.to_datetime(df_trend['Date'])
                df_trend = df_trend.sort_values('Date')
                fig_line = px.line(df_trend, x='Date', y='Amount', markers=True, text='Amount', color_discrete_sequence=['#1F497D'])
                fig_line.update_traces(textposition="top center")
                fig_line.update_layout(margin=dict(t=20, b=20, l=0, r=0), yaxis_title="Amount (₹)", xaxis_title="")
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("No recent collections to show trend.")
                
        st.markdown("---")
        st.markdown("#### 📊 Class-wise Revenue Generation")
        c.execute('''SELECT s.class, SUM(f.amount) FROM fee_log f JOIN student_master s ON f.roll_no = s.roll_no GROUP BY s.class''')
        cls_col_data = c.fetchall()
        if cls_col_data:
            df_cls = pd.DataFrame(cls_col_data, columns=['Class', 'Collected Amount'])
            df_cls['Class'] = pd.Categorical(df_cls['Class'], categories=c_list, ordered=True)
            df_cls = df_cls.sort_values('Class')
            fig_bar = px.bar(df_cls, x='Class', y='Collected Amount', text='Collected Amount', color='Collected Amount', color_continuous_scale='Blues')
            fig_bar.update_traces(texttemplate='₹ %{text:.2s}', textposition='outside')
            fig_bar.update_layout(margin=dict(t=20, b=20, l=0, r=0), xaxis_title="Classes", yaxis_title="Total Collected (₹)")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No class-wise collection data available yet.")

    elif menu == "⚙️ Setup Fee Structure":
        st.subheader("Update Class-wise Base Fees")
        df_fees = pd.read_sql_query("SELECT * FROM fee_structure", conn)
        st.dataframe(df_fees, use_container_width=True, hide_index=True)
        with st.form("update_fee"):
            col1, col2, col3, col4 = st.columns(4)
            edit_cls = col1.selectbox("Select Class", df_fees['class'].tolist())
            c.execute("SELECT * FROM fee_structure WHERE class=?", (edit_cls,))
            f_data = c.fetchone()
            n_reg = col2.number_input("Reg Fee", value=f_data[1]); n_adm = col3.number_input("Admission Fee", value=f_data[2])
            n_tui = col4.number_input("Monthly Tuition", value=f_data[3]); n_qex = col1.number_input("Quarterly Exam", value=f_data[4])
            n_hex = col2.number_input("Half-Yearly Exam", value=f_data[5]); n_yex = col3.number_input("Yearly Exam", value=f_data[6])
            n_van = col4.number_input("Monthly Van Fee", value=f_data[7]); n_eng = col1.number_input("English Medium Extra", value=f_data[8])
            n_oth = col2.number_input("Other Annual Fee", value=f_data[9])
            if st.form_submit_button("Update Fees"):
                c.execute("UPDATE fee_structure SET reg_fee=?, adm_fee=?, tuition=?, q_exam=?, h_exam=?, y_exam=?, van_fee=?, eng_fee=?, other_fee=? WHERE class=?", 
                          (n_reg, n_adm, n_tui, n_qex, n_hex, n_yex, n_van, n_eng, n_oth, edit_cls))
                conn.commit(); st.success("✅ Fees Updated!"); force_rerun()

    elif menu == "👥 Student Master":
        st.subheader("Student Database Management")
        tab1, tab2 = st.tabs(["➕ Add New Student", "✏️ Edit Existing Student"])
        with tab1:
            with st.form("student_form", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                roll_no = col1.number_input("Roll No", min_value=1, step=1)
                sch_no = col2.text_input("Scholar No (SCH NO)")
                dob_obj = col3.date_input("Date of Birth", value=datetime(2015, 1, 1), min_value=datetime(1990, 1, 1), max_value=datetime.today())
                name = col1.text_input("Student Name")
                father = col2.text_input("Father's Name")
                mother = col3.text_input("Mother's Name")
                cls = col1.selectbox("Class", c_list)
                transport = col2.radio("Transport Mode", ["Self", "Van"], horizontal=True)
                medium = col3.radio("Medium", ["HINDI", "ENGLISH"], horizontal=True)
                if st.form_submit_button("Save Student"):
                    try:
                        dob_str = dob_obj.strftime("%d-%m-%Y")
                        c.execute("INSERT INTO student_master (roll_no, name, class, father_name, transport, medium, mother_name, dob, sch_no) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                  (roll_no, name.upper().strip(), cls, father.upper().strip(), transport, medium, mother.upper().strip(), dob_str, sch_no.upper().strip()))
                        conn.commit(); st.success("✅ Student Added!"); force_rerun()
                    except: st.error("❌ Roll No already exists!")
        with tab2:
            edit_roll = st.number_input("Enter Roll No to Edit", min_value=1, step=1)
            c.execute("SELECT roll_no, name, class, father_name, transport, medium, mother_name, dob, sch_no FROM student_master WHERE roll_no=?", (edit_roll,))
            stu_edit = c.fetchone()
            if stu_edit:
                with st.form("edit_stu_form"):
                    col1, col2, col3 = st.columns(3)
                    e_sch = col1.text_input("Scholar No", value=stu_edit[8])
                    e_dob = col2.text_input("DOB (DD-MM-YYYY)", value=stu_edit[7])
                    e_name = col3.text_input("Student Name", value=stu_edit[1])
                    e_father = col1.text_input("Father's Name", value=stu_edit[3])
                    e_mother = col2.text_input("Mother's Name", value=stu_edit[6])
                    e_cls = col3.selectbox("Class", c_list, index=c_list.index(stu_edit[2]))
                    e_trans = col1.radio("Transport", ["Self", "Van"], index=0 if stu_edit[4]=="Self" else 1, horizontal=True)
                    e_med = col2.radio("Medium", ["HINDI", "ENGLISH"], index=0 if stu_edit[5]=="HINDI" else 1, horizontal=True)
                    if st.form_submit_button("Update Details"):
                        c.execute("UPDATE student_master SET name=?, class=?, father_name=?, transport=?, medium=?, mother_name=?, dob=?, sch_no=? WHERE roll_no=?", 
                                  (e_name.upper().strip(), e_cls, e_father.upper().strip(), e_trans, e_med, e_mother.upper().strip(), e_dob, e_sch.upper().strip(), edit_roll))
                        conn.commit(); st.success("Updated!"); force_rerun()
        st.write("---")
        st.dataframe(pd.read_sql_query("SELECT roll_no, sch_no, name, class, father_name, mother_name, dob FROM student_master ORDER BY class, roll_no", conn), use_container_width=True, hide_index=True)

    elif menu == "🎒 Assign Extra Items":
        st.subheader("Manage Extra Items & Charges")
        tab1, tab2, tab3, tab4 = st.tabs(["👤 Assign Individual", "🏫 Assign to Class", "✏️ Edit Individual", "🗑️ Batch Delete (Class)"])
        with tab1:
            with st.form("item_form", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                r_no = col1.number_input("Roll No", min_value=1, step=1)
                item_name = col2.text_input("Item Name")
                item_amt = col3.number_input("Amount (₹)", min_value=1, step=10)
                if st.form_submit_button("Assign Charge"):
                    c.execute("SELECT name FROM student_master WHERE roll_no=?", (r_no,))
                    if c.fetchone():
                        c.execute("INSERT INTO student_charges (roll_no, item_name, amount, date) VALUES (?, ?, ?, ?)", (r_no, item_name.upper().strip(), item_amt, str(datetime.today().date())))
                        conn.commit(); st.success("✅ Added Successfully!"); force_rerun()
                    else: st.error("❌ Student not found!")
        with tab2:
            cls_name = st.selectbox("Select Class", c_list, key="cls_assign")
            c.execute("SELECT COUNT(*) FROM student_master WHERE class=?", (cls_name,))
            stu_count = c.fetchone()[0]
            st.info(f"👥 Students in Class {cls_name}: **{stu_count}**")
            with st.form("class_item_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                cls_item_name = col1.text_input("Item Name")
                cls_item_amt = col2.number_input("Amount (₹)", min_value=1, step=10)
                if st.form_submit_button("Assign to Entire Class"):
                    if stu_count > 0 and cls_item_name.strip():
                        c.execute("SELECT roll_no FROM student_master WHERE class=?", (cls_name,))
                        for stu in c.fetchall():
                            c.execute("INSERT INTO student_charges (roll_no, item_name, amount, date) VALUES (?, ?, ?, ?)", (stu[0], cls_item_name.upper().strip(), cls_item_amt, str(datetime.today().date())))
                        conn.commit(); st.success("✅ Added to Class Successfully!"); force_rerun()
        with tab3:
            df_charges = pd.read_sql_query("SELECT c.id as ID, c.roll_no as Roll_No, s.name as Student_Name, s.class as Class, c.item_name as Item_Name, c.amount as Amount FROM student_charges c JOIN student_master s ON c.roll_no = s.roll_no ORDER BY c.id DESC LIMIT 30", conn)
            st.dataframe(df_charges, use_container_width=True, hide_index=True)
            edit_id = st.number_input("Enter ID from above to Edit/Delete", min_value=1, step=1)
            c.execute("SELECT * FROM student_charges WHERE id=?", (edit_id,))
            chg = c.fetchone()
            if chg:
                with st.form("edit_charge_form"):
                    col1, col2, col3 = st.columns(3)
                    e_r_no = col1.number_input("Roll No", value=chg[1], step=1)
                    e_i_name = col2.text_input("Item Name", value=chg[2])
                    e_amt = col3.number_input("Amount (₹)", value=chg[3], step=10)
                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("✅ Update"):
                        c.execute("UPDATE student_charges SET roll_no=?, item_name=?, amount=? WHERE id=?", (e_r_no, e_i_name.upper().strip(), e_amt, edit_id))
                        conn.commit(); st.success("Updated!"); force_rerun()
                    if c2.form_submit_button("❌ Delete"):
                        c.execute("DELETE FROM student_charges WHERE id=?", (edit_id,))
                        conn.commit(); st.error("Deleted!"); force_rerun()
        with tab4:
            del_cls = st.selectbox("Select Class to Clean", c_list, key="del_cls")
            c.execute("SELECT DISTINCT c.item_name FROM student_charges c JOIN student_master s ON c.roll_no = s.roll_no WHERE s.class = ?", (del_cls,))
            existing_items = [x[0] for x in c.fetchall()]
            if existing_items:
                with st.form("batch_del_form"):
                    del_item = st.selectbox("Select Charge to Delete", existing_items)
                    if st.form_submit_button("❌ Delete this charge from entire class"):
                        c.execute("SELECT roll_no FROM student_master WHERE class=?", (del_cls,))
                        rolls = [str(r[0]) for r in c.fetchall()]
                        if rolls:
                            c.execute(f"DELETE FROM student_charges WHERE item_name=? AND roll_no IN ({','.join(rolls)})", (del_item,))
                            conn.commit(); st.success("Deleted!"); force_rerun()
            else: st.info("No charges found.")

    # 👇 COMBINED FEE COLLECTION & PRINTING TAB (RBAC ENABLED)
    elif menu in ["📝 Fee Collection & Print", "🖨️ Print Receipts"]:
        if 'receipt_to_print' not in st.session_state: st.session_state.receipt_to_print = None
        
        if role == 'Teacher':
            st.subheader("🖨️ View & Print Receipts")
        else:
            st.subheader("Fee Receipts & Printing")

        if st.session_state.receipt_to_print:
            rec_no = st.session_state.receipt_to_print
            c.execute('''SELECT f.receipt_no, f.date, f.roll_no, s.name, s.class, f.head, f.amount, f.mode, s.father_name, s.medium, s.transport FROM fee_log f LEFT JOIN student_master s ON f.roll_no = s.roll_no WHERE f.receipt_no=?''', (rec_no,))
            r = c.fetchone()
            if r:
                st.markdown("### 🖨️ A5 Receipt Print View")
                if st.button("❌ Close Receipt & Go Back"):
                    st.session_state.receipt_to_print = None; force_rerun()
                rec_no, rec_date, roll, name, cls, fee_head_note, amt_paid, mode, fname, medium, transport = r
                name, cls, fname = name or "N/A", cls or "N/A", fname or "N/A"
                c.execute("SELECT amount, receipt_no FROM fee_log WHERE roll_no=? ORDER BY date ASC, receipt_no ASC", (roll,))
                prev_paid = sum([row[0] for row in c.fetchall() if row[1] != rec_no])
                new_total_paid = prev_paid + amt_paid
                c.execute("SELECT * FROM fee_structure WHERE class=?", (cls,))
                fs = c.fetchone()
                heads = [('Registration Fee', fs[1], 1), ('Admission Fee', fs[2], 1), ('Other Fee', fs[9], 1)]
                c.execute("SELECT item_name, amount FROM student_charges WHERE roll_no=?", (roll,))
                for item in c.fetchall(): heads.append((f"{item[0]} (EXTRA)", item[1], 1))
                heads.extend([('April Tuition', fs[3], 1), ('May Tuition', fs[3], 2), ('June Tuition', fs[3], 3), ('July Tuition', fs[3], 4), ('Quarterly Exam', fs[4], 4), ('August Tuition', fs[3], 5), ('September Tuition', fs[3], 6), ('October Tuition', fs[3], 7), ('Half-Yearly Exam', fs[5], 7), ('November Tuition', fs[3], 8), ('December Tuition', fs[3], 9), ('January Tuition', fs[3], 10), ('February Tuition', fs[3], 11), ('March Tuition', fs[3], 12), ('Yearly Exam', fs[6], 12)])
                
                allocation_rows_html, cum_payable_prev = "", 0
                for h_name, base_amt, m_idx in heads:
                    head_payable = base_amt
                    if "Tuition" in h_name:
                        if transport == "Van": head_payable += fs[7]
                        if medium == "ENGLISH": head_payable += fs[8]
                    prev_paid_head = min(head_payable, max(0, prev_paid - cum_payable_prev))
                    new_paid_head = min(head_payable, max(0, new_total_paid - cum_payable_prev))
                    allocated = new_paid_head - prev_paid_head
                    alloc_str = f"<b style='color:#006100;'>₹ {int(allocated):,}</b>" if allocated > 0 else "<span style='color:#ccc;'>-</span>"
                    allocation_rows_html += f"<tr><td style='border: 1px solid black; padding: 1px 5px;'>{h_name.upper()}</td><td style='border: 1px solid black; padding: 1px 5px; text-align: center;'>₹ {head_payable:,}</td><td style='border: 1px solid black; padding: 1px 5px; text-align: center;'>{alloc_str}</td></tr>"
                    cum_payable_prev += head_payable
                    
                pay, paid, due, adv, _ = get_student_financials(roll, get_current_m_idx())
                html_code = f"""<html><head><style>body {{ font-family: 'Calibri', Arial, sans-serif; font-size: 11px; color: black; background: #fff; padding: 10px; margin: 0; }} table {{ width: 100%; border-collapse: collapse; }} td {{ padding: 2px 5px; }} .main-box {{ width: 100%; max-width: 148mm; margin: 0 auto; border: 1px solid #000; padding: 8px; background: white; }} .lbl {{ background-color: #E7E6E6; border: 1px solid black; text-align: right; font-weight: bold; width: 35%; }} .val {{ border: 1px solid black; text-transform: uppercase; font-weight: bold; color: #0000FF; }} @media print {{ @page {{ size: A5 portrait; margin: 4mm; }} body {{ padding: 0; margin: 0; }} .main-box {{ border: 2px solid #000; padding: 5px; width: 98%; max-width: none; box-sizing: border-box; }} * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }} }}</style></head><body onload="setTimeout(() => window.print(), 500)"><div class="main-box"><table style="border: 2px solid black; margin-bottom: 5px; width: 100%;"><tr><td style="background-color: #1F497D; color: white; text-align: center; font-size: 20px; font-weight: bold; padding: 4px;">M.S. PUBLIC SCHOOL</td></tr><tr><td style="text-align: center; font-size: 11px; font-weight: bold; padding: 2px; color: #222; border-bottom: 1px solid black;">Larawak, Kachhwa, Mirzapur - 231501 &nbsp;|&nbsp; Mob No: 6307210754, 9455587731</td></tr><tr><td style="background-color: #DCE6F1; text-align: center; font-size: 13px; font-weight: bold; padding: 2px;">FEE RECEIPT</td></tr></table><table style="margin-bottom: 5px; text-align: center;"><tr><td style="width: 25%; text-align: right; font-weight: bold;">Receipt No:</td><td style="width: 25%; background-color: #FFFF99; border: 1px solid black; font-weight: bold; font-size: 12px; color: #000;">{rec_no}</td><td style="width: 20%; background-color: #E7E6E6; border: 1px solid black; font-weight: bold;">Date:</td><td style="width: 30%; border: 1px solid black; color: red; font-weight: bold; font-size: 12px;">{rec_date}</td></tr></table><table style="margin-bottom: 5px;"><tr><td class="lbl">Roll No:</td><td class="val" style="color:#000;">{roll}</td></tr><tr><td class="lbl">Student Name:</td><td class="val">{name}</td></tr><tr><td class="lbl">Father Name:</td><td class="val">{fname}</td></tr><tr><td class="lbl">Class & Medium:</td><td class="val">{cls} ({medium})</td></tr><tr><td class="lbl">Fee Head Note:</td><td class="val" style="color:#000;">{fee_head_note}</td></tr><tr><td class="lbl">Payment Mode:</td><td class="val" style="color:#000;">{mode}</td></tr><tr><td class="lbl">Amount Paid:</td><td class="val" style="text-align: right; font-weight: bold; font-size: 14px; color:#000;">₹ {amt_paid:,}</td></tr></table><table style="margin-bottom: 5px;"><tr><td colspan="3" style="background-color: #4F81BD; color: white; text-align: center; font-weight: bold; padding: 3px; border: 1px solid black;">PAYMENT ALLOCATION BREAKDOWN</td></tr><tr><td style="background-color: #4F81BD; color: white; text-align: center; font-weight: bold; border: 1px solid black; width: 45%;">Fee Head</td><td style="background-color: #4F81BD; color: white; text-align: center; font-weight: bold; border: 1px solid black; width: 25%;">Amount Payable</td><td style="background-color: #4F81BD; color: white; text-align: center; font-weight: bold; border: 1px solid black; width: 30%;">Amount Applied</td></tr>{allocation_rows_html}</table><div style="text-align: center; font-size: 9px; font-style: italic; margin-bottom: 5px;">* Any excess advance amount is carried forward automatically.</div><table style="margin-bottom: 5px;"><tr><td colspan="2" style="background-color: #1F497D; color: white; text-align: center; font-weight: bold; padding: 3px; border: 1px solid black;">ACCOUNT STATUS (AS OF TODAY)</td></tr><tr><td class="lbl" style="width: 60%;">Total Payable (Till Month):</td><td class="val" style="font-weight: bold; color:#000;">₹ {pay:,}</td></tr><tr><td class="lbl">Total Paid (All Time):</td><td class="val" style="font-weight: bold; color:#000;">₹ {paid:,}</td></tr><tr><td class="lbl">Current Balance Due:</td><td class="val" style="font-weight: bold; color: #9C0006; background-color: #FFC7CE;">₹ {due:,}</td></tr><tr><td class="lbl">Advance Paid (If Any):</td><td class="val" style="font-weight: bold; color: #006100; background-color: #C6EFCE;">₹ {adv:,}</td></tr></table><div style="text-align: right; font-weight: bold; font-size: 11px; margin-top: 20px; padding-right: 10px;">_________________________<br>Authorized Signatory</div></div></body></html>"""
                components.html(html_code, height=900, scrolling=True)
                st.write("---")
                st.stop()

        # 👇 SIRF ADMIN KO ENTRY AUR EDIT KA OPTION DIKHEGA
        if role == 'Admin':
            tab1, tab2 = st.tabs(["💰 Collect New Fee", "✏️ Edit / Delete Receipt"])
            with tab1:
                with st.form("fee_form", clear_on_submit=True):
                    col1, col2, col3 = st.columns(3)
                    next_rec = get_next_receipt_no()
                    col1.text_input("Receipt No (Auto)", value=next_rec, disabled=True)
                    roll_no = col2.number_input("Roll No", min_value=1, step=1)
                    date = col3.date_input("Date")
                    amount = col1.number_input("Amount Paid (₹)", min_value=0, step=10)
                    mode = col2.selectbox("Payment Mode", ["CASH", "ONLINE (UPI)", "BANK TRANSFER", "CHEQUE"])
                    head = col3.text_input("Fee Head Note", value="GENERAL PAYMENT")
                    if st.form_submit_button("Save Payment"):
                        try:
                            c.execute("INSERT INTO fee_log (receipt_no, date, roll_no, amount, mode, head, collected_by) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                                      (next_rec, str(date), roll_no, amount, mode, head.upper().strip(), st.session_state.admin_id))
                            conn.commit(); st.success("Payment Saved!"); force_rerun()
                        except: st.error("❌ Something went wrong!")
            with tab2:
                e_rec = st.text_input("Enter Receipt No to Edit")
                if e_rec:
                    c.execute("SELECT * FROM fee_log WHERE receipt_no=?", (e_rec,))
                    rec_edit = c.fetchone()
                    if rec_edit:
                        with st.form("edit_rec_form"):
                            col1, col2, col3 = st.columns(3)
                            er_roll = col1.number_input("Roll No", value=rec_edit[2], step=1)
                            try: er_date = datetime.strptime(rec_edit[1], "%Y-%m-%d").date()
                            except: er_date = datetime.today().date()
                            er_date_in = col2.date_input("Date", value=er_date)
                            er_amt = col3.number_input("Amount", value=rec_edit[3], step=10)
                            modes = ["CASH", "ONLINE (UPI)", "BANK TRANSFER", "CHEQUE"]
                            er_mode = col1.selectbox("Mode", modes, index=modes.index(rec_edit[4]) if rec_edit[4] in modes else 0)
                            er_head = col2.text_input("Fee Head", value=rec_edit[5])
                            c1, c2 = st.columns(2)
                            if c1.form_submit_button("✅ Update"):
                                c.execute("UPDATE fee_log SET roll_no=?, date=?, amount=?, mode=?, head=? WHERE receipt_no=?", (er_roll, str(er_date_in), er_amt, er_mode, er_head.upper().strip(), e_rec))
                                conn.commit(); st.success("Updated!"); force_rerun()
                            if c2.form_submit_button("❌ Delete"):
                                c.execute("DELETE FROM fee_log WHERE receipt_no=?", (e_rec,))
                                conn.commit(); st.error("Deleted!"); force_rerun()

        st.write("---")
        st.write("### 💸 Recent Collections & Print")
        c.execute('''SELECT f.receipt_no, f.date, f.roll_no, s.name, s.class, f.head, f.amount, f.mode FROM fee_log f LEFT JOIN student_master s ON f.roll_no = s.roll_no ORDER BY f.date DESC LIMIT 20''')
        logs = c.fetchall()
        
        if logs:
            cols = st.columns([1.5, 1.2, 0.8, 1.5, 0.8, 1.5, 1, 1, 1])
            cols[0].markdown("**Receipt No**")
            cols[1].markdown("**Date**")
            cols[2].markdown("**Roll No**")
            cols[3].markdown("**Name**")
            cols[4].markdown("**Class**")
            cols[5].markdown("**Fee Head**")
            cols[6].markdown("**Amount**")
            cols[7].markdown("**Mode**")
            cols[8].markdown("**Action**")
            st.markdown("<hr style='margin:0; padding:0;'>", unsafe_allow_html=True)
            
            for r in logs:
                c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([1.5, 1.2, 0.8, 1.5, 0.8, 1.5, 1, 1, 1])
                c1.write(r[0])
                c2.write(r[1])
                c3.write(str(r[2]))
                c4.write(r[3] or "-")
                c5.write(str(r[4] or "-"))
                c6.write(r[5])
                c7.write(f"₹ {r[6]:,}")
                c8.write(r[7])
                if c9.button("🖨️ Print", key=f"print_{r[0]}"):
                    st.session_state.receipt_to_print = r[0]
                    force_rerun()
        else:
            st.info("No collections recorded yet.")

    elif menu == "🔍 Student Statement":
        st.subheader("Month-by-Month Student Fee Statement")
        roll = st.number_input("Enter Roll No:", min_value=1, step=1)
        if st.button("Generate Excel-Style Statement"):
            pay, paid, due, adv, stu = get_student_financials(roll, current_m_idx)
            if stu:
                st.markdown(f"""<div style="background-color:#1F497D; padding:15px; border-radius:8px; color:#FFFFFF; font-size:16px;">
                <span style="color:#A9D0F5;"><b>Student Name:</b></span> {stu[1].upper()} &nbsp; | &nbsp; <span style="color:#A9D0F5;"><b>Class:</b></span> {stu[2]} &nbsp; | &nbsp; <span style="color:#A9D0F5;"><b>Transport:</b></span> {stu[4]} &nbsp; | &nbsp; <span style="color:#A9D0F5;"><b>Medium:</b></span> {stu[5]}<br>
                <span style="color:#A9D0F5;"><b>Father Name:</b></span> {stu[3].upper()}</div><br>""", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                c1.info(f"Total Expected: ₹{pay:,}"); c2.success(f"Total Paid: ₹{paid:,}")
                if due > 0: c3.error(f"Current Due: ₹{due:,}")
                else: c3.success(f"Advance Rcvd: ₹{adv:,}")
                
                c.execute("SELECT * FROM fee_structure WHERE class=?", (stu[2],))
                fs = c.fetchone()
                heads = [('Registration Fee', fs[1], 1), ('Admission Fee', fs[2], 1), ('Other Fee', fs[9], 1)]
                c.execute("SELECT item_name, amount FROM student_charges WHERE roll_no=?", (roll,))
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
            else: st.error("Roll No not found!")

    elif menu == "📈 Class Statement":
        st.subheader("Class-wise Fee Summary")
        c.execute("SELECT class FROM fee_structure")
        sel_cls = st.selectbox("Select Class:", [x[0] for x in c.fetchall()])
        if st.button("Generate Report"):
            c.execute("SELECT roll_no, name, transport, medium FROM student_master WHERE class=?", (sel_cls,))
            students = c.fetchall()
            tot_pay_all = tot_paid_all = tot_due_all = tot_adv_all = 0; report = []
            for stu in students:
                pay, paid, due, adv, _ = get_student_financials(stu[0], current_m_idx)
                tot_pay_all += pay; tot_paid_all += paid; tot_due_all += due; tot_adv_all += adv
                status = "🔴 Due" if due > 0 else "🟢 Paid"
                report.append([stu[0], stu[1].upper(), sel_cls, f"₹{pay:,}", f"₹{paid:,}", f"₹{due:,}", f"₹{adv:,}", status])
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Students", len(students)); col2.metric("Total Expected", f"₹ {tot_pay_all:,}")
            col3.metric("Total Collected", f"₹ {tot_paid_all:,}"); col4.metric("Total Balance Due", f"₹ {tot_due_all:,}")
            st.write("---")
            st.dataframe(pd.DataFrame(report, columns=["Roll No", "Name", "Class", "Payable", "Paid", "Due", "Advance", "Status"]), use_container_width=True, hide_index=True)

    elif menu == "📅 Daily Collection":
        st.subheader("Daily Collection Report (By Admin ID)")
        query = """SELECT date as Date, collected_by as Admin_ID, SUM(amount) as Total,
                   SUM(CASE WHEN mode='CASH' THEN amount ELSE 0 END) as Cash,
                   SUM(CASE WHEN mode='ONLINE (UPI)' THEN amount ELSE 0 END) as Online_UPI,
                   SUM(CASE WHEN mode='BANK TRANSFER' THEN amount ELSE 0 END) as Bank,
                   SUM(CASE WHEN mode='CHEQUE' THEN amount ELSE 0 END) as Cheque 
                   FROM fee_log GROUP BY date, collected_by ORDER BY date DESC"""
        df_db = pd.read_sql_query(query, conn)
        if not df_db.empty:
            for col in ["Total", "Cash", "Online_UPI", "Bank", "Cheque"]: df_db[col] = df_db[col].apply(lambda x: f"₹ {x:,}")
            st.dataframe(df_db, use_container_width=True, hide_index=True)
        else: st.info("No collections recorded yet.")