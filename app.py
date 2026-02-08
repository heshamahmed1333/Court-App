import streamlit as st
import pandas as pd

st.set_page_config(page_title="نظام سكرتارية النقض الذكي", layout="wide")

st.title("⚖️ نظام توزيع طعون الجلسة (دمج المقرر والأعضاء)")
st.write("رئاسة المستشار/ نبيل الكشكى")

judges_names = [
    "نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق", 
    "ماجد ابراهيم", "محسن أبو بكر", "حاتم غراب", 
    "كمال عبد القوى", "محمد منصور", "محمد فؤاد"
]

if 'cases' not in st.session_state:
    st.session_state.cases = []

with st.sidebar:
    st.header("📝 إدخال طعن جديد")
    date_val = st.text_input("تاريخ الجلسة", value="06-02-2026")
    c_no = st.text_input("رقم الطعن")
    c_year = st.text_input("السنة")
    c_appellant = st.text_input("اسم الطاعن")
    c_court = st.text_input("المحكمة المصدر")
    c_charge = st.text_input("التهمة")

    if st.button("إضافة الطعن"):
        if c_no:
            st.session_state.cases.append({
                'رقم الطعن': c_no, 'السنة': c_year,
                'اسم الطاعن': c_appellant, 'المحكمة المصدر': c_court,
                'التهمة': c_charge
            })
            st.toast(f"تم إضافة طعن رقم {c_no}")
        else:
            st.error("ادخل رقم الطعن!")

if st.session_state.cases:
    st.header("📊 جدول التوزيع")
    st.info("بمجرد وضع (+) أو (-) أمام اسم المستشار، سيتم إدراجه كعضو في الهيئة تلقائياً.")
    
    df_input = pd.DataFrame(st.session_state.cases)
    for name in judges_names:
        df_input[name] = ""
    
    edited_df = st.data_editor(df_input, num_rows="dynamic", use_container_width=True)

    if st.button("🚀 توليد الجدول النهائي"):
        final_list = []
        rank_map = {name: i for i, name in enumerate(judges_names)}

        for _, row in edited_df.iterrows():
            case_entry = {
                'رقم الطعن': row['رقم الطعن'], 'السنة': row['السنة'],
                'الطاعن': row['اسم الطاعن'], 'المحكمة': row['المحكمة المصدر'],
                'التهمة': row['التهمة'], 'المقرر': "",
                'م1': "نبيل الكشكى", 'م2': "سامح عبد الرحيم", 'م3': "محمود صديق",
                'م4': "", 'م5': "", 'sort_idx': 999
            }
            
            # قائمة لاحتواء أي مستشار تم تعليمه بـ + أو -
            selected_members = []
            
            for judge in judges_names:
                mark = str(row[judge]).strip()
                if mark in ["+", "-"]:
                    # استبعاد الثلاثة الكبار من القائمة الديناميكية لأنهم م1، م2، م3 ثوابت
                    if judge not in ["نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق"]:
                        selected_members.append(judge)
                    
                    # إذا كانت العلامة + يكون هو المقرر
                    if mark == "+":
                        case_entry['المقرر'] = judge
                        case_entry['sort_idx'] = rank_map[judge]
            
            # ملء م4 وم5 تلقائياً من المختارين (سواء كانوا + أو -)
            if len(selected_members) >= 1: case_entry['م4'] = selected_members[0]
            if len(selected_members) >= 2: case_entry['م5'] = selected_members[1]
            
            final_list.append(case_entry)

        res_df = pd.DataFrame(final_list).sort_values('sort_idx').drop(columns=['sort_idx'])
        st.success("✅ تم المعالجة! المقرر أصبح عضواً تلقائياً في خانات الهيئة.")
        st.dataframe(res_df, use_container_width=True)

        # تحميل الملف
        file_name = f"رول_{date_val}.xlsx"
        res_df.to_excel(file_name, index=False)
        with open(file_name, 'rb') as f:
            st.download_button("📥 تحميل الرول النهائي", f, file_name=file_name)

if st.button("🗑️ مسح الجلسة"):
    st.session_state.cases = []
    st.rerun()
