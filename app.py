import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io

# إعداد الصفحة
st.set_page_config(page_title="نظام سكرتارية النقض الذكي", layout="wide")

st.title("⚖️ نظام إدارة طعون الجلسة المتكامل")

# قائمة المستشارين (الأقدمية)
judges_names = [
    "نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق", 
    "ماجد ابراهيم", "محسن أبو بكر", "حاتم غراب", 
    "كمال عبد القوى", "محمد منصور", "محمد فؤاد"
]

if 'cases' not in st.session_state:
    st.session_state.cases = []

# --- القائمة الجانبية ---
with st.sidebar:
    st.header("📂 استكمال عمل سابق")
    uploaded_file = st.file_uploader("ارفع ملف الإكسيل لاستكمال الشغل", type=["xlsx"])
    if uploaded_file:
        try:
            old_df = pd.read_excel(uploaded_file)
            st.session_state.cases = old_df.to_dict('records')
            st.success("تم استعادة البيانات!")
        except:
            st.error("تنسيق الملف غير مدعوم.")

    st.divider()
    st.header("📝 إدخال بيانات الطعن")
    date_val = st.text_input("تاريخ الجلسة", value="06-02-2026")
    session_type = st.selectbox("نوع الجلسة", options=["ج", "ض"])
    
    c_no = st.text_input("رقم الطعن")
    c_year = st.text_input("السنة")
    c_appellant = st.text_input("اسم الطاعن")
    c_court = st.text_input("المحكمة المصدر")
    c_charge = st.text_input("التهمة")

    if st.button("إضافة الطعن للقائمة"):
        if c_no:
            st.session_state.cases.append({
                'رقم الطعن': c_no, 'السنة': c_year,
                'اسم الطاعن': c_appellant, 'المحكمة المصدر': c_court,
                'التهمة': c_charge, 'النوع': session_type,
                'منطوق الحكم': "", 'حضور المحامين': "" # الخانات الجديدة
            })
            st.toast(f"تم إضافة طعن رقم {c_no}")
        else:
            st.error("يرجى إدخال رقم الطعن")

# --- الجزء الرئيسي ---
if st.session_state.cases:
    st.header("📊 جدول البيانات (توزيع المستشارين + المنطوق والحضور)")
    st.info("يمكنك كتابة المنطوق وحضور المحامين مباشرة في الجدول أدناه لكل طعن.")
    
    df_input = pd.DataFrame(st.session_state.cases)
    # إضافة أعمدة المستشارين
    for name in judges_names:
        if name not in df_input.columns:
            df_input[name] = ""
    
    # التأكد من وجود الخانات الجديدة في الجدول
    if 'منطوق الحكم' not in df_input.columns: df_input['منطوق الحكم'] = ""
    if 'حضور المحامين' not in df_input.columns: df_input['حضور المحامين'] = ""

    # عرض الجدول للتعديل
    edited_df = st.data_editor(df_input, num_rows="dynamic", key="main_editor", use_container_width=True)

    if st.button("🚀 معالجة وحفظ البيانات النهائية"):
        final_list = []
        rank_map = {name: i for i, name in enumerate(judges_names)}

        for _, row in edited_df.iterrows():
            case_entry = {
                'م': 0,
                'رقم_الطعن': row['رقم الطعن'], 'السنة': row['السنة'],
                'الطاعن': row['اسم الطاعن'], 'المحكمة': row['المحكمة المصدر'],
                'التهمة': row['التهمة'], 'النوع': row['النوع'],
                'منطوق_الحكم': row['منطوق الحكم'], # للورد
                'حضور_المحامين': row['حضور المحامين'], # للورد
                'المقرر': "",
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
        res_df['م'] = range(1, len(res_df) + 1)
        res_df = res_df.drop(columns=['sort_idx'])
        st.session_state.final_df = res_df
        
        st.success("✅ تم تحديث البيانات بنجاح!")
        st.dataframe(res_df, use_container_width=True)

        # حفظ نسخة الإكسيل للاستكمال (شاملة المنطوق والحضور)
        towrite = io.BytesIO()
        res_df.to_excel(towrite, index=False)
        st.download_button("💾 حفظ النسخة الحالية (إكسيل)", towrite.getvalue(), f"session_backup_{date_val}.xlsx")

    # --- مركز الطباعة ---
    if 'final_df' in st.session_state:
        st.divider()
        st.header("🖨️ طباعة المستندات")
        data_to_print = st.session_state.final_df.to_dict('records')
        context = {'cases': data_to_print, 'date': date_val}

        c1, c2, c3 = st.columns(3)
        with c1:
            try:
                doc1 = DocxTemplate("template_roll.docx")
                doc1.render(context)
                bio1 = io.BytesIO()
                doc1.save(bio1)
                st.download_button("📄 تحميل الرول", bio1.getvalue(), f"Roll_{date_val}.docx")
            except: st.warning("قالب الرول غير موجود")
        
        with c2:
            try:
                doc2 = DocxTemplate("template_minutes.docx")
                doc2.render(context)
                bio2 = io.BytesIO()
                doc2.save(bio2)
                st.download_button("📜 تحميل المحاضر", bio2.getvalue(), f"Minutes_{date_val}.docx")
            except: st.warning("قالب المحاضر غير موجود")

        with c3:
            try:
                doc3 = DocxTemplate("template_facts.docx")
                doc3.render(context)
                bio3 = io.BytesIO()
                doc3.save(bio3)
                st.download_button("📑 تحميل الوقائع", bio3.getvalue(), f"Facts_{date_val}.docx")
            except: st.warning("قالب الوقائع غير موجود")
