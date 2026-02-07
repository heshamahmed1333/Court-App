import streamlit as st
import pandas as pd

# إعداد الصفحة
st.set_page_config(page_title="نظام سكرتارية النقض", layout="wide")

st.title("⚖️ نظام توزيع طعون الجلسة الذكي")
st.write("رئاسة المستشار/ نبيل الكشكى")

# قائمة المستشارين بالترتيب
judges_names = [
    "نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق", 
    "ماجد ابراهيم", "محسن أبو بكر", "حاتم غراب", 
    "كمال عبد القوى", "محمد منصور", "محمد فؤاد"
]

if 'cases' not in st.session_state:
    st.session_state.cases = []

# --- القائمة الجانبية ---
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
    st.header("📊 جدول التوزيع (+ مقرر / - مشترك)")
    
    df_input = pd.DataFrame(st.session_state.cases)
    for name in judges_names:
        df_input[name] = ""
    
    edited_df = st.data_editor(df_input, num_rows="dynamic", use_container_width=True)

    if st.button("🚀 معالجة وترتيب النتائج"):
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
            
            others = []
            for judge in judges_names:
                mark = str(row[judge]).strip()
                if mark == "+":
                    case_entry['المقرر'] = judge
                    case_entry['sort_idx'] = rank_map[judge]
                elif mark == "-":
                    if judge not in ["نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق"]:
                        others.append(judge)
            
            if len(others) >= 1: case_entry['م4'] = others[0]
            if len(others) >= 2: case_entry['م5'] = others[1]
            
            final_list.append(case_entry)

        res_df = pd.DataFrame(final_list).sort_values('sort_idx').drop(columns=['sort_idx'])
        st.success("✅ تم الترتيب بنجاح!")
        st.dataframe(res_df, use_container_width=True)

        # تجهيز ملف التحميل
        towrite = pd.ExcelWriter(f'session_{date_val}.xlsx', engine='openpyxl')
        res_df.to_excel(towrite, index=False)
        towrite.close()
        
        with open(f'session_{date_val}.xlsx', 'rb') as f:
            st.download_button("📥 تحميل ملف الإكسيل النهائي", f, f"session_{date_val}.xlsx")

if st.button("🗑️ مسح الكل"):
    st.session_state.cases = []
    st.rerun()
