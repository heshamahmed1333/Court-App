import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io

st.set_page_config(page_title="نظام سكرتارية النقض الذكي", layout="wide")

# --- قائمة المستشارين الثابتة ---
judges_names = ["نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق", "ماجد ابراهيم", "محسن أبو بكر", "حاتم غراب", "كمال عبد القوى", "محمد منصور", "محمد فؤاد"]

if 'cases' not in st.session_state: st.session_state.cases = []
if 'current_case_idx' not in st.session_state: st.session_state.current_case_idx = 0

# --- دالة المعالجة والترتيب ---
def process_data():
    final_list = []
    rank_map = {name: i for i, name in enumerate(judges_names)}
    for case in st.session_state.cases:
        entry = {
            'م': 0, 'رقم_الطعن': case['رقم الطعن'], 'السنة': case['السنة'],
            'الطاعن': case['اسم الطاعن'], 'المحكمة': case['المحكمة المصدر'],
            'التهمة': case['التهمة'], 'النوع': case.get('النوع', 'ج'),
            'منطوق_الحكم': case.get('منطوق الحكم', ""), 'حضور_المحامين': case.get('حضور المحامين', ""),
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
        if len(selected) >= 1: entry['م4'] = selected[0]
        if len(selected) >= 2: entry['م5'] = selected[1]
        final_list.append(entry)
    
    res_df = pd.DataFrame(final_list).sort_values('sort_idx')
    res_df['م'] = range(1, len(res_df) + 1)
    return res_df.drop(columns=['sort_idx'])

# --- واجهة البرنامج ---
tab_prep, tab_close = st.tabs(["📋 تحضير الجلسة", "⚖️ تقفيل الجلسة (الأحكام والحضور)"])

# 1. تحضير الجلسة
with tab_prep:
    with st.sidebar:
        st.header("📝 إدخال طعون جديدة")
        date_v = st.text_input("تاريخ الجلسة", value="06-02-2026")
        type_v = st.selectbox("نوع الجلسة", ["ج", "ض"])
        c_no = st.text_input("رقم الطعن")
        c_yr = st.text_input("السنة")
        c_ap = st.text_input("اسم الطاعن")
        c_ct = st.text_input("المحكمة المصدر")
        c_ch = st.text_input("التهمة")
        if st.button("إضافة الطعن"):
            st.session_state.cases.append({'رقم الطعن': c_no, 'السنة': c_yr, 'اسم الطاعن': c_ap, 'المحكمة المصدر': c_ct, 'التهمة': c_ch, 'النوع': type_v})
            st.rerun()

    if st.session_state.cases:
        st.subheader("جدول توزيع المستشارين")
        df_p = pd.DataFrame(st.session_state.cases)
        for j in judges_names: 
            if j not in df_p.columns: df_p[j] = ""
        
        edited_p = st.data_editor(df_p, use_container_width=True, key="prep_ed")
        if st.button("💾 حفظ التوزيع والترتيب"):
            st.session_state.cases = edited_p.to_dict('records')
            st.success("تم الحفظ والترتيب حسب الأقدمية!")

# 2. تقفيل الجلسة
with tab_close:
    if not st.session_state.cases:
        st.warning("يرجى تحضير الجلسة أولاً")
    else:
        # ترتيب الطعون أولاً حسب م
        processed_df = process_data()
        cases_list = processed_df.to_dict('records')
        
        col_side, col_main = st.columns([1, 3])
        
        with col_side:
            mode = st.radio("اختر نوع الإدخال:", ["إضافة أحكام", "إضافة حضور محاميين"])
            st.divider()
            idx = st.number_input("الطعن الحالي (مسلسل رقم):", min_value=1, max_value=len(cases_list), value=st.session_state.current_case_idx + 1)
            st.session_state.current_case_idx = idx - 1
            curr_case = cases_list[st.session_state.current_case_idx]
            
        with col_main:
            st.subheader(f"📍 إدخال بيانات الطعن مسلسل ({curr_case['م']})")
            # عرض بيانات مرجعية للموظف
            st.info(f"**رقم الطعن:** {curr_case['رقم_الطعن']} لسنة {curr_case['السنة']} | **الطاعن:** {curr_case['الطاعن']}")
            
            if mode == "إضافة أحكام":
                val = st.text_area("منطوق الحكم:", value=curr_case.get('منطوق_الحكم', ""))
                if st.button("حفظ الحكم والذهاب للتالي (Enter)"):
                    # البحث عن الطعن الأصلي وتحديثه
                    for c in st.session_state.cases:
                        if c['رقم الطعن'] == curr_case['رقم_الطعن']: c['منطوق الحكم'] = val
                    if st.session_state.current_case_idx < len(cases_list) - 1:
                        st.session_state.current_case_idx += 1
                    st.rerun()
            else:
                val = st.text_area("حضور المحاميين:", value=curr_case.get('حضور_المحامين', ""))
                if st.button("حفظ الحضور والذهاب للتالي (Enter)"):
                    for c in st.session_state.cases:
                        if c['رقم الطعن'] == curr_case['رقم_الطعن']: c['حضور المحامين'] = val
                    if st.session_state.current_case_idx < len(cases_list) - 1:
                        st.session_state.current_case_idx += 1
                    st.rerun()

        st.divider()
        if st.button("📥 تحميل كافة المستندات النهائية (ورد)"):
            final_res = process_data()
            # (هنا نضع نفس كود DocxTemplate السابق للتحميل)
            st.success("جاهز للتحميل")
            st.dataframe(final_res)


