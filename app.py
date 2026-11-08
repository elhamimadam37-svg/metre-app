import streamlit as st
import pandas as pd
import io
import os

# إعدادات الصفحة
st.set_page_config(page_title="تطبيق المترية وحفظ البيانات", layout="wide")

st.title("🏗️ تطبيق المترية الشامل والتلقائي (Avant-Métré & Aciers)")
st.write("حساب تلقائي للكميات والأوزان، حفظ دائم للبيانات محلياً، وتصدير مباشر إلى Excel.")

# أسماء ملفات الحفظ المحلي
FILE_METRE = "saved_metre_data.csv"
FILE_ACIER = "saved_acier_data.csv"

# دالة لتحميل البيانات المحفوظة محلياً عند بدء التطبيق
def load_data():
    metre_list = []
    acier_list = []
    
    if os.path.exists(FILE_METRE):
        try:
            df_m = pd.read_csv(FILE_METRE)
            metre_list = df_m.to_dict('records')
        except Exception:
            metre_list = []
            
    if os.path.exists(FILE_ACIER):
        try:
            df_a = pd.read_csv(FILE_ACIER)
            acier_list = df_a.to_dict('records')
        except Exception:
            acier_list = []
            
    return metre_list, acier_list

# دالة لحفظ البيانات محلياً
def save_data():
    df_m = pd.DataFrame(st.session_state.metre_data)
    df_m.to_csv(FILE_METRE, index=False)
    
    df_a = pd.DataFrame(st.session_state.acier_data)
    df_a.to_csv(FILE_ACIER, index=False)

# تهيئة الحالات في Session State
if 'metre_data' not in st.session_state or 'acier_data' not in st.session_state:
    m_data, a_data = load_data()
    st.session_state.metre_data = m_data
    st.session_state.acier_data = a_data

# تقسيم التطبيق إلى تبويبات
main_tab1, main_tab2 = st.tabs([
    "📊 1. جدول المترية العامة (Avant-Métré)", 
    "⚙️ 2. جدول تفصيل الحديد (Elements en Aciers)"
])

# ==========================================
# 1. جدول المترية العامة
# ==========================================
with main_tab1:
    st.subheader("📋 إدخال وحساب عناصر المترية تلقائياً")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        m_num = st.text_input("رقم البند (N°)", "1", key="m_num")
        m_desig = st.text_input("وصف العمل (Désignation)", "Fouille en pleine masse", key="m_desig")
        m_nombre = st.number_input("العدد (Nombre)", min_value=1.0, value=1.0, step=1.0, key="m_nombre")
    with col2:
        m_unite = st.selectbox("الوحدة (Unité)", ["m³", "m²", "ml", "Fft", "U"], key="m_unite")
        m_l = st.number_input("الطول L (m)", min_value=0.0, value=5.0, step=0.1, key="m_l")
        m_w = st.number_input("العرض l (m)", min_value=0.0, value=4.0, step=0.1, key="m_w")
    with col3:
        m_h = st.number_input("الارتفاع/السماكة h/ép (m)", min_value=0.0, value=1.0, step=0.1, key="m_h")
        m_plus = st.number_input("إضافة (+)", min_value=0.0, value=0.0, step=0.1, key="m_plus")
        m_moins = st.number_input("خصم (-)", min_value=0.0, value=0.0, step=0.1, key="m_moins")
        m_obs = st.text_input("ملاحظات (Observation)", "", key="m_obs")

    # الحساب التلقائي للكمية الجزئية
    base_calc = m_nombre * m_l * (m_w if m_w > 0 else 1.0) * (m_h if m_h > 0 else 1.0)
    if m_w == 0 and m_h == 0:
        base_calc = m_nombre * m_l
    elif m_w == 0:
        base_calc = m_nombre * m_l * m_h

    partielle_auto = base_calc + m_plus - m_moins
    st.info(f"💡 النتيجة الحسابية التلقائية: **{partielle_auto:.3f} {m_unite}**")

    if st.button("💾 حفظ وإضافة البند", key="add_metre"):
        st.session_state.metre_data.append({
            "N°": m_num,
            "DESIGNATION DES OUVRAGES": m_desig,
            "NOMBRE": m_nombre,
            "UNITE": m_unite,
            "L": m_l,
            "l": m_w,
            "h/ép": m_h,
            "+": m_plus,
            "-": m_moins,
            "Partielle": round(partielle_auto, 3),
            "Totale": round(partielle_auto, 3),
            "OBSERVATION": m_obs
        })
        save_data() # حفظ في CSV محلياً
        st.success("تمت الإضافة والحفظ تلقائياً!")
        st.rerun()

    if len(st.session_state.metre_data) > 0:
        st.markdown("---")
        st.subheader("📋 الجدول العام الحالي")
        df_m = pd.DataFrame(st.session_state.metre_data)
        st.dataframe(df_m, use_container_width=True)

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("🗑️ مسح الجدول وحذف الملف المحفوظ", key="clear_m"):
                st.session_state.metre_data = []
                if os.path.exists(FILE_METRE):
                    os.remove(FILE_METRE)
                st.rerun()

        with col_b2:
            output_m = io.BytesIO()
            with pd.ExcelWriter(output_m, engine='openpyxl') as writer:
                df_m.to_excel(writer, index=False, sheet_name='Avant-Metre')
            
            st.download_button(
                label="📥 تصدير جدول المترية إلى Excel (.xlsx)",
                data=output_m.getvalue(),
                file_name="Avant_Metre_General.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# ==========================================
# 2. جدول حديد التسليح
# ==========================================
with main_tab2:
    st.subheader("⚙️ إدخال وحساب أوزان حديد التسليح تلقائياً")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        a_num = st.text_input("رقم البند (N°)", "1", key="a_num")
        a_desig = st.text_input("تسمية العنصر", "Semelle S1", key="a_desig")
        a_nombre = st.number_input("العدد الإجمالي للعناصر", min_value=1.0, value=1.0, step=1.0, key="a_nombre")
        a_nuance = st.text_input("نوع الحديد (Nuance)", "FeE500", key="a_nuance")
    with col2:
        a_dia = st.selectbox("القطر (DIA Ø)", [6, 8, 10, 12, 14, 16, 20], key="a_dia")
        a_nbre_un = st.number_input("عدد القضبان في العنصر", min_value=1.0, value=4.0, step=1.0, key="a_nbre_un")
        a_long_dev = st.number_input("الطول المطوّر للقضيب (cm)", min_value=0.0, value=150.0, step=5.0, key="a_long_dev")
    with col3:
        poids_unit_dict = {6: 0.222, 8: 0.394, 10: 0.617, 12: 0.888, 14: 1.208, 16: 1.578, 20: 2.468}
        st.write(f"القطر المحدد: **Ø{a_dia}**")
        st.write(f"الوزن النظري: **{poids_unit_dict[a_dia]} kg/m**")

    # الحساب التلقائي للحديد
    nbre_total_bars = a_nombre * a_nbre_un
    longueur_totale_m = (nbre_total_bars * a_long_dev) / 100.0
    poids_total_diam = longueur_totale_m * poids_unit_dict[a_dia]

    st.info(f"💡 النتيجة: **{nbre_total_bars} قضيب** | الطول الإجمالي: **{longueur_totale_m:.2f} m** | الوزن: **{poids_total_diam:.2f} kg**")

    if st.button("💾 حفظ وإضافة لعناصر الحديد", key="add_acier"):
        row_data = {
            "N°": a_num,
            "Désignation des travaux": a_desig,
            "Nombre": a_nombre,
            "Nuance": a_nuance,
            "DIA Ø": f"Ø{a_dia}",
            "Nbr / un élément": a_nbre_un,
            "Nbre total": nbre_total_bars,
            "Longueur développée (cm)": a_long_dev,
            "Longueur totale (cm)": nbre_total_bars * a_long_dev,
            "Ø6 (m)": longueur_totale_m if a_dia == 6 else 0.0,
            "Ø8 (m)": longueur_totale_m if a_dia == 8 else 0.0,
            "Ø10 (m)": longueur_totale_m if a_dia == 10 else 0.0,
            "Ø12 (m)": longueur_totale_m if a_dia == 12 else 0.0,
            "Ø14 (m)": longueur_totale_m if a_dia == 14 else 0.0,
            "Ø16 (m)": longueur_totale_m if a_dia == 16 else 0.0,
            "Ø20 (m)": longueur_totale_m if a_dia == 20 else 0.0,
            "Poids Total (kg)": round(poids_total_diam, 2)
        }
        st.session_state.acier_data.append(row_data)
        save_data() # حفظ في CSV محلياً
        st.success("تمت الإضافة والحفظ بنجاح!")
        st.rerun()

    if len(st.session_state.acier_data) > 0:
        st.markdown("---")
        st.subheader("⚙️ جدول تفصيل أوزان الحديد")
        df_a = pd.DataFrame(st.session_state.acier_data)
        st.dataframe(df_a, use_container_width=True)

        # حساب مجموع الأوزان الإجمالية لكل قطر تلقائياً
        sum_cols = ["Ø6 (m)", "Ø8 (m)", "Ø10 (m)", "Ø12 (m)", "Ø14 (m)", "Ø16 (m)", "Ø20 (m)"]
        diam_keys = [6, 8, 10, 12, 14, 16, 20]
        
        st.markdown("### 📊 ملخص الأوزان حسب الأقطار:")
        col_res = st.columns(len(diam_keys))
        total_global_acier = 0
        
        for idx, (col_name, d_val) in enumerate(zip(sum_cols, diam_keys)):
            tot_m = df_a[col_name].sum()
            weight = tot_m * poids_unit_dict[d_val]
            total_global_acier += weight
            with col_res[idx]:
                st.metric(label=f"Ø{d_val}", value=f"{weight:.1f} kg")

        st.success(f"🔥 **مجموع وزن الحديد الكامل للورش (Total Aciers): {total_global_acier:.2f} kg**")

        col_ba1, col_ba2 = st.columns(2)
        with col_ba1:
            if st.button("🗑️ مسح جدول الحديد وحذف المحفوظات", key="clear_a"):
                st.session_state.acier_data = []
                if os.path.exists(FILE_ACIER):
                    os.remove(FILE_ACIER)
                st.rerun()

        with col_ba2:
            output_a = io.BytesIO()
            with pd.ExcelWriter(output_a, engine='openpyxl') as writer:
                df_a.to_excel(writer, index=False, sheet_name='Aciers')
            
            st.download_button(
                label="📥 تصدير جدول الحديد إلى Excel (.xlsx)",
                data=output_a.getvalue(),
                file_name="Nomenclature_Aciers.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
