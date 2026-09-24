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
        
        # 🔍 1. DYNAMIC COLUMNS FETCHING LOGIC
        c.execute("SELECT * FROM student_master LIMIT 0")
        all_cols = [desc[0] for desc in c.description]
        std_cols = ['roll_no', 'name', 'class', 'father_name', 'transport', 'medium', 'mother_name', 'dob', 'sch_no']
        # Extract custom columns that are not standard (ignoring internal 'id' if any)
        custom_cols = [col for col in all_cols if col not in std_cols and col != 'id']

        tab1, tab2, tab3 = st.tabs(["➕ Add New Student", "✏️ Edit Existing Student", "⚙️ Manage Custom Fields"])
        
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
                
                # 🔥 DYNAMIC TEXT BOXES FOR CUSTOM FIELDS
                custom_vals = {}
                if custom_cols:
                    st.markdown("#### 🔹 Extra Details (Dynamic)")
                    dyn_cols = st.columns(3)
                    for i, c_name in enumerate(custom_cols):
                        c_title = c_name.replace("_", " ").title()
                        custom_vals[c_name] = dyn_cols[i % 3].text_input(c_title)
                
                if st.form_submit_button("Save Student"):
                    try:
                        dob_str = dob_obj.strftime("%d-%m-%Y")
                        
                        cols_to_insert = std_cols + custom_cols
                        placeholders = ", ".join(["?"] * len(cols_to_insert))
                        
                        vals_to_insert = [roll_no, name.upper().strip(), cls, father.upper().strip(), transport, medium, mother.upper().strip(), dob_str, sch_no.upper().strip()]
                        
                        # Add custom values to insertion array
                        for c_name in custom_cols:
                            vals_to_insert.append(custom_vals[c_name].upper().strip() if custom_vals[c_name] else "")
                            
                        query = f"INSERT INTO student_master ({', '.join(cols_to_insert)}) VALUES ({placeholders})"
                        c.execute(query, tuple(vals_to_insert))
                        conn.commit(); st.success("✅ Student Added!"); force_rerun()
                    except Exception as e: st.error(f"❌ Error: {e}")

        with tab2:
            edit_roll = st.number_input("Enter Roll No to Edit", min_value=1, step=1)
            query_cols = ", ".join(std_cols + custom_cols)
            c.execute(f"SELECT {query_cols} FROM student_master WHERE roll_no=?", (edit_roll,))
            stu_edit = c.fetchone()
            
            if stu_edit:
                with st.form("edit_stu_form"):
                    col1, col2, col3 = st.columns(3)
                    e_sch = col1.text_input("Scholar No", value=stu_edit[std_cols.index('sch_no')])
                    e_dob = col2.text_input("DOB (DD-MM-YYYY)", value=stu_edit[std_cols.index('dob')])
                    e_name = col3.text_input("Student Name", value=stu_edit[std_cols.index('name')])
                    e_father = col1.text_input("Father's Name", value=stu_edit[std_cols.index('father_name')])
                    e_mother = col2.text_input("Mother's Name", value=stu_edit[std_cols.index('mother_name')])
                    e_cls = col3.selectbox("Class", c_list, index=c_list.index(stu_edit[std_cols.index('class')]) if stu_edit[std_cols.index('class')] in c_list else 0)
                    e_trans = col1.radio("Transport", ["Self", "Van"], index=0 if stu_edit[std_cols.index('transport')]=="Self" else 1, horizontal=True)
                    e_med = col2.radio("Medium", ["HINDI", "ENGLISH"], index=0 if stu_edit[std_cols.index('medium')]=="HINDI" else 1, horizontal=True)
                    
                    # 🔥 DYNAMIC PRE-FILLED TEXT BOXES FOR EDITING
                    e_custom_vals = {}
                    if custom_cols:
                        st.markdown("#### 🔹 Extra Details (Dynamic)")
                        dyn_cols = st.columns(3)
                        for i, c_name in enumerate(custom_cols):
                            c_title = c_name.replace("_", " ").title()
                            idx = len(std_cols) + i
                            e_custom_vals[c_name] = dyn_cols[i % 3].text_input(c_title, value=stu_edit[idx] or "")
                    
                    if st.form_submit_button("Update Details"):
                        try:
                            set_clauses = ["name=?", "class=?", "father_name=?", "transport=?", "medium=?", "mother_name=?", "dob=?", "sch_no=?"]
                            update_vals = [e_name.upper().strip(), e_cls, e_father.upper().strip(), e_trans, e_med, e_mother.upper().strip(), e_dob, e_sch.upper().strip()]
                            
                            for c_name in custom_cols:
                                set_clauses.append(f"{c_name}=?")
                                update_vals.append(e_custom_vals[c_name].upper().strip())
                                
                            update_vals.append(edit_roll)
                            
                            query = f"UPDATE student_master SET {', '.join(set_clauses)} WHERE roll_no=?"
                            c.execute(query, tuple(update_vals))
                            conn.commit(); st.success("Updated!"); force_rerun()
                        except Exception as e: st.error(f"❌ Error: {e}")

        with tab3:
            # ⚙️ ADMIN ONLY: MANAGE CUSTOM FIELDS
            if role == 'Admin':
                st.info("💡 Add fields like 'Aadhar No', 'Address', or 'Blood Group'. They will automatically appear in the forms.")
                
                if custom_cols:
                    st.markdown("##### 📌 Currently Active Custom Fields:")
                    st.markdown("`" + "` | `".join([c.replace("_", " ").title() for c in custom_cols]) + "`")
                    st.write("---")
                
                colA, colB = st.columns(2)
                with colA:
                    with st.form("add_field_form"):
                        st.markdown("#### ➕ Create New Field")
                        new_field = st.text_input("Enter Field Name (e.g., Aadhar No)")
                        if st.form_submit_button("Add Field"):
                            if new_field.strip():
                                safe_col = new_field.strip().lower().replace(" ", "_").replace("-", "_")
                                if safe_col in all_cols:
                                    st.error("Field already exists!")
                                else:
                                    try:
                                        c.execute(f'ALTER TABLE student_master ADD COLUMN "{safe_col}" TEXT')
                                        conn.commit(); st.success(f"Added {new_field}!"); force_rerun()
                                    except Exception as e:
                                        st.error(f"Database Error: {e}")
                            else:
                                st.warning("Please enter a field name.")
                                
                with colB:
                    if custom_cols:
                        with st.form("del_field_form"):
                            st.markdown("#### 🗑️ Delete Field")
                            del_col = st.selectbox("Select Field to Delete", custom_cols, format_func=lambda x: x.replace("_", " ").title())
                            st.warning("⚠️ Deleting a field will permanently delete its data for all students.")
                            if st.form_submit_button("Delete Field"):
                                try:
                                    c.execute(f'ALTER TABLE student_master DROP COLUMN "{del_col}"')
                                    conn.commit(); st.success("Field Deleted!"); force_rerun()
                                except Exception as e:
                                    st.error(f"Error: Cannot delete column. {e}")
            else:
                st.warning("Only Admin can manage custom database fields.")

        st.write("---")
        df_stu = pd.read_sql_query("SELECT * FROM student_master ORDER BY class, roll_no", conn)
        # Reformat column headers for the display table to look neat
        df_stu.columns = [col.replace("_", " ").title() for col in df_stu.columns]
        st.dataframe(df_stu, use_container_width=True, hide_index=True)
        
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

# 👇 RECEIPT PRINTING OVERLAY (WORKS ACROSS ALL MENUS)
    if st.session_state.get('receipt_to_print'):
        rec_no = st.session_state.receipt_to_print
        c.execute('''SELECT f.receipt_no, f.date, f.roll_no, s.name, s.class, f.head, f.amount, f.mode, s.father_name, s.medium, s.transport FROM fee_log f LEFT JOIN student_master s ON f.roll_no = s.roll_no WHERE f.receipt_no=?''', (rec_no,))
        r = c.fetchone()
        if r:
            st.markdown("### 🖨️ A5 Receipt Print View")
            if st.button("❌ Close Receipt & Go Back"):
                st.session_state.receipt_to_print = None; force_rerun()
            rec_no, rec_date, roll, name, cls, fee_head_note, amt_paid, mode, fname, medium, transport = r
            name, cls, fname = name or "N/A", cls or "N/A", fname or "N/A"
            
            is_ext_receipt = str(fee_head_note).upper().startswith("EXTRA")
            
            # Fetch ONLY payments made BEFORE this specific receipt
            c.execute("SELECT amount, head FROM fee_log WHERE roll_no=? AND receipt_no < ? ORDER BY receipt_no ASC", (roll, rec_no))
            prev_payments = c.fetchall()
            
            prev_gen_paid = 0
            prev_ext_paid = 0
            for p_amt, p_head in prev_payments:
                if str(p_head).upper().startswith("EXTRA"): prev_ext_paid += p_amt
                else: prev_gen_paid += p_amt
                    
            new_gen_paid = prev_gen_paid + (0 if is_ext_receipt else amt_paid)
            new_ext_paid = prev_ext_paid + (amt_paid if is_ext_receipt else 0)

            # Build Fee Heads Table
            c.execute("SELECT * FROM fee_structure WHERE class=?", (cls,))
            fs = c.fetchone()
            heads = [('Registration Fee', fs[1], 1, False), ('Admission Fee', fs[2], 1, False), ('Other Fee', fs[9], 1, False)]
            
            c.execute("SELECT item_name, amount, date FROM student_charges WHERE roll_no=?", (roll,))
            for item in c.fetchall(): heads.append((f"{item[0]} (EXTRA)", item[1], get_m_idx_for_date(item[2]), True))
            
            heads.extend([('April Tuition', fs[3], 1, False), ('May Tuition', fs[3], 2, False), ('June Tuition', fs[3], 3, False), ('July Tuition', fs[3], 4, False), ('Quarterly Exam', fs[4], 4, False), ('August Tuition', fs[3], 5, False), ('September Tuition', fs[3], 6, False), ('October Tuition', fs[3], 7, False), ('Half-Yearly Exam', fs[5], 7, False), ('November Tuition', fs[3], 8, False), ('December Tuition', fs[3], 9, False), ('January Tuition', fs[3], 10, False), ('February Tuition', fs[3], 11, False), ('March Tuition', fs[3], 12, False), ('Yearly Exam', fs[6], 12, False)])
            heads.sort(key=lambda h: h[2])
            
            # 🔥 TIME CAPSULE FIX: Receipt ki date ke hisaab se logic check hoga
            try:
                rec_m_idx = get_m_idx_for_date(rec_date)
            except:
                rec_m_idx = get_current_m_idx() # fallback
                
            allocation_rows_html = ""
            cum_gen_payable = 0
            cum_ext_payable = 0
            hist_pay = 0 # Theek us din tak total fee kitni banti thi
            
            for h_name, base_amt, m_idx, is_ext in heads:
                head_payable = base_amt
                if "Tuition" in h_name:
                    if transport == "Van": head_payable += fs[7]
                    if medium == "ENGLISH": head_payable += fs[8]
                    
                if is_ext:
                    prev_paid_head = min(head_payable, max(0, prev_ext_paid - cum_ext_payable))
                    new_paid_head = min(head_payable, max(0, new_ext_paid - cum_ext_payable))
                    cum_ext_payable += head_payable
                else:
                    prev_paid_head = min(head_payable, max(0, prev_gen_paid - cum_gen_payable))
                    new_paid_head = min(head_payable, max(0, new_gen_paid - cum_gen_payable))
                    cum_gen_payable += head_payable
                    
                allocated = new_paid_head - prev_paid_head
                
                # 🔥 Calculate Total Expected Fee EXACTLY till the date of this receipt
                if m_idx <= rec_m_idx:
                    hist_pay += head_payable
                
                # Extra Receipt mein sirf Extra Item dikhega
                if is_ext_receipt and not is_ext:
                    continue
                    
                already_paid = (prev_paid_head >= head_payable and head_payable > 0)
                unpaid_portion = head_payable - prev_paid_head - allocated
                is_due_month = (m_idx <= rec_m_idx) # Only mark DUE if month had arrived BEFORE receipt date
                
                if allocated > 0:
                    if is_due_month and unpaid_portion > 0:
                        alloc_str = f"<b style='color:#006100;'>₹ {int(allocated):,}</b><br><span style='color:#9C0006; font-size:10px;'>(DUE: ₹ {int(unpaid_portion):,})</span>"
                    else:
                        alloc_str = f"<b style='color:#006100;'>₹ {int(allocated):,}</b>"
                elif already_paid:
                    alloc_str = "<b style='color:#006100; font-size:11px;'>PAID</b>"
                elif is_due_month:
                    alloc_str = f"<b style='color:#9C0006; font-size:11px;'>DUE: ₹ {int(unpaid_portion):,}</b>"
                else:
                    alloc_str = "<span style='color:#ccc;'>-</span>"
                    
                allocation_rows_html += f"<tr><td style='border: 1px solid black; padding: 1px 5px;'>{h_name.upper()}</td><td style='border: 1px solid black; padding: 1px 5px; text-align: center;'>₹ {head_payable:,}</td><td style='border: 1px solid black; padding: 1px 5px; text-align: center;'>{alloc_str}</td></tr>"
                
            # 🔥 Calculate EXACT HISTORICAL Due and Advance based on receipt time
            hist_paid = new_gen_paid + new_ext_paid
            hist_due = max(0, hist_pay - hist_paid)
            hist_adv = max(0, hist_paid - hist_pay)
            
            # HTML Render
            html_code = f"""<html><head><style>body {{ font-family: 'Calibri', Arial, sans-serif; font-size: 11px; color: black; background: #fff; padding: 10px; margin: 0; }} table {{ width: 100%; border-collapse: collapse; }} td {{ padding: 2px 5px; }} .main-box {{ width: 100%; max-width: 148mm; margin: 0 auto; border: 1px solid #000; padding: 8px; background: white; }} .lbl {{ background-color: #E7E6E6; border: 1px solid black; text-align: right; font-weight: bold; width: 35%; }} .val {{ border: 1px solid black; text-transform: uppercase; font-weight: bold; color: #0000FF; }} @media print {{ @page {{ size: A5 portrait; margin: 4mm; }} body {{ padding: 0; margin: 0; }} .main-box {{ border: 2px solid #000; padding: 5px; width: 98%; max-width: none; box-sizing: border-box; }} * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }} }}</style></head><body onload="setTimeout(() => window.print(), 500)"><div class="main-box"><table style="border: 2px solid black; margin-bottom: 5px; width: 100%;"><tr><td style="background-color: #1F497D; color: white; text-align: center; font-size: 20px; font-weight: bold; padding: 4px;">M.S. PUBLIC SCHOOL</td></tr><tr><td style="text-align: center; font-size: 11px; font-weight: bold; padding: 2px; color: #222; border-bottom: 1px solid black;">Larawak, Kachhwa, Mirzapur - 231501 &nbsp;|&nbsp; Mob No: 6307210754, 9455587731</td></tr><tr><td style="background-color: #DCE6F1; text-align: center; font-size: 13px; font-weight: bold; padding: 2px;">FEE RECEIPT</td></tr></table><table style="margin-bottom: 5px; text-align: center;"><tr><td style="width: 25%; text-align: right; font-weight: bold;">Receipt No:</td><td style="width: 25%; background-color: #FFFF99; border: 1px solid black; font-weight: bold; font-size: 12px; color: #000;">{rec_no}</td><td style="width: 20%; background-color: #E7E6E6; border: 1px solid black; font-weight: bold;">Date:</td><td style="width: 30%; border: 1px solid black; color: red; font-weight: bold; font-size: 12px;">{rec_date}</td></tr></table><table style="margin-bottom: 5px;"><tr><td class="lbl">Roll No:</td><td class="val" style="color:#000;">{roll}</td></tr><tr><td class="lbl">Student Name:</td><td class="val">{name}</td></tr><tr><td class="lbl">Father Name:</td><td class="val">{fname}</td></tr><tr><td class="lbl">Class & Medium:</td><td class="val">{cls} ({medium})</td></tr><tr><td class="lbl">Fee Head Note:</td><td class="val" style="color:#000;">{fee_head_note}</td></tr><tr><td class="lbl">Payment Mode:</td><td class="val" style="color:#000;">{mode}</td></tr><tr><td class="lbl">Amount Paid:</td><td class="val" style="text-align: right; font-weight: bold; font-size: 14px; color:#000;">₹ {amt_paid:,}</td></tr></table><table style="margin-bottom: 5px;"><tr><td colspan="3" style="background-color: #4F81BD; color: white; text-align: center; font-weight: bold; padding: 3px; border: 1px solid black;">PAYMENT ALLOCATION BREAKDOWN</td></tr><tr><td style="background-color: #4F81BD; color: white; text-align: center; font-weight: bold; border: 1px solid black; width: 45%;">Fee Head</td><td style="background-color: #4F81BD; color: white; text-align: center; font-weight: bold; border: 1px solid black; width: 25%;">Amount Payable</td><td style="background-color: #4F81BD; color: white; text-align: center; font-weight: bold; border: 1px solid black; width: 30%;">Amount Applied</td></tr>{allocation_rows_html}</table><div style="text-align: center; font-size: 9px; font-style: italic; margin-bottom: 5px;">* Any excess advance amount is carried forward automatically.</div><table style="margin-bottom: 5px;"><tr><td colspan="2" style="background-color: #1F497D; color: white; text-align: center; font-weight: bold; padding: 3px; border: 1px solid black;">ACCOUNT STATUS (AS ON RECEIPT DATE)</td></tr><tr><td class="lbl" style="width: 60%;">Current Balance Due:</td><td class="val" style="font-weight: bold; color: #9C0006; background-color: #FFC7CE;">₹ {hist_due:,}</td></tr><tr><td class="lbl">Advance Paid (If Any):</td><td class="val" style="font-weight: bold; color: #006100; background-color: #C6EFCE;">₹ {hist_adv:,}</td></tr></table><div style="text-align: right; font-weight: bold; font-size: 11px; margin-top: 20px; padding-right: 10px;">_________________________<br>Authorized Signatory</div></div></body></html>"""
            components.html(html_code, height=900, scrolling=True)
            st.write("---")
            st.stop()

    # 👇 COMBINED FEE COLLECTION & PRINTING TAB (RBAC ENABLED)
    if menu in ["📝 Fee Collection & Print", "🖨️ Print Receipts"]:
        if role == 'Teacher':
            st.subheader("🖨️ View & Print Receipts")
        else:
            st.subheader("Fee Receipts & Printing")
            tab1, tab2, tab3 = st.tabs(["💰 Collect New Fee", "🛍️ Collect Extra Charge", "✏️ Edit / Delete Receipt"])
            
            with tab1:
                # 🔍 SMART STUDENT SEARCH SYSTEM (GENERAL FEE)
                c.execute("SELECT roll_no, name, class, father_name FROM student_master")
                all_students = c.fetchall()
                search_options = ["🔍 --- Type Name to Search Student ---"]
                for s in all_students:
                    search_options.append(f"Roll: {s[0]} | Name: {s[1]} | Class: {s[2]} | Father: {s[3]}")
                
                selected_student = st.selectbox("Search & Select Student:", search_options, key="search_gen")
                auto_roll = 1
                if selected_student != "🔍 --- Type Name to Search Student ---":
                    auto_roll = int(selected_student.split("|")[0].replace("Roll:", "").strip())

                with st.form("fee_form", clear_on_submit=True):
                    col1, col2, col3 = st.columns(3)
                    next_rec = get_next_receipt_no()
                    col1.text_input("Receipt No (Auto)", value=next_rec, disabled=True)
                    
                    if selected_student != "🔍 --- Type Name to Search Student ---":
                        roll_no = col2.number_input("👤 Student Roll No", value=auto_roll, disabled=True)
                    else:
                        roll_no = col2.number_input("👤 Enter Roll No Manually", min_value=1, step=1)
                    
                    date = col3.date_input("Date")
                    amount = col1.number_input("Amount Paid (₹)", min_value=0, step=10)
                    mode = col2.selectbox("Payment Mode", ["CASH", "ONLINE (UPI)", "BANK TRANSFER", "CHEQUE"])
                    head = col3.text_input("Fee Head Note (DO NOT use 'EXTRA')", value="GENERAL PAYMENT")
                    
                    if st.form_submit_button("Save General Payment"):
                        if str(head).upper().startswith("EXTRA"):
                            st.error("❌ General Payment head cannot start with 'EXTRA'. Use the Extra Charge tab.")
                        else:
                            try:
                                c.execute("INSERT INTO fee_log (receipt_no, date, roll_no, amount, mode, head, collected_by) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                                          (next_rec, str(date), roll_no, amount, mode, head.upper().strip(), st.session_state.admin_id))
                                conn.commit(); st.success("General Payment Saved!"); force_rerun()
                            except: st.error("❌ Something went wrong!")

            with tab2:
                # 🛍️ MULTI-SELECT EXTRA CHARGE COLLECTION 
                st.markdown("### Collect Extra Charge (Items/Fines)")
                selected_student_ext = st.selectbox("Search & Select Student:", search_options, key="search_ext")
                auto_roll_ext = 1
                if selected_student_ext != "🔍 --- Type Name to Search Student ---":
                    auto_roll_ext = int(selected_student_ext.split("|")[0].replace("Roll:", "").strip())
                    
                c.execute("SELECT item_name, amount FROM student_charges WHERE roll_no=?", (auto_roll_ext,))
                all_extras = c.fetchall()
                c.execute("SELECT SUM(amount) FROM fee_log WHERE roll_no=? AND head LIKE ?", (auto_roll_ext, 'EXTRA%'))
                tot_ext_paid_so_far = c.fetchone()[0] or 0
                
                pool = tot_ext_paid_so_far
                pending_options = []
                for e_item, e_amt in all_extras:
                    if pool >= e_amt:
                        pool -= e_amt
                    else:
                        due = e_amt - pool
                        pool = 0
                        if due > 0:
                            pending_options.append(f"{e_item} (Due: ₹{due})")

                with st.form("extra_charge_form", clear_on_submit=True):
                    col1, col2, col3 = st.columns(3)
                    next_rec_ext = get_next_receipt_no() 
                    col1.text_input("Receipt No (Auto)", value=next_rec_ext, disabled=True, key="r_ext")
                    
                    if selected_student_ext != "🔍 --- Type Name to Search Student ---":
                        roll_no_ext = col2.number_input("👤 Student Roll No", value=auto_roll_ext, disabled=True, key="roll_ext_d")
                    else:
                        roll_no_ext = col2.number_input("👤 Enter Roll No", min_value=1, step=1, value=auto_roll_ext, key="roll_ext_m")

                    date_ext = col3.date_input("Date", key="d_ext")
                    
                    selected_items = st.multiselect("Select Extra Item(s) to Pay (Can choose multiple)", pending_options)
                    max_amt_payable = sum([int(x.split('₹')[1].replace(')', '')) for x in selected_items]) if selected_items else 0
                    
                    if selected_items:
                        item_names = [x.split(" (Due")[0] for x in selected_items]
                        default_head = f"EXTRA - {', '.join(item_names)}"
                    else:
                        default_head = "EXTRA CHARGE"
                        
                    amount_ext = col1.number_input(f"Amount Paid (Max Due: ₹{max_amt_payable})", min_value=0, step=10, value=max_amt_payable, key="a_ext")
                    mode_ext = col2.selectbox("Payment Mode", ["CASH", "ONLINE (UPI)", "BANK TRANSFER", "CHEQUE"], key="m_ext")
                    head_ext = col3.text_input("Fee Head Note (Must start with EXTRA)", value=default_head, key="h_ext")
                    
                    if st.form_submit_button("Save Extra Charge"):
                        if not selected_items:
                            st.warning("Please select at least one Extra Item from the dropdown.")
                        elif amount_ext <= 0:
                            st.warning("Amount must be greater than 0.")
                        elif amount_ext > max_amt_payable:
                            st.error(f"❌ Cannot accept more than pending due (₹{max_amt_payable}) for selected items!")
                        elif not head_ext.upper().startswith("EXTRA"):
                            st.error("❌ Fee Head Note must start with 'EXTRA'.")
                        else:
                            try:
                                c.execute("INSERT INTO fee_log (receipt_no, date, roll_no, amount, mode, head, collected_by) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                                          (next_rec_ext, str(date_ext), roll_no_ext, amount_ext, mode_ext, head_ext.upper().strip(), st.session_state.admin_id))
                                conn.commit(); st.success("✅ Extra Charge Saved!"); force_rerun()
                            except Exception as e: st.error(f"❌ Error: {e}")

            with tab3:
                # EDIT / DELETE RECEIPT
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
        st.subheader("Student Fee Statement & History")
        
        col1, col2 = st.columns([1, 2])
        active_roll = st.session_state.get('stmt_roll', 0)
        roll = col1.number_input("Enter Roll No:", min_value=1, step=1, value=active_roll if active_roll > 0 else 1)
        
        if col2.button("🔍 Generate / Refresh Statement") or active_roll > 0:
            st.session_state.stmt_roll = roll
            pay, paid, due, adv, stu = get_student_financials(roll, current_m_idx)
            
            if stu:
                st.markdown(f"""<div style="background-color:#1F497D; padding:15px; border-radius:8px; color:#FFFFFF; font-size:16px; margin-top:10px;">
                <span style="color:#A9D0F5;"><b>Student Name:</b></span> {stu[1].upper()} &nbsp; | &nbsp; <span style="color:#A9D0F5;"><b>Class:</b></span> {stu[2]} &nbsp; | &nbsp; <span style="color:#A9D0F5;"><b>Transport:</b></span> {stu[4]} &nbsp; | &nbsp; <span style="color:#A9D0F5;"><b>Medium:</b></span> {stu[5]}<br>
                <span style="color:#A9D0F5;"><b>Father Name:</b></span> {stu[3].upper()}</div><br>""", unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                c1.info(f"Total Expected: ₹{pay:,}"); c2.success(f"Total Paid: ₹{paid:,}")
                if due > 0: c3.error(f"Current Due: ₹{due:,}")
                else: c3.success(f"Advance Rcvd: ₹{adv:,}")
                
                # Fetch Payments to Create Pools
                c.execute("SELECT amount, head FROM fee_log WHERE roll_no=?", (roll,))
                all_logs = c.fetchall()
                tot_gen_paid = sum([x[0] for x in all_logs if not str(x[1]).upper().startswith("EXTRA")])
                tot_ext_paid = sum([x[0] for x in all_logs if str(x[1]).upper().startswith("EXTRA")])
                
                # --- GENERAL FEE TABLE ---
                st.markdown("#### 📘 Regular Fee Statement")
                c.execute("SELECT * FROM fee_structure WHERE class=?", (stu[2],))
                fs = c.fetchone()
                gen_heads = [('Registration Fee', fs[1], 1), ('Admission Fee', fs[2], 1), ('Other Fee', fs[9], 1)]
                gen_heads.extend([('April Tuition', fs[3], 1), ('May Tuition', fs[3], 2), ('June Tuition', fs[3], 3), ('July Tuition', fs[3], 4), ('Quarterly Exam', fs[4], 4), ('August Tuition', fs[3], 5), ('September Tuition', fs[3], 6), ('October Tuition', fs[3], 7), ('Half-Yearly Exam', fs[5], 7), ('November Tuition', fs[3], 8), ('December Tuition', fs[3], 9), ('January Tuition', fs[3], 10), ('February Tuition', fs[3], 11), ('March Tuition', fs[3], 12), ('Yearly Exam', fs[6], 12)])
                gen_heads.sort(key=lambda h: h[2])
                
                gen_pool = tot_gen_paid; gen_table = []
                for h_name, base_amt, m_idx in gen_heads:
                    amt = base_amt
                    if "Tuition" in h_name:
                        if stu[4] == "Van": amt += fs[7]
                        if stu[5] == "ENGLISH": amt += fs[8]
                    paid_here = min(amt, max(0, gen_pool))
                    gen_pool -= paid_here
                    if amt <= 0: status = "-"
                    elif paid_here >= amt: status = "🟢 Paid"
                    elif paid_here > 0: status = "🟡 Partial"
                    elif m_idx <= current_m_idx: status = "🔴 Due"
                    else: status = "⚪ Upcoming"
                    curr_due = max(0, amt - paid_here) if m_idx <= current_m_idx else 0
                    gen_table.append([h_name.upper(), f"₹{amt:,}", f"₹{paid_here:,}", status, f"₹{curr_due:,}"])
                st.dataframe(pd.DataFrame(gen_table, columns=["Fee Head / Month", "Payable", "Paid", "Status", "Current Due"]), use_container_width=True, hide_index=True)
                
                # --- EXTRA CHARGES TABLE ---
                st.markdown("#### 🎒 Extra Charges Statement")
                c.execute("SELECT item_name, amount FROM student_charges WHERE roll_no=?", (roll,))
                ext_items = c.fetchall()
                if ext_items:
                    ext_pool = tot_ext_paid; ext_table = []
                    for e_name, e_amt in ext_items:
                        paid_here = min(e_amt, max(0, ext_pool))
                        ext_pool -= paid_here
                        if e_amt <= 0: status = "-"
                        elif paid_here >= e_amt: status = "🟢 Paid"
                        elif paid_here > 0: status = "🟡 Partial"
                        else: status = "🔴 Due"
                        curr_due = max(0, e_amt - paid_here)
                        ext_table.append([e_name.upper(), f"₹{e_amt:,}", f"₹{paid_here:,}", status, f"₹{curr_due:,}"])
                    st.dataframe(pd.DataFrame(ext_table, columns=["Extra Item", "Payable", "Paid", "Status", "Current Due"]), use_container_width=True, hide_index=True)
                else:
                    st.info("No Extra Charges assigned to this student.")
                
                # --- RECENT PAYMENTS WITH VIEW BUTTON ---
                st.write("---")
                st.markdown("#### 💸 Payment History & Receipts")
                c.execute("SELECT receipt_no, date, head, amount, mode FROM fee_log WHERE roll_no=? ORDER BY receipt_no DESC", (roll,))
                recent_logs = c.fetchall()
                if recent_logs:
                    cols = st.columns([1.5, 1.2, 2, 1, 1, 1])
                    cols[0].markdown("**Receipt No**")
                    cols[1].markdown("**Date**")
                    cols[2].markdown("**Fee Head**")
                    cols[3].markdown("**Amount**")
                    cols[4].markdown("**Mode**")
                    cols[5].markdown("**Action**")
                    st.markdown("<hr style='margin:0; padding:0;'>", unsafe_allow_html=True)
                    
                    for r in recent_logs:
                        c1, c2, c3, c4, c5, c6 = st.columns([1.5, 1.2, 2, 1, 1, 1])
                        c1.write(r[0])
                        c2.write(r[1])
                        c3.write(r[2])
                        c4.write(f"₹ {r[3]:,}")
                        c5.write(r[4])
                        if c6.button("🖨️ View", key=f"stmt_print_{r[0]}"):
                            st.session_state.receipt_to_print = r[0]
                            force_rerun()
                else:
                    st.info("No payment history found for this student.")
                    
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