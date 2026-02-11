import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io

# 1. إعدادات أساسية
st.set_page_config(page_title="نظام سكرتارية النقض", layout="wide")
judges_names = ["نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق", "ماجد ابراهيم", "محسن أبو بكر", "حاتم غراب", "كمال عبد القوى", "محمد منصور", "محمد فؤاد"]

# 2. إدارة الذاكرة
if 'cases' not in st.session_state: st.session_state.cases = []
if 'curr_idx' not in st.session_state: st.session_state.curr_idx = 0

# 3. دالة المعالجة الأساسية
def get_final_df():
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
                if j not in ["نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق"]: selected.append(j)
        if len(selected) >= 1: row['م4'] = selected[0]
        if len(selected) >= 2: row['م5'] = selected[1]
        data.append(row)
    df = pd.DataFrame(data).sort_values('sort_idx')
    df.insert(0, 'م', range(1, len(df) + 1))
    return df

# --- الشريط الجانبي ---
with st.sidebar:
    st.header("💾 إدارة البيانات")
    up = st.file_uploader("رفع ملف إكسيل", type="xlsx")
    if up:
        st.session_state.cases = pd.read_excel(up).fillna("").to_dict('records')
        st.rerun()

    if st.session_state.cases:
        towrite = io.BytesIO()
        pd.DataFrame(st.session_state.cases).to_excel(towrite, index=False)
        st.download_button("📥 حفظ وتنزيل النسخة الحالية", towrite.getvalue(), "session_backup.xlsx")
    
    st.divider()
    st.header("📝 إدخال طعن جديد")
    c_no = st.text_input("رقم الطعن")
    c_yr = st.text_input("السنة")
    c_ap = st.text_input("الطاعن")
    c_ct = st.text_input("المحكمة المصدر")
    c_ch = st.text_input("التهمة")
    if st.button("إضافة الطعن"):
        st.session_state.cases.append({
            'رقم الطعن': c_no, 'السنة': c_yr, 'اسم الطاعن': c_ap, 
            'المحكمة المصدر': c_ct, 'التهمة': c_ch, 
            'منطوق الحكم': "", 'حضور المحامين': ""
        })
        st.rerun()

# --- الواجهة الرئيسية ---
t1, t2 = st.tabs(["📑 1. تحضير الجلسة", "🔨 2. تقفيل الجلسة"])

with t1:
    if st.session_state.cases:
        st.subheader("جدول تحضير الجلسة وتوزيع المستشارين")
        df_p = pd.DataFrame(st.session_state.cases)
        cols = ['رقم الطعن', 'السنة', 'اسم الطاعن', 'المحكمة المصدر', 'التهمة'] + judges_names
        for col in cols:
            if col not in df_p.columns: df_p[col] = ""
        edited = st.data_editor(df_p[cols], use_container_width=True, key="ed_prep")
        if st.button("💾 حفظ التوزيع"):
            st.session_state.cases = edited.to_dict('records')
            st.success("تم الحفظ!")

with t2:
    df_f = get_final_df()
    if df_f.empty:
        st.warning("أدخل بيانات أولاً.")
    else:
        cases_list = df_f.to_dict('records')
        
        # منطقة الإدخال العلوي
        st.subheader("🔨 منطقة تقفيل الجلسة")
        c_idx = st.number_input("المسلسل الحالي (م)", 1, len(cases_list), value=st.session_state.curr_idx+1) - 1
        st.session_state.curr_idx = c_idx
        item = cases_list[st.session_state.curr_idx]
        
        st.info(f"📍 طعن رقم: {item['رقم الطعن']} لسنة {item['السنة']} | {item['اسم الطاعن']}")
        
        col_a, col_b = st.columns(2)
        with col_a:
            # تم إصلاح الخطأ البرمجي هنا (Syntax Error fix)
            key_h = f"hukm_{item['رقم الطعن']}_{item['السنة']}"
            hukm = st.text_area("منطوق الحكم", value=item.get('منطوق الحكم', ""), key=key_h)
        with col_b:
            key_ho = f"hodoor_{item['رقم الطعن']}_{item['السنة']}"
            hodoor = st.text_area("حضور المحامين", value=item.get('حضور المحامين', ""), key=key_ho)
        
        if st.button("💾 حفظ البيانات"):
            # تحديث الذاكرة
            for c in st.session_state.cases:
                if str(c['رقم الطعن']) == str(item['رقم الطعن']) and str(c['السنة']) == str(item['السنة']):
                    c['منطوق الحكم'] = hukm
                    c['حضور المحامين'] = hodoor
            st.toast("تم الحفظ بنجاح!")
            st.rerun()

        # --- المعاينة الفورية ---
        st.divider()
        st.subheader("📊 معاينة فورية لجدول الجلسة")
        st.dataframe(get_final_df(), use_container_width=True)
