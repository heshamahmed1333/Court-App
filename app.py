import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io

st.set_page_config(page_title="نظام سكرتارية النقض الذكي", layout="wide")

# --- قائمة المستشارين ---
judges_names = ["نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق", "ماجد ابراهيم", "محسن أبو بكر", "حاتم غراب", "كمال عبد القوى", "محمد منصور", "محمد فؤاد"]

if 'cases' not in st.session_state: st.session_state.cases = []
if 'current_case_idx' not in st.session_state: st.session_state.current_case_idx = 0

# --- دالة الحفظ الشاملة ---
def save_case_data(case_no, case_year, field_name, value):
    for case in st.session_state.cases:
        # الربط برقم الطعن والسنة معاً لضمان الدقة
        if str(case['رقم الطعن']) == str(case_no) and str(case['السنة']) == str(case_year):
            case[field_name] = value
            return True
    return False

# --- دالة المعالجة والترتيب ---
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
            entry[j] = mark
        if len(selected) >= 1: entry['م4'] = selected[0]
        if len(selected) >= 2: entry['م5'] = selected[1]
        final_list.append(entry)
    
    res_df = pd.DataFrame(final_list).sort_values('sort_idx')
    res_df['م'] = range(1, len(res_df) + 1)
    return res_df

# --- القائمة الجانبية ---
with st.sidebar:
    st.header("💾 إدارة الملفات")
    uploaded_file = st.file_uploader("رفع ملف إكسيل لاستكمال العمل", type=["xlsx"])
    if uploaded_file:
        st.session_state.cases = pd.read_excel(uploaded_file).fillna("").to_dict('records')
        st.success("تم شحن البيانات!")
    
    if st.session_state.cases:
        df_to_save = pd.DataFrame(st.session_state.cases)
        towrite = io.BytesIO()
        df_to_save.to_excel(towrite, index=False, engine='openpyxl')
        st.download_button("📥 حفظ العمل الحالي (إكسيل)", towrite.getvalue(), "session_backup.xlsx")

    st.divider()
    st.header("📝 إضافة طعن جديد")
    c_no = st.text_input("رقم الطعن")
    c_yr = st.text_input("السنة")
    c_ap = st.text_input("اسم الطاعن")
    if st.button("➕ إضافة"):
        st.session_state.cases.append({'رقم الطعن': c_no, 'السنة': c_yr, 'اسم الطاعن': c_ap})
        st.rerun()

# --- التبويبات ---
tab_prep, tab_close = st.tabs(["📑 تحضير الجلسة", "🔨 تقفيل الجلسة"])

with tab_prep:
    if st.session_state.cases:
        df_p = pd.DataFrame(st.session_state.cases)
        for j in judges_names:
            if j not in df_p.columns: df_p[j] = ""
        edited_p = st.data_editor(df_p, use_container_width=True, key="prep_ed")
        if st.button("✅ حفظ توزيع المستشارين"):
            st.session_state.cases = edited_p.to_dict('records')
            st.success("تم حفظ التوزيع!")

with tab_close:
    if not st.session_state.cases:
        st.warning("لا توجد بيانات.")
    else:
        # الترتيب حسب المسلسل م
        processed_df = process_data()
        cases_list = processed_df.to_dict('records')
        
        col_side, col_main = st.columns([1, 2])
        with col_side:
            mode = st.radio("نوع الإدخال:", ["الأحكام", "حضور المحامين"])
            idx = st.number_input("المسلسل الحالي (م):", 1, len(cases_list), value=st.session_state.current_case_idx + 1)
            st.session_state.current_case_idx = idx - 1
            curr = cases_list[st.session_state.current_case_idx]
            
        with col_main:
            st.markdown(f"### طعن {curr['رقم الطعن']} / {curr['السنة']}")
            st.write(f"**الطاعن:** {curr['اسم الطاعن']}")
            
            if mode == "الأحكام":
                current_val = curr.get('منطوق الحكم', "")
                new_val = st.text_area("منطوق الحكم:", value=current_val, key=f"v_{curr['م']}")
                if st.button("💾 حفظ الحكم"):
                    save_case_data(curr['رقم الطعن'], curr['السنة'], 'منطوق الحكم', new_val)
                    st.toast("تم حفظ الحكم!")
                    if st.session_state.current_case_idx < len(cases_list) - 1:
                        st.session_state.current_case_idx += 1
                    st.rerun()
            else:
                current_val = curr.get('حضور المحامين', "")
                new_val = st.text_area("حضور المحامين:", value=current_val, key=f"h_{curr['م']}")
                if st.button("💾 حفظ الحضور"):
                    save_case_data(curr['رقم الطعن'], curr['السنة'], 'حضور المحامين', new_val)
                    st.toast("تم حفظ الحضور!")
                    if st.session_state.current_case_idx < len(cases_list) - 1:
                        st.session_state.current_case_idx += 1
                    st.rerun()

        st.divider()
        if st.button("🔄 عرض الجدول النهائي للطباعة"):
            final_df = process_data()
            st.dataframe(final_df)
