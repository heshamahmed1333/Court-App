import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io

# إعداد الصفحة
st.set_page_config(page_title="نظام سكرتارية النقض", layout="wide")

st.title("⚖️ نظام توزيع طعون الجلسة الذكي")
st.write("رئاسة المستشار/ نبيل الكشكى")

judges_names = [
    "نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق", 
    "ماجد ابراهيم", "محسن أبو بكر", "حاتم غراب", 
    "كمال عبد القوى", "محمد منصور", "محمد فؤاد"
]

# تهيئة مخزن البيانات في المتصفح
if 'cases' not in st.session_state:
    st.session_state.cases = []

# --- القائمة الجانبية ---
with st.sidebar:
    st.header("📂 استكمال عمل سابق")
    # خاصية رفع الملف القديم
    uploaded_file = st.file_uploader("ارفع ملف الإكسيل الذي قمت بتحميله سابقاً", type=["xlsx"])
    if uploaded_file:
        try:
            old_df = pd.read_excel(uploaded_file)
            # التأكد من وجود الأعمدة الأساسية وتحديث البيانات
            if 'رقم الطعن' in old_df.columns:
                # تحويل الإكسيل لبيانات يفهمها البرنامج
                st.session_state.cases = old_df[['رقم الطعن', 'السنة', 'اسم الطاعن', 'المحكمة المصدر', 'التهمة']].to_dict('records')
                st.success("تم استعادة بيانات الجلسة بنجاح!")
        except:
            st.error("عفواً، الملف غير متوافق.")

    st.divider()
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
            st.error("برجاء إدخال رقم الطعن!")

# --- الجزء الرئيسي ---
if st.session_state.cases:
    st.header("📊 جدول توزيع العمل")
    
    df_input = pd.DataFrame(st.session_state.cases)
    # إضافة أعمدة المستشارين إذا لم تكن موجودة
    for name in judges_names:
        if name not in df_input.columns:
            df_input[name] = ""
    
    edited_df = st.data_editor(df_input, num_rows="dynamic", key="main_editor", use_container_width=True)

    if st.button("🚀 معالجة البيانات واستخراج النتائج"):
        final_list = []
        rank_map = {name: i for i, name in enumerate(judges_names)}

        for _, row in edited_df.iterrows():
            case_entry = {
                'رقم_الطعن': row['رقم الطعن'], 'السنة': row['السنة'],
                'الطاعن': row['اسم الطاعن'], 'المحكمة': row['المحكمة المصدر'],
                'التهمة': row['التهمة'], 'المقرر': "",
                'م1': "نبيل الكشكى", 'م2': "سامح عبد الرحيم", 'م3': "محمود صديق",
                'م4': "", 'م5': "", 'sort_idx': 999
            }
            
            selected = []
            for judge in judges_names:
                mark = str(row[judge]).strip()
                if mark in ["+", "-"]:
                    if judge not in ["نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق"]:
                        selected.append(judge)
                    if mark == "+":
                        case_entry['المقرر'] = judge
                        case_entry['sort_idx'] = rank_map[judge]
            
            if len(selected) >= 1: case_entry['م4'] = selected[0]
            if len(selected) >= 2: case_entry['م5'] = selected[1]
            final_list.append(case_entry)

        res_df = pd.DataFrame(final_list).sort_values('sort_idx')
        res_df.insert(0, 'م', range(1, len(res_df) + 1))
        res_df = res_df.drop(columns=['sort_idx'])
        st.session_state.final_df = res_df
        
        st.success("✅ تم التحديث!")
        st.dataframe(res_df, use_container_width=True)

        # زر حفظ كـ إكسيل (للمسودة)
        towrite = io.BytesIO()
        res_df.to_excel(towrite, index=False, engine='openpyxl')
        st.download_button("💾 حفظ نسخة إكسيل لاستكمالها لاحقاً", towrite.getvalue(), f"backup_{date_val}.xlsx")

    # أزرار الطباعة (نفس الكود السابق)
    if 'final_df' in st.session_state:
        st.divider()
        st.header("🖨️ طباعة المستندات")
        # ... (أزرار الرول والمحاضر والوقائع) ...
