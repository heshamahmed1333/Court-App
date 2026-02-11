import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io

# 1. إعدادات الصفحة والأسماء
st.set_page_config(page_title="نظام سكرتارية النقض", layout="wide")
st.title("⚖️ نظام إدارة الجلسات المتكامل")

judges_names = [
    "نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق", 
    "ماجد ابراهيم", "محسن أبو بكر", "حاتم غراب", 
    "كمال عبد القوى", "محمد منصور", "محمد فؤاد"
]

# 2. إدارة الذاكرة (Session State)
if 'cases' not in st.session_state:
    st.session_state.cases = []
if 'curr_idx' not in st.session_state:
    st.session_state.curr_idx = 0

# 3. دالة معالجة وترتيب البيانات (م)
def get_final_df():
    if not st.session_state.cases:
        return pd.DataFrame()
    
    final_list = []
    rank_map = {name: i for i, name in enumerate(judges_names)}
    
    for case in st.session_state.cases:
        entry = {
            'م': 0,
            'رقم_الطعن': case.get('رقم الطعن', ''),
            'السنة': case.get('السنة', ''),
            'الطاعن': case.get('اسم الطاعن', ''),
            'المحكمة': case.get('المحكمة المصدر', ''),
            'التهمة': case.get('التهمة', ''),
            'النوع': case.get('النوع', 'ج'),
            'منطوق_الحكم': case.get('منطوق الحكم', ''),
            'حضور_المحامين': case.get('حضور المحامين', ''),
            'م1': "نبيل الكشكى", 'م2': "سامح عبد الرحيم", 'م3': "محمود صديق",
            'م4': "", 'م5': "", 'المقرر': "", 'sort_idx': 999
        }
        
        selected = []
        for judge in judges_names:
            mark = str(case.get(judge, "")).strip()
            if mark == "+":
                entry['المقرر'] = judge
                entry['sort_idx'] = rank_map[judge]
            elif mark == "-":
                if judge not in ["نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق"]:
                    selected.append(judge)
        
        if len(selected) >= 1: entry['م4'] = selected[0]
        if len(selected) >= 2: entry['م5'] = selected[1]
        final_list.append(entry)
    
    df = pd.DataFrame(final_list).sort_values('sort_idx')
    df['م'] = range(1, len(df) + 1)
    return df.drop(columns=['sort_idx'])

# --- القائمة الجانبية (إدارة البيانات) ---
with st.sidebar:
    st.header("📂 إدارة الجلسة")
    up = st.file_uploader("استيراد ملف إكسيل سابق", type="xlsx")
    if up:
        st.session_state.cases = pd.read_excel(up).fillna("").to_dict('records')
        st.rerun()

    if st.session_state.cases:
        towrite = io.BytesIO()
        pd.DataFrame(st.session_state.cases).to_excel(towrite, index=False)
        st.download_button("💾 حفظ الشغل الحالي (Excel)", towrite.getvalue(), "session_backup.xlsx")
    
    st.divider()
    st.header("📝 إدخال طعن جديد")
    date_val = st.text_input("تاريخ الجلسة", value="06-02-2026")
    type_val = st.selectbox("نوع الجلسة", ["ج", "ض"])
    c_no = st.text_input("رقم الطعن")
    c_yr = st.text_input("السنة")
    c_ap = st.text_input("اسم الطاعن")
    c_ct = st.text_input("المحكمة المصدر")
    c_ch = st.text_input("التهمة")
    
    if st.button("➕ إضافة الطعن للقائمة"):
        st.session_state.cases.append({
            'رقم الطعن': c_no, 'السنة': c_yr, 'اسم الطاعن': c_ap,
            'المحكمة المصدر': c_ct, 'التهمة': c_ch, 'النوع': type_val,
            'منطوق الحكم': "", 'حضور المحامين': ""
        })
        st.rerun()

# --- الواجهة الرئيسية ---
tab1, tab2 = st.tabs(["📑 1. تحضير الجلسة (التوزيع)", "🔨 2. تقفيل الجلسة (الأحكام)"])

# تبويب التحضير
with tab1:
    if st.session_state.cases:
        st.subheader("جدول البيانات وتوزيع المستشارين")
        df_p = pd.DataFrame(st.session_state.cases)
        # التأكد من وجود أعمدة المستشارين
        for j in judges_names:
            if j not in df_p.columns: df_p[j] = ""
        
        edited = st.data_editor(df_p, use_container_width=True, key="prep_editor")
        if st.button("✅ حفظ توزيع المستشارين"):
            st.session_state.cases = edited.to_dict('records')
            st.success("تم حفظ التوزيع بنجاح!")

# تبويب التقفيل
with tab2:
    df_final = get_final_df()
    if df_final.empty:
        st.warning("يرجى إدخال بيانات في التحضير أولاً.")
    else:
        cases_list = df_final.to_dict('records')
        
        # التنقل
        idx = st.number_input("المسلسل الحالي (م)", 1, len(cases_list), value=st.session_state.curr_idx + 1) - 1
        st.session_state.curr_idx = idx
        curr = cases_list[st.session_state.curr_idx]
        
        # عرض معلومات الطعن
        st.info(f"📍 طعن رقم: {curr['رقم_الطعن']} لسنة {curr['السنة']} | {curr['الطاعن']} | {curr['المحكمة']} | {curr['التهمة']}")
        
        col_a, col_b = st.columns(2)
        with col_a:
            h_val = st.text_area("منطوق الحكم", value=curr['منطوق_الحكم'], key=f"h_{curr['رقم_الطعن']}")
        with col_b:
            ho_val = st.text_area("حضور المحامين", value=curr['حضور_المحامين'], key=f"ho_{curr['رقم_الطعن']}")
            
        if st.button("💾 حفظ البيانات والذهاب للتالي"):
            for c in st.session_state.cases:
                if str(c['رقم الطعن']) == str(curr['رقم_الطعن']) and str(c['السنة']) == str(curr['السنة']):
                    c['منطوق الحكم'] = h_val
                    c['حضور المحامين'] = ho_val
            
            if st.session_state.curr_idx < len(cases_list) - 1:
                st.session_state.curr_idx += 1
            st.rerun()

        # --- المعاينة التلقائية الفورية ---
        st.divider()
        st.subheader("📊 معاينة الجدول النهائي")
        st.dataframe(get_final_df(), use_container_width=True)

        # --- قسم الطباعة (قوالب الورد) ---
        st.header("🖨️ استخراج القوالب")
        final_data = get_final_df().to_dict('records')
        context = {'cases': final_data, 'date': date_val}
        
        c1, c2, c3 = st.columns(3)
        with c1:
            try:
                doc = DocxTemplate("template_roll.docx")
                doc.render(context); b = io.BytesIO(); doc.save(b)
                st.download_button("📄 تحميل الرول", b.getvalue(), "Roll.docx")
            except: st.error("قالب الرول مفقود")
        with c2:
            try:
                doc = DocxTemplate("template_minutes.docx")
                doc.render(context); b = io.BytesIO(); doc.save(b)
                st.download_button("📜 تحميل المحاضر", b.getvalue(), "Minutes.docx")
            except: st.error("قالب المحاضر مفقود")
        with c3:
            try:
                doc = DocxTemplate("template_facts.docx")
                doc.render(context); b = io.BytesIO(); doc.save(b)
                st.download_button("📑 تحميل الوقائع", b.getvalue(), "Facts.docx")
            except: st.error("قالب الوقائع مفقود")
