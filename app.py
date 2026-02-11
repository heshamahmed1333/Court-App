import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام سكرتارية النقض", layout="wide")
st.title("⚖️ استكمال تقفيل الجلسة")

judges_names = ["نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق", "ماجد ابراهيم", "محسن أبو بكر", "حاتم غراب", "كمال عبد القوى", "محمد منصور", "محمد فؤاد"]

# 2. إدارة الذاكرة
if 'cases' not in st.session_state: st.session_state.cases = []
if 'curr_idx' not in st.session_state: st.session_state.curr_idx = 0

# 3. دالة المعالجة (بترتب الطعون بناءً على التوزيع اللي في الإكسيل المرفوع)
def get_final_df():
    if not st.session_state.cases: return pd.DataFrame()
    data = []
    rank_map = {name: i for i, name in enumerate(judges_names)}
    for c in st.session_state.cases:
        row = c.copy()
        # القيم الافتراضية للدوائر
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

# --- القائمة الجانبية (رفع الملف القديم) ---
with st.sidebar:
    st.header("📂 رفع ملف الجلسة")
    up = st.file_uploader("ارفع ملف الإكسيل المحضر سابقاً", type="xlsx")
    if up:
        # قراءة الملف وملء أي خانات فاضية بنصوص فارغة
        st.session_state.cases = pd.read_excel(up).fillna("").to_dict('records')
        st.success("تم رفع الملف وقراءة التوزيع!")
    
    if st.session_state.cases:
        st.divider()
        towrite = io.BytesIO()
        pd.DataFrame(st.session_state.cases).to_excel(towrite, index=False)
        st.download_button("📥 حفظ العمل الحالي (Excel)", towrite.getvalue(), "session_update.xlsx")

# --- واجهة الإدخال الذكية ---
if not st.session_state.cases:
    st.info("💡 ابدأ برفع ملف الإكسيل اللي حضرته قبل كده من القائمة الجانبية.")
else:
    tab1, tab2 = st.tabs(["🔨 إدخال الأحكام والحضور", "📊 المعاينة والطباعة"])

    with tab1:
        df_f = get_final_df()
        cases_list = df_f.to_dict('records')
        
        # اختيار الطعن
        idx = st.number_input("المسلسل (م)", 1, len(cases_list), value=st.session_state.curr_idx + 1) - 1
        st.session_state.curr_idx = idx
        curr = cases_list[st.session_state.curr_idx]
        
        # عرض معلومات الطعن بالكامل (عشان الموظف يتأكد)
        st.warning(f"📍 طعن {curr['رقم_الطعن']} / {curr['السنة']} | طاعن: {curr['الطاعن']} | مقرر: {curr['المقرر']}")
        st.write(f"🏢 المحكمة: {curr['المحكمة']} | 📝 التهمة: {curr['التهمة']}")
        
        col_h, col_ho = st.columns(2)
        with col_h:
            h_val = st.text_area("منطوق الحكم", value=curr.get('منطوق_الحكم', ""), key=f"h_{idx}", height=150)
        with col_ho:
            ho_val = st.text_area("حضور المحامين", value=curr.get('حضور_المحامين', ""), key=f"ho_{idx}", height=150)
            
        if st.button("💾 حفظ البيانات"):
            # تحديث الذاكرة الأصلية
            for c in st.session_state.cases:
                # بنربط بالرقم والسنة عشان نضمن الدقة
                if str(c.get('رقم الطعن')) == str(curr['رقم_الطعن']) and str(c.get('السنة')) == str(curr['السنة']):
                    c['منطوق الحكم'] = h_val
                    c['حضور المحامين'] = ho_val
            
            st.toast("✅ تم الحفظ في الجدول")
            st.rerun()

        st.divider()
        st.subheader("📊 الجدول المحدث")
        st.dataframe(get_final_df(), use_container_width=True)

    with tab2:
        final_res = get_final_df()
        st.dataframe(final_res, use_container_width=True)
        # هنا تضع أكواد تحميل الـ Word (الرول، المحاضر، الوقائع)
