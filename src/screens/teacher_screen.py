import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import check_teacher_exists, create_teacher, teacher_login, get_teacher_subjects, get_attendance_for_teacher, get_attendance_with_student_for_teacher
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog

from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog
import numpy as np

from datetime import datetime

import pandas as pd

from src.database.config import supabase


from src.components.dialog_voice_attendance import voice_attendance_dialog
def teacher_screen():

    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=="login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()





def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {teacher_data['name']} """)
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data 
            st.rerun()


    st.space()

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'
    tab1, tab2, tab3 = st.columns(3)


    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == 'take_attendance' else "tertiary"
        if st.button('Take Attendance',type=type1, width='stretch', icon=':material/ar_on_you:'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == 'manage_subjects' else "tertiary"
        if st.button('Manage Subjects', type=type2, width='stretch', icon=':material/book_ribbon:'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()

    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == 'attendance_records' else "tertiary"
        if st.button('Attendance Records',type=type3, width='stretch', icon=':material/cards_stack:'):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()


    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()

    


    footer_dashboard()

def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.header('Take AI Attendance')


    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning('You havent created any subjects yet! Please create one to begin!')
        return
    
    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3,1], vertical_alignment='bottom')

    with col1:
        selected_subject_label = st.selectbox('Select Subject', options=list(subject_options.keys()))

    with col2:
        if st.button('Add Photos', type='primary', icon=':material/photo_prints:', width='stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()

    if st.session_state.attendance_images:
        st.header('Added Photos')
        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4 ]:
                st.image(img, width='stretch', caption=f'Photo {idx+1}')
    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button('Clear all photos', width='stretch', type='tertiary', icon=':material/delete:', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()


    with c2:
        
        if st.button('Run Face Analysis', width='stretch', type='secondary', icon=':material/analytics:', disabled=not has_photos):
            with st.spinner('Deep scanning classroom photos...'):
                all_detected_ids = {}

                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected, _, _ = predict_attendance(img_np)


                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)

                            all_detected_ids.setdefault(student_id, []).append(f"Photo {idx+1}")

                enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id',selected_subject_id ).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning('No students enrolled in this course')
                else:

                    results, attendance_to_log  = [], []

                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_ids.get(int(student['student_id']), [])
                        is_present= len(sources) > 0

                        results.append({
                            "Name": student['name'],
                            "ID": student['student_id'],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "✅ Present" if is_present else "❌ Absent"
                        })

                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })

                attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button('Use Voice Attendance', type='primary', width='stretch', icon=':material/mic:'):
            voice_attendance_dialog(selected_subject_id)











def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)
    with col1:
        st.header('Manage Subjects', width='stretch')

    with col2:
        if st.button('Create New Subject', width='stretch'):
            create_subject_dialog(teacher_id)


    # LIST all SUBJECTS
    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("🫂", "Students", sub['total_students']),
                ("🕰️", "Classes", sub['total_classes']),
            ]
        def share_btn():
            if st.button(f"Share Code: {sub['name']}", key=f"share_{sub['subject_code']}", icon=":material/share:"):
                share_subject_dialog(sub['name'], sub['subject_code'])
            st.space()

        subject_card(
            name = sub['name'],
            code = sub['subject_code'],
            section = sub['section'],
            stats=stats,
            footer_callback=share_btn
        )
    else:
        st.info("NO SUBJECTS FOUND. CREATE ONE ABOVE")


def teacher_tab_attendance_records():
    st.header('Attendance Records & Reports')

    teacher_id = st.session_state.teacher_data['teacher_id']

    # Fetch subjects
    subjects = get_teacher_subjects(teacher_id)
    
    # Fetch records
    records = get_attendance_for_teacher(teacher_id)

    if not records:
        st.info("No attendance records found yet. Start taking attendance to generate reports!")
        return

    # Tabs for different report views
    tab_overview, tab_subject_report, tab_session_report = st.tabs([
        "📅 Sessions Overview", 
        "📊 Subject Matrix Report", 
        "📝 Detailed Session Report"
    ])

    # 1. Sessions Overview Tab
    with tab_overview:
        st.subheader("All Class Sessions")
        
        data = []
        for r in records:
            ts = r.get('timestamp')
            data.append({
                "ts_group": ts.split(".")[0] if ts else None,
                "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N/A",
                "Subject": r['subjects']['name'],
                "Subject Code": r['subjects']['subject_code'],
                "is_present": bool(r.get('is_present', False))
            })

        df = pd.DataFrame(data)
        summary = (
            df.groupby(['ts_group', 'Time', 'Subject', 'Subject Code'])
            .agg(
                Present_Count = ('is_present', 'sum'),
                Total_Count = ('is_present', 'count')
            ).reset_index()
        )

        summary['Attendance Stats'] = (
            "✅ " + summary['Present_Count'].astype(str) + " / "
            + summary['Total_Count'].astype(str) + ' Students'
        )

        display_df = (summary.sort_values(by='ts_group', ascending=False)
                      [['Time', 'Subject', 'Subject Code', 'Attendance Stats']])
        
        st.dataframe(display_df, width='stretch', hide_index=True)

        # Download button for summary of sessions
        export_summary = display_df.copy()
        csv_summary = export_summary.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Sessions Overview (CSV)",
            data=csv_summary,
            file_name=f"sessions_overview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="download_sessions_overview"
        )

    # 2. Subject Matrix Report Tab
    with tab_subject_report:
        st.subheader("Subject-wise Attendance Grid")
        if not subjects:
            st.warning("No subjects found.")
        else:
            subject_options = {f"{s['name']} - {s['subject_code']}": s for s in subjects}
            selected_sub_label = st.selectbox(
                'Select Subject for Matrix Report', 
                options=list(subject_options.keys()),
                key='matrix_subject_select'
            )
            selected_sub = subject_options[selected_sub_label]
            selected_subject_id = selected_sub['subject_id']

            with st.spinner('Generating report...'):
                # Get all enrolled students for this subject
                enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', selected_subject_id).execute()
                enrolled_students = enrolled_res.data

                # Get all logs for this subject
                logs_res = supabase.table('attendance_logs').select("*, students(*)").eq('subject_id', selected_subject_id).execute()
                logs = logs_res.data

            if not enrolled_students:
                st.warning("No students are enrolled in this subject.")
            elif not logs:
                st.info("No attendance logs found for this subject yet.")
            else:
                # Find all unique timestamps (sessions) for this subject
                timestamps = sorted(list(set(log['timestamp'] for log in logs)))
                formatted_ts_headers = [datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") for ts in timestamps]

                # Map timestamp to its formatted name
                ts_map = dict(zip(timestamps, formatted_ts_headers))

                # Build the matrix
                matrix_rows = []
                for node in enrolled_students:
                    student = node['students']
                    s_id = student['student_id']
                    s_name = student['name']

                    row = {
                        "Student ID": s_id,
                        "Student Name": s_name
                    }

                    # Check attendance for each session
                    attended_count = 0
                    for ts in timestamps:
                        # Find log for this student and timestamp
                        log_entry = next((l for l in logs if l['student_id'] == s_id and l['timestamp'] == ts), None)
                        if log_entry and log_entry.get('is_present'):
                            row[ts_map[ts]] = "✅ Present"
                            attended_count += 1
                        else:
                            row[ts_map[ts]] = "❌ Absent"

                    row["Total Classes"] = len(timestamps)
                    row["Attended"] = attended_count
                    row["Attendance Rate (%)"] = round((attended_count / len(timestamps)) * 100, 2) if len(timestamps) > 0 else 0.0

                    matrix_rows.append(row)

                matrix_df = pd.DataFrame(matrix_rows)
                st.dataframe(matrix_df, width='stretch', hide_index=True)

                # Export Subject Matrix as CSV
                csv_matrix = matrix_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Export {selected_sub['name']} Report (CSV)",
                    data=csv_matrix,
                    file_name=f"attendance_report_{selected_sub['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_subject_matrix"
                )

    # 3. Session-Level Detailed Report Tab
    with tab_session_report:
        st.subheader("Detailed Session Attendance")
        
        # We need a list of unique sessions (timestamp, subject) from records
        detailed_records = get_attendance_with_student_for_teacher(teacher_id)
        
        if not detailed_records:
            st.info("No session logs found.")
        else:
            # Group by timestamp and subject
            sessions_dict = {}
            for r in detailed_records:
                ts = r.get('timestamp')
                sub_name = r['subjects']['name']
                sub_code = r['subjects']['subject_code']
                sub_id = r['subject_id']
                key = (ts, sub_id, sub_name, sub_code)
                if key not in sessions_dict:
                    sessions_dict[key] = []
                sessions_dict[key].append(r)

            # Sort sessions chronologically descending
            sorted_keys = sorted(sessions_dict.keys(), key=lambda x: x[0], reverse=True)
            
            session_labels = {
                f"{datetime.fromisoformat(k[0]).strftime('%Y-%m-%d %I:%M %p')} - {k[2]} ({k[3]})": k
                for k in sorted_keys
            }

            selected_session_label = st.selectbox(
                'Select Session to View Details',
                options=list(session_labels.keys()),
                key='session_detail_select'
            )
            
            selected_key = session_labels[selected_session_label]
            session_logs = sessions_dict[selected_key]
            
            # Show details
            session_ts, session_sub_id, session_sub_name, session_sub_code = selected_key
            
            st.write(f"**Subject:** {session_sub_name} ({session_sub_code})")
            st.write(f"**Date/Time:** {datetime.fromisoformat(session_ts).strftime('%Y-%m-%d %I:%M %p')}")
            
            session_data = []
            present_count = 0
            for log in session_logs:
                student = log.get('students')
                if student:
                    is_present = log.get('is_present', False)
                    if is_present:
                        present_count += 1
                    session_data.append({
                        "Student ID": student.get('student_id'),
                        "Student Name": student.get('name'),
                        "Status": "✅ Present" if is_present else "❌ Absent"
                    })
            
            session_df = pd.DataFrame(session_data)
            
            # Display stats cards/metrics
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Total Students", len(session_df))
            with m2:
                st.metric("Present", present_count)
            with m3:
                st.metric("Absent", len(session_df) - present_count)
                
            st.dataframe(session_df, width='stretch', hide_index=True)
            
            # Export session details
            csv_session = session_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Session Details (CSV)",
                data=csv_session,
                file_name=f"session_details_{session_sub_name.replace(' ', '_')}_{session_ts.split('.')[0].replace(':', '-')}.csv",
                mime="text/csv",
                key="download_session_details"
            )


def login_teacher(username, password):
    if not username or not password:
        return False
    
    teacher = teacher_login(username, password)

    if teacher:
        st.session_state.user_role ='teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    

    return False
def teacher_screen_login():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login using password', text_alignment='center')
    st.space()
    st.space()


    teacher_username = st.text_input("Enter username", placeholder='Eg.Sinchu')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Login', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            if login_teacher(teacher_username, teacher_pass):
                st.toast("welcome back!", icon="👋")
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username and password combo")

    with btnc2:
        if st.button('Register Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'register'

    footer_dashboard()



def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All Fields are required!"
    if check_teacher_exists(teacher_username):
        return False, "Username already taken"
    if teacher_pass != teacher_pass_confirm:
        return False, "Password doesn't match"
    
    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Sucessfully Created! Login Now"
    except Exception as e:
        return False, "Unexpected Error!"
    

def teacher_screen_register():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()



    st.header('Register your teacher profile')

    st.space()
    st.space()

    
    teacher_username = st.text_input("Enter username", placeholder='Deekshi12')

    teacher_name = st.text_input("Enter name", placeholder='Deekshi H K')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    teacher_pass_confirm = st.text_input("Confirm your password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Register now', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)


    with btnc2:
        if st.button('Login Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'login'

    footer_dashboard()