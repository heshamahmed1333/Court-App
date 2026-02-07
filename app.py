import streamlit as st
import pandas as pd
import os

# إعدادات الصفحة
st.set_page_config(page_title="نظام سكرتارية النقض الذكي", layout="wide")

st.title("⚖️ نظام توزيع طعون الجلسة (الهيئة الخماسية)")
st.subheader("المستشار/ نبيل الكشكى - رئيس الدائرة")

# المستشارين الثابتين
judges_names = [
    "نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق", 
    "ماجد ابراهيم", "محسن أبو بكر", "حاتم غراب", 
    "كمال عبد القوى", "محمد منصور", "محمد فؤاد"
]

# مخزن البيانات في الجلسة (Session State)
if 'cases' not in st.session_state:
    st.session_state.cases = []

# --- الجزء الأول: إدخال البيانات ---
with st.sidebar:
    st.header("📝 إدخال طعن جديد")
    date = st.text_input("تاريخ الجلسة", placeholder="06-02-2026")
    case_no = st.text_input("رقم الطعن")
    case_year = st.text_input("السنة")
    appellant = st.text_input("اسم الطاعن")
    court = st.text_input("المحكمة المصدر")
    charge = st.text_input("التهمة")

    if st.button("إضافة الطعن للقائمة"):
        if case_no:
            st.session_state.cases.append({
                'رقم الطعن': case_no, 'السنة': case_year,
                'اسم الطاعن': appellant, 'المحكمة المصدر': court,
                'التهمة': charge
            })
            st.success(f"تم إضافة طعن رقم {case_no}")
        else:
            st.error("برجاء إدخال رقم الطعن")

# --- الجزء الثاني: التوزيع والترتيب ---
if st.session_state.cases:
    st.header("📊 جدول توزيع الهيئة (+ مقرر / - مشترك)")
    
    # تحويل القائمة لجدول وعرضها للتعديل
    df_temp = pd.DataFrame(st.session_state.cases)
    for name in judges_names:
        df_temp[name] = ""
    
    # ميزة التعديل المباشر (Data Editor)
    edited_df = st.data_editor(df_temp, num_rows="dynamic")

    if st.button("🚀 تحويل ومعالجة النتائج النهائية"):
        final_data = []
        judge_rank = {name: i for i, name in enumerate(judges_names)}

        for index, row in edited_df.iterrows():
            case_info = {
                'رقم الطعن': row['رقم الطعن'], 'السنة': row['السنة'],
                'الطاعن': row['اسم الطاعن'], 'المقرر': "",
                'م1': "نبيل الكشكى", 'م2': "سامح عبد الرحيم", 'م3': "محمود صديق",
                'م4': "", 'م5': "", 'رتبة_المقرر': 999
            }
            
            other_members = []
            for judge in judges_names:
                mark = str(row[judge]).strip()
                if mark == "+":
                    case_info['المقرر'] = judge
                    case_info['رتبة_المقرر'] = judge_rank[judge]
                elif mark == "-" and judge not in ["نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق"]:
                    other_members.append(judge)
            
            if len(other_members) >= 1: case_info['م4'] = other_members[0]
            if len(other_members) >= 2: case_info['م5'] = other_members[1]
            
            final_data.append(case_info)

        final_df = pd.DataFrame(final_data).sort_values(by='رتبة_المقرر')
        final_df = final_df.drop(columns=['رتبة_المقرر'])

        st.header("✅ النتائج النهائية")
        st.dataframe(final_df)

        # زر تحميل ملف الإكسيل
        csv = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل النتائج (Excel/CSV)", data=csv, file_name=f"نتائج_{date}.csv", mime='text/csv')

if st.button("🗑️ مسح الكل لبدء جلسة جديدة"):
    st.session_state.cases = []
    st.rerun()