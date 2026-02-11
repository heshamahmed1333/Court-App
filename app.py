import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io

# 1. إعدادات أساسية
st.set_page_config(page_title="نظام سكرتارية النقض", layout="wide")
judges_names = ["نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق", "ماجد ابراهيم", "محسن أبو بكر", "حاتم غراب", "كمال عبد القوى", "محمد منصور", "محمد فؤاد"]

# 2. إدارة الذاكرة (Session State)
if 'cases' not in st.session_state: st.session_state.cases = []
if 'curr_idx' not in st.session_state: st.session_state.curr_idx = 0

# 3. الوظائف البرمجية (Functions)
def get_final_df():
    """هذه الدالة هي التي ترتب الجدول وتوزع المستشارين"""
    if not st.session_state.cases: return pd.DataFrame()
    data = []
    rank_map = {name: i for i, name in enumerate(judges_names)}
    
    for c in st.session_state.cases:
        row = c.copy()
        row['م1'], row['م2'], row['م3'] = "نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق"
        row['م4'], row['م5'], row['المقرر'], row['sort_idx'] = "", "", "", 999
        
        selected = []
        for j in judges_names:
            mark = str(c.get(j, "")).strip()
            if mark == "+":
                row['المقرر'] = j
                row['sort_idx'] = rank_map[j]
            elif mark == "-":
                if j not in ["نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق"]:
                    selected.append(j)
        
        if len(selected) >= 1: row['م4'] = selected[0]
        if len(selected) >= 2: row['م5'] = selected[1]
        data.append(row)
    
    df = pd.DataFrame(data).sort_values('sort_idx')
    df.insert(0, 'م', range(1, len(df) + 1))
    return df

# --- الشريط الجانبي (Sidebar) ---
with st.sidebar:
    st.header("💾 إدارة البيانات")
    up = st.file_uploader("رفع ملف إكسيل قديم", type="xlsx")
    if up:
        st.session_state.cases = pd.read_excel(up).fillna("").to_dict('records')
        st.success("تم التحميل!")

    if st.session_state.cases:
        towrite = io.BytesIO()
        pd.DataFrame(st.session_state.cases).to_excel(towrite, index=False)
        st.download_button("📥 حفظ العمل الحالي (Excel)", towrite.getvalue(), "backup.xlsx")
    
    st.divider()
    st.header("📝 إدخال طعن")
    c_no = st.text_input("رقم الطعن")
    c_yr = st.text_input("السنة")
    c_ap = st.text_input("الطاعن")
    if st.button("إضافة"):
        st.session_state.cases.append({'رقم الطعن':c_no, 'السنة':c_yr, 'اسم الطاعن':c_ap, 'منطوق الحكم':"", 'حضور المحامين':""})
        st.rerun()

# --- الواجهة الرئيسية ---
t1, t2 = st.tabs(["📑 تحضير (توزيع)", "🔨 تقفيل (أحكام)"])

with t1:
    if st.session_state.cases:
        df_p = pd.DataFrame(st.session_state.cases)
        for j in judges_names:
            if j not in df_p.columns: df_p[j] = ""
        
        # جدول التعديل (توزيع المستشارين)
        edited = st.data_editor(df_p, use_container_width=True, key="ed1")
        if st.button("حفظ التوزيع"):
            st.session_state.cases = edited.to_dict('records')
            st.success("تم الحفظ!")

with t2:
    df_f = get_final_df()
    if df_f.empty:
        st.warning("أدخل بيانات أولاً")
    else:
        cases_list = df_f.to_dict('records')
        
        # التنقل بين الطعون
        c_idx = st.number_input("الطعن الحالي (م)", 1, len(cases_list), value=st.session_state.curr_idx+1) - 1
        st.session_state.curr_idx = c_idx
        item = cases_list[st.session_state.curr_idx]
        
        st.info(f"الطعن: {item['رقم الطعن']} / {item['السنة']} | {item['اسم الطاعن']}")
        
        # خانات الإدخال
        col_a, col_b = st.columns(2)
        with col_a:
            hukm = st.text_area("منطوق الحكم", value=item.get('منطوق الحكم', ""))
        with col_b:
            hodoor = st.text_area("حضور المحامين", value=item.get('حضور المحامين', ""))
        
        if st.button("💾 حفظ البيانات والذهاب للتالي"):
            # تحديث البيانات في الذاكرة الأصلية
            for c in st.session_state.cases:
                if str(c['رقم الطعن']) == str(item['رقم الطعن']) and str(c['السنة']) == str(item['السنة']):
                    c['منطوق الحكم'] = hukm
                    c['حضور المحامين'] = hodoor
            
            if st.session_state.curr_idx < len(cases_list) - 1:
                st.session_state.curr_idx += 1
            st.success("تم الحفظ!")
            st.rerun()

    st.divider()
    st.subheader("📊 المعاينة النهائية والطباعة")
    if st.button("إظهار الجدول النهائي"):
        res = get_final_df()
        st.dataframe(res)
