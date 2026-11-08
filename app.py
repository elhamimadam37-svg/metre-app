import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(page_title="تطبيق المترية وحديد التسليح الاحترافي", layout="wide")

# عرض اسمك في أعلى التطبيق بأسلوب مهني وأنيق
st.markdown("### 👷 Conçu et développé par : **ADAM ELHAMIM**")
st.title("🏗️ تطبيق المترية وحديد التسليح الشامل (الإصدار المهني المتكامل)")

FILE_METRE = "table_metre_pro.csv"
FILE_ACIER = "table_aciers_pro.csv"

# تحميل البيانات المحفوظة محلياً
def load_data():
    m, a = [], []
    if os.path.exists(FILE_METRE):
        try: m = pd.read_csv(FILE_METRE).to_dict('records')
        except: m = []
    if os.path.exists(FILE_ACIER):
        try: a = pd.read_csv(FILE_ACIER).to_dict('records')
        except: a = []
    return m, a

def save_data():
    pd.DataFrame(st.session_state.metre_rows).to_csv(FILE_METRE, index=False)
    pd.DataFrame(st.session_state.acier_rows).to_csv(FILE_ACIER, index=False)

if 'metre_rows' not in st.session_state or 'acier_rows' not in st.session_state:
    m_data, a_data = load_data()
    st.session_state.metre_rows = m_data
    st.session_state.acier_rows = a_data

# اختيار اسم المشروع في الشريط الجانبي
with st.sidebar:
    st.header("📁 إعدادات المشروع")
    project_name = st.text_input("اسم الورشة أو المشروع", "مشروع البناء الرئيسي")
    st.markdown("---")
    st.info("💡 التطبيق يحفظ البيانات تلقائياً ويدعم التصدير إلى Excel.")

tab1, tab2 = st.tabs([
    "📋 1. جدول المترية (Avant-Métré)", 
    "⚙️ 2. جدول الحديد والتوزيع (Aciers & Ventilation)"
])

# ==========================================
# 1. جدول المترية
# ==========================================
with tab1:
    st.subheader(f"📋 جدول المترية والمقادير - {project_name}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        m_n = st.text_input("N° بند", "1", key="mn_pro")
        m_desig = st.text_input("DESIGNATION DES OUVRAGES", "Fouille en pleine masse", key="md_pro")
        m_nombre = st.number_input("NOMBRE", min_value=0.0, value=1.0, key="mnb_pro")
    with col2:
        m_unite = st.selectbox("UNITE", ["m³", "m²", "ml", "Fft", "U"], key="mu_pro")
        m_l = st.number_input("Dimensions - L (طول)", min_value=0.0, value=5.0, key="ml_pro")
        m_w = st.number_input("Dimensions - l (عرض)", min_value=0.0, value=4.0, key="mw_pro")
    with col3:
        m_h = st.number_input("Dimensions - h/ép. (ارتفاع)", min_value=0.0, value=1.0, key="mh_pro")
        m_plus = st.number_input("QUANTITES - (+)", min_value=0.0, value=0.0, key="mp_pro")
        m_moins = st.number_input("QUANTITES - (-)", min_value=0.0, value=0.0, key="mm_pro")
    with col4:
        m_obs = st.text_input("OBSERVATION", "", key="mobs_pro")

    # الحسابات الهندسية للكمية
    dim_prod = m_l * (m_w if m_w > 0 else 1.0) * (m_h if m_h > 0 else 1.0)
    if m_w == 0 and m_h == 0:
        dim_prod = m_l
    elif m_w == 0:
        dim_prod = m_l * m_h
        
    partielle = (m_nombre * dim_prod) + m_plus - m_moins
    st.info(f"الكمية الجزئية البند (Partielle): **{partielle:.3f} {m_unite}**")

    if st.button("➕ إضافة بند جديد للمترية", key="add_m_pro"):
        st.session_state.metre_rows.append({
            "Project": project_name,
            "N°": m_n,
            "DESIGNATION DES OUVRAGES": m_desig,
            "NOMBRE": m_nombre,
            "UNITE": m_unite,
            "L": m_l,
            "l": m_w,
            "h/ép.": m_h,
            "+": m_plus,
            "-": m_moins,
            "Partielle": round(partielle, 3),
            "OBSERVATION": m_obs
        })
        save_data()
        st.success("تمت الإضافة بنجاح!")
        st.rerun()

    if len(st.session_state.metre_rows) > 0:
        st.markdown("---")
        df_m = pd.DataFrame(st.session_state.metre_rows)
        st.dataframe(df_m, use_container_width=True)

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("🗑️ مسح كاع بنود المترية", key="clr_m_pro"):
                st.session_state.metre_rows = []
                if os.path.exists(FILE_METRE): os.remove(FILE_METRE)
                st.rerun()
        with col_b2:
            out_m = io.BytesIO()
            with pd.ExcelWriter(out_m, engine='openpyxl') as writer:
                df_m.to_excel(writer, index=False, sheet_name='Avant-Metre')
            st.download_button("📥 تحميل ملف Excel للمترية", out_m.getvalue(), "Avant_Metre_Pro.xlsx")

# ==========================================
# 2. جدول الحديد (Aciers & Ventilation)
# ==========================================
with tab2:
    st.subheader(f"⚙️ جدول حديد التسليح والتهوية - {project_name}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        a_n = st.text_input("N° عنصر الحديد", "1", key="an_pro")
        a_desig = st.text_input("Désignation des travaux", "Semelle S1", key="ad_pro")
        a_nombre = st.number_input("Nombre d'éléments", min_value=1.0, value=1.0, key="anb_pro")
        a_nuance = st.text_input("Nuance", "FeE500", key="anu_pro")
    with col2:
        a_dia = st.selectbox("DIA Ø", [6, 8, 10, 12, 14, 16, 20], key="adia_pro")
        a_nbr_un = st.number_input("Nbr / un élément", min_value=1.0, value=4.0, key="anbu_pro")
        a_long_dev = st.number_input("Longueur développée (cm)", min_value=0.0, value=150.0, key="ald_pro")
    with col3:
        poids_unit = {6: 0.222, 8: 0.394, 10: 0.617, 12: 0.888, 14: 1.208, 16: 1.578, 20: 2.468}
        st.write(f"القطر المختار: **Ø{a_dia}**")
        st.write(f"الوزن الطولي: **{poids_unit[a_dia]} kg/m**")
        concrete_vol = st.number_input("حجم الخرسانة المقابل (m³) لاحتساب النسبة", min_value=0.0, value=1.0, key="c_vol")

    # حسابات الأوزان والأطوال
    nbre_total = a_nombre * a_nbr_un
    long_totale_cm = nbre_total * a_long_dev
    long_totale_m = long_totale_cm / 100.0
    poids_total_ligne = long_totale_m * poids_unit[a_dia]
    
    ratio_kg_m3 = (poids_total_ligne / concrete_vol) if concrete_vol > 0 else 0.0

    st.info(f"عدد الإجمالي: **{nbre_total}** | الطول الإجمالي: **{long_totale_m:.2f} m** | الوزن: **{poids_total_ligne:.2f} kg** | نسبة الحديد: **{ratio_kg_m3:.2f} kg/m³**")

    if st.button("➕ إضافة سطر الحديد", key="add_a_pro"):
        row = {
            "Project": project_name,
            "N°": a_n,
            "Désignation": a_desig,
            "Nombre": a_nombre,
            "Nuance": a_nuance,
            "DIA Ø": f"Ø{a_dia}",
            "Nbr/élm": a_nbr_un,
            "Nbre total": nbre_total,
            "Long. un (cm)": a_long_dev,
            "Long. tot (m)": round(long_totale_m, 2),
            "Ø6 (m)": long_totale_m if a_dia == 6 else 0.0,
            "Ø8 (m)": long_totale_m if a_dia == 8 else 0.0,
            "Ø10 (m)": long_totale_m if a_dia == 10 else 0.0,
            "Ø12 (m)": long_totale_m if a_dia == 12 else 0.0,
            "Ø14 (m)": long_totale_m if a_dia == 14 else 0.0,
            "Ø16 (m)": long_totale_m if a_dia == 16 else 0.0,
            "Ø20 (m)": long_totale_m if a_dia == 20 else 0.0,
            "Poids Total (kg)": round(poids_total_ligne, 2),
            "Ratio (kg/m³)": round(ratio_kg_m3, 2)
        }
        st.session_state.acier_rows.append(row)
        save_data()
        st.success("تمت إضافة سطر الحديد بنجاح!")
        st.rerun()

    if len(st.session_state.acier_rows) > 0:
        st.markdown("---")
        df_a = pd.DataFrame(st.session_state.acier_rows)
        st.dataframe(df_a, use_container_width=True)

        st.markdown("### 📊 ملخص الأوزان والتهوية حسب الأقطار (Ventilation):")
        
        sum_cols = ["Ø6 (m)", "Ø8 (m)", "Ø10 (m)", "Ø12 (m)", "Ø14 (m)", "Ø16 (m)", "Ø20 (m)"]
        diam_keys = [6, 8, 10, 12, 14, 16, 20]
        
        cols_ui = st.columns(len(diam_keys))
        total_global_weight = 0
        
        for idx, (col_n, d_val) in enumerate(zip(sum_cols, diam_keys)):
            tot_m_diam = df_a[col_n].sum()
            w_diam = tot_m_diam * poids_unit[d_val]
            total_global_weight += w_diam
            with cols_ui[idx]:
                st.metric(label=f"Ø{d_val}", value=f"{w_diam:.2f} kg")

        st.success(f"🔥 **Poids total d'acier (الوزن الإجمالي للحديد في الورشة): {total_global_weight:.2f} kg**")

        col_ba1, col_ba2 = st.columns(2)
        with col_ba1:
            if st.button("🗑️ مسح جدول الحديد", key="clr_a_pro"):
                st.session_state.acier_rows = []
                if os.path.exists(FILE_ACIER): os.remove(FILE_ACIER)
                st.rerun()
        with col_ba2:
            out_a = io.BytesIO()
            with pd.ExcelWriter(out_a, engine='openpyxl') as writer:
                df_a.to_excel(writer, index=False, sheet_name='Nomenclature-Aciers')
            st.download_button("📥 تحميل جدول الحديد Excel", out_a.getvalue(), "Nomenclature_Aciers_Pro.xlsx")
