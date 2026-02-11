import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io

st.set_page_config(page_title="نظام سكرتارية النقض الذكي", layout="wide")

# --- قائمة المستشارين الثابتة ---
judges_names = ["نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق", "ماجد ابراهيم", "محسن أبو بكر", "حاتم غراب", "كمال عبد القوى", "محمد منصور", "محمد فؤاد"]

# تهيئة السيشن
if 'cases' not in st.session_state: st.session_state.cases = []
if 'current_case_idx' not in st.session_state: st.session_state.current_case_idx = 0

# --- دالة تحويل البيانات لإكسيل للتحميل ---
def convert_df_to_excel(cases_list):
    output = io.BytesIO()
    df_to_save = pd.DataFrame(cases_list)
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_to_save.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# --- دالة المعالجة والترتيب (م) ---
def process_data():
    if not st.session_state.cases: return pd.DataFrame()
    final_list = []
    rank_map = {name: i for i, name in enumerate(judges_names)}
    for case in st.session_state.cases:
        entry = {
            'م': 0, 'رقم الطعن': case.get('رقم الطعن', ''), 'السنة': case.get('السنة', ''),
            'اسم الطاعن': case.get('اسم الطاعن', ''), 'المحكمة المصدر': case.get('المحكمة المصدر', ''),
            'التهمة': case.get('التهمة', ''), 'النوع': case.get('النوع', 'ج'),
            'منطوق الحكم': case.get('منطوق الحكم', ""), 'حضور المحامين': case.get('حضور المحامين', ""),
            'م1': "نبيل الكشكى", 'م2': "سامح عبد الرحيم", 'م3': "محمود صديق",
            'م4': "", 'م5': "", 'المقرر': "", 'sort_idx': 999
        }
        selected = []
        for j in judges_names:
            mark = str(case.get(j, "")).strip()
            if mark in ["+", "-"]:
                if j not in ["نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق"]: selected.append(j)
                if mark == "+":
                    entry['المقرر'] = j
                    entry['sort_idx'] = rank_map[j]
            entry[j] = mark # حفظ العلامات أيضاً
        if len(selected) >= 1: entry['م4'] = selected[0]
        if len(selected) >= 2: entry['م5'] = selected[1]
        final_list.append(entry)
    
    res_df = pd.DataFrame(final_list).sort_values('sort_idx')
    res_df['م'] = range(1, len(res_df) + 1)
    return res_df

# --- الشريط الجانبي (متاح في كل المراحل) ---
with st.sidebar:
    st.header("💾 مركز حفظ واستعادة البيانات")
    
    # 1. رفع ملف للاستكمال
    uploaded_file = st.file_uploader("استيراد ملف إكسيل (للمتابعة)", type=["xlsx"])
    if uploaded_file:
        try:
            st.session_state.cases = pd.read_excel(uploaded_file).to_dict('records')
            st.success("تم استعادة البيانات بنجاح!")
        except: st.error("خطأ في قراءة الملف.")
    
    st.divider()
    
    # 2. زر حفظ وتنزيل دائم
    if st.session_state.cases:
        st.subheader("حفظ العمل الحالي")
        excel_data = convert_df_to_excel(st.session_state.cases)
        st.download_button(
            label="📥 تنزيل ملف الجلسة الحالي (Excel)",
            data=excel_data,
            file_name=f"session_backup.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="اضغط هنا لحفظ كل ما قمت بإدخاله وتنزيله على جهازك لتكمله لاحقاً"
        )
    
    st.divider()
    st.header("📝 إدخال طعن جديد")
    date_v = st.text_input("تاريخ الجلسة", value="06-02-2026")
    type_v = st.selectbox("نوع الجلسة", ["ج", "ض"])
    c_no = st.text_input("رقم الطعن")
    c_yr = st.text_input("السنة")
    c_ap = st.text_input("اسم الطاعن")
    if st.button("➕ إضافة الطعن"):
        st.session_state.cases.append({'رقم الطعن': c_no, 'السنة': c_yr, 'اسم الطاعن': c_ap, 'النوع': type_v})
        st.rerun()

# --- واجهة التبويبات الرئيسية ---
tab_prep, tab_close = st.tabs(["📑 1. تحضير الجلسة", "🔨 2. تقفيل الجلسة"])

# 1. مرحلة التحضير
with tab_prep:
    if st.session_state.cases:
        st.subheader("جدول توزيع المستشارين")
        df_p = pd.DataFrame(st.session_state.cases)
        for j in judges_names: 
            if j not in df_p.columns: df_p[j] = ""
        
        edited_p = st.data_editor(df_p, use_container_width=True, key="prep_ed")
        if st.button("✅ حفظ توزيع المستشارين"):
            st.session_state.cases = edited_p.to_dict('records')
            st.success("تم حفظ التوزيع في الذاكرة المؤقتة. استخدم زر التحميل في الجانب لحفظه نهائياً.")

# 2. مرحلة التقفيل
with tab_close:
    if not st.session_state.cases:
        st.warning("يرجى إضافة طعون أو رفع ملف من الجانب أولاً.")
    else:
        processed_df = process_data()
        cases_list = processed_df.to_dict('records')
        
        col_side, col_main = st.columns([1, 3])
        with col_side:
            mode = st.radio("نوع العملية:", ["إضافة أحكام", "إضافة حضور محاميين"])
            idx = st.number_input("المسلسل الحالي (م):", min_value=1, max_value=len(cases_list), value=st.session_state.current_case_idx + 1)
            st.session_state.current_case_idx = idx - 1
            curr_case = cases_list[st.session_state.current_case_idx]
            
        with col_main:
            st.info(f"📍 طعن رقم: {curr_case['رقم الطعن']} لسنة {curr_case['السنة']} | {curr_case['اسم الطاعن']}")
            
            if mode == "إضافة أحكام":
                val = st.text_area("اكتب منطوق الحكم هنا:", value=curr_case.get('منطوق الحكم', ""))
                if st.button("حفظ الحكم 💾"):
                    for c in st.session_state.cases:
                        if str(c['رقم الطعن']) == str(curr_case['رقم الطعن']): c['منطوق الحكم'] = val
                    if st.session_state.current_case_idx < len(cases_list) - 1: st.session_state.current_case_idx += 1
                    st.rerun()
            else:
                val = st.text_area("اكتب حضور المحامين هنا:", value=curr_case.get('حضور المحامين', ""))
                if st.button("حفظ الحضور 💾"):
                    for c in st.session_state.cases:
                        if str(c['رقم الطعن']) == str(curr_case['رقم الطعن']): c['حضور المحامين'] = val
                    if st.session_state.current_case_idx < len(cases_list) - 1: st.session_state.current_case_idx += 1
                    st.rerun()

        st.divider()
        st.subheader("🖨️ استخراج ملفات الورد النهائية")
        if st.button("🔄 تحديث واستخراج الجداول والملفات"):
            final_df = process_data()
            st.dataframe(final_df)
            # هنا يتم وضع كود DocxTemplate للتحميل النهائي كما في السابق
