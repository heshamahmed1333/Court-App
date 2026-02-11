import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io

# إعداد الصفحة
st.set_page_config(page_title="نظام سكرتارية النقض الذكي", layout="wide")

st.title("⚖️ منصة إدارة الجلسات الرقمية")

# قائمة المستشارين (الأقدمية)
judges_names = [
    "نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق", 
    "ماجد ابراهيم", "محسن أبو بكر", "حاتم غراب", 
    "كمال عبد القوى", "محمد منصور", "محمد فؤاد"
]

if 'cases' not in st.session_state:
    st.session_state.cases = []

# --- القائمة الجانبية (ثابتة للمرحلتين) ---
with st.sidebar:
    st.header("📂 إدارة البيانات")
    uploaded_file = st.file_uploader("استيراد جلسة سابقة (إكسيل)", type=["xlsx"])
    if uploaded_file:
        try:
            old_df = pd.read_excel(uploaded_file)
            st.session_state.cases = old_df.to_dict('records')
            st.success("تم شحن البيانات!")
        except:
            st.error("خطأ في قراءة الملف.")

    st.divider()
    date_val = st.text_input("تاريخ الجلسة", value="06-02-2026")
    session_type = st.selectbox("نوع الجلسة", options=["ج", "ض"])
    
    st.header("📝 إضافة طعن جديد")
    c_no = st.text_input("رقم الطعن")
    c_year = st.text_input("السنة")
    c_appellant = st.text_input("اسم الطاعن")
    c_court = st.text_input("المحكمة المصدر")
    c_charge = st.text_input("التهمة")

    if st.button("➕ إضافة الطعن"):
        if c_no:
            st.session_state.cases.append({
                'رقم الطعن': c_no, 'السنة': c_year,
                'اسم الطاعن': c_appellant, 'المحكمة المصدر': c_court,
                'التهمة': c_charge, 'النوع': session_type,
                'منطوق الحكم': "", 'حضور المحامين': ""
            })
            st.rerun()

# --- تقسيم الشاشة إلى زرين كبار (Tabs) ---
tab_prep, tab_close = st.tabs(["📑 تحضير الجلسة (توزيع الأدوار)", "🔨 تقفيل الجلسة (الأحكام والحضور)"])

# ---------------------------------------------------------
# 1. مرحلة تحضير الجلسة
# ---------------------------------------------------------
with tab_prep:
    if st.session_state.cases:
        st.subheader("توزيع المستشارين (+ للمقرر / - للمشترك)")
        df_prep = pd.DataFrame(st.session_state.cases)
        
        # إظهار أعمدة التوزيع فقط وإخفاء المنطوق والحضور
        cols_to_show = ['رقم الطعن', 'السنة', 'اسم الطاعن', 'المحكمة المصدر', 'التهمة'] + judges_names
        for j in judges_names:
            if j not in df_prep.columns: df_prep[j] = ""
            
        edited_prep = st.data_editor(df_prep[cols_to_show], num_rows="dynamic", use_container_width=True, key="prep_editor")

        if st.button("💾 حفظ توزيع الأدوار"):
            # تحديث بيانات السيشن بما تم تعديله في جدول التحضير
            for i, row in edited_prep.iterrows():
                for j in judges_names:
                    st.session_state.cases[i][j] = row[j]
            st.success("تم حفظ التوزيع بنجاح!")

# ---------------------------------------------------------
# 2. مرحلة تقفيل الجلسة
# ---------------------------------------------------------
with tab_close:
    if st.session_state.cases:
        st.subheader("إدخال مناطيق الأحكام وحضور المحامين")
        df_close = pd.DataFrame(st.session_state.cases)
        
        # إظهار الأعمدة الأساسية مع المنطوق والحضور فقط
        cols_close = ['رقم الطعن', 'السنة', 'اسم الطاعن', 'منطوق الحكم', 'حضور المحامين']
        edited_close = st.data_editor(df_close[cols_close], use_container_width=True, key="close_editor")

        if st.button("🚀 المعالجة النهائية واستخراج الرول/المحاضر"):
            # دمج كل البيانات (توزيع + أحكام) للمعالجة
            final_list = []
            rank_map = {name: i for i, name in enumerate(judges_names)}
            
            # تحديث السيشن ببيانات الإغلاق
            for i, row in edited_close.iterrows():
                st.session_state.cases[i]['منطوق الحكم'] = row['منطوق الحكم']
                st.session_state.cases[i]['حضور المحامين'] = row['حضور المحامين']

            for case in st.session_state.cases:
                case_entry = {
                    'م': 0, 'رقم_الطعن': case['رقم الطعن'], 'السنة': case['السنة'],
                    'الطاعن': case['اسم الطاعن'], 'المحكمة': case['المحكمة المصدر'],
                    'التهمة': case['التهمة'], 'النوع': case.get('النوع', 'ج'),
                    'منطوق_الحكم': case['منطوق الحكم'], 'حضور_المحامين': case['حضور المحامين'],
                    'م1': "نبيل الكشكى", 'م2': "سامح عبد الرحيم", 'م3': "محمود صديق",
                    'م4': "", 'م5': "", 'المقرر': "", 'sort_idx': 999
                }
                
                selected = []
                for judge in judges_names:
                    mark = str(case.get(judge, "")).strip()
                    if mark in ["+", "-"]:
                        if judge not in ["نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق"]:
                            selected.append(judge)
                        if mark == "+":
                            case_entry['المقرر'] = judge
                            case_entry['sort_idx'] = rank_map[judge]
                
                if len(selected) >= 1: case_entry['م4'] = selected[0]
                if len(selected) >= 2: case_entry['م5'] = selected[1]
                final_list.append(case_entry)

            # الترتيب والترقيم
            res_df = pd.DataFrame(final_list).sort_values('sort_idx')
            res_df['م'] = range(1, len(res_df) + 1)
            res_df = res_df.drop(columns=['sort_idx'])
            st.session_state.final_df = res_df
            
            st.success("تمت المعالجة النهائية!")
            st.dataframe(res_df)

            # أزرار التحميل
            st.divider()
            st.header("🖨️ طباعة المستندات النهائية")
            data_to_print = res_df.to_dict('records')
            context = {'cases': data_to_print, 'date': date_val}

            c1, c2, c3 = st.columns(3)
            # (نفس أكواد تحميل docxtpl السابقة هنا للرول والمحاضر والوقائع)
            with c1:
                try:
                    doc1 = DocxTemplate("template_roll.docx")
                    doc1.render(context)
                    bio1 = io.BytesIO()
                    doc1.save(bio1)
                    st.download_button("📥 تحميل الرول", bio1.getvalue(), f"Roll_{date_val}.docx")
                except: st.warning("قالب الرول ناقص")

# زر مسح البيانات
if st.button("🗑️ مسح كل البيانات لبدء جلسة جديدة"):
    st.session_state.cases = []
    st.rerun()
