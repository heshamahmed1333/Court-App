import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io

# إعداد الصفحة
st.set_page_config(page_title="نظام سكرتارية النقض", layout="wide")

st.title("⚖️ نظام توزيع طعون الجلسة الذكي")
st.write("رئاسة المستشار/ نبيل الكشكى")

# قائمة المستشارين بالترتيب (الأقدمية)
judges_names = [
    "نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق", 
    "ماجد ابراهيم", "محسن أبو بكر", "حاتم غراب", 
    "كمال عبد القوى", "محمد منصور", "محمد فؤاد"
]

if 'cases' not in st.session_state:
    st.session_state.cases = []

# --- القائمة الجانبية لإدخال البيانات ---
with st.sidebar:
    st.header("📝 إدخال بيانات الطعن")
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
            st.error("برجاء إدخال رقم الطعن!")

# --- الجزء الرئيسي ---
if st.session_state.cases:
    st.header("📊 جدول وضع العلامات (+ للمقرر / - للمشترك)")
    
    df_input = pd.DataFrame(st.session_state.cases)
    for name in judges_names:
        df_input[name] = ""
    
    edited_df = st.data_editor(df_input, num_rows="dynamic", use_container_width=True)

    if st.button("🚀 استخراج الجدول النهائي المرتب بالمسلسل"):
        final_list = []
        rank_map = {name: i for i, name in enumerate(judges_names)}

        for _, row in edited_df.iterrows():
            case_entry = {
                'رقم الطعن': row['رقم الطعن'], 'السنة': row['السنة'],
                'الطاعن': row['اسم الطاعن'], 'المحكمة': row['المحكمة المصدر'],
                'التهمة': row['التهمة'],
                'المقرر': "",
                'م1': "نبيل الكشكى", 'م2': "سامح عبد الرحيم", 'م3': "محمود صديق",
                'م4': "", 'م5': "",
                'sort_idx': 999
            }
            
            selected_members = []
            for judge in judges_names:
                mark = str(row[judge]).strip()
                if mark in ["+", "-"]:
                    if judge not in ["نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق"]:
                        selected_members.append(judge)
                    if mark == "+":
                        case_entry['المقرر'] = judge
                        case_entry['sort_idx'] = rank_map[judge]
            
            if len(selected_members) >= 1: case_entry['م4'] = selected_members[0]
            if len(selected_members) >= 2: case_entry['م5'] = selected_members[1]
            
            final_list.append(case_entry)

        # 1. الترتيب أولاً حسب أقدمية المقرر (sort_idx)
        res_df = pd.DataFrame(final_list).sort_values('sort_idx')

        # 2. إضافة عمود المسلسل (م) بعد الترتيب
        res_df.insert(0, 'م', range(1, len(res_df) + 1))

        # 3. حذف عمود الترتيب المساعد
        res_df = res_df.drop(columns=['sort_idx'])

        st.success("✅ تم الترتيب وإضافة المسلسل!")
        st.dataframe(res_df, use_container_width=True)

        # جهوزية ملف الإكسيل والورد (كما شرحنا سابقاً)
        # ... (أزرار التحميل هنا)
