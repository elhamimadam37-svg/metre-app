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
        save_
