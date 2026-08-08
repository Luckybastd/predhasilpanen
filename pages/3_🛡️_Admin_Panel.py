import streamlit as st
import pandas as pd
from pymongo import MongoClient

st.set_page_config(page_title="TANIKITA | Admin", page_icon="🛡️", layout="wide")

# Proteksi Lapis Ganda: Hanya user dengan role 'admin' yang bisa masuk
if 'logged_in' not in st.session_state or st.session_state.get('role') != 'admin':
    st.error("⛔ Akses Terlarang. Halaman ini hanya diperuntukkan bagi Administrator Sistem.")
    st.stop()

st.title("🛡️ Panel Kendali Administrator")
st.write("Sistem Pemantauan Global TANIKITA")

@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongo"]["uri"])

client = init_connection()
db = client.pertanian_db

# Mengambil semua data tanpa filter user
semua_data = list(db.pencatatan.find({}, {"_id": 0}))
semua_user = list(db.users.find({}, {"_id": 0, "password": 0}))

col1, col2, col3 = st.columns(3)
col1.metric("Total Pengguna Terdaftar", len(semua_user))
col2.metric("Total Transaksi Tercatat", len(semua_data))

if semua_data:
    df_global = pd.DataFrame(semua_data)
    total_omset = df_global['Keuntungan'].sum()
    col3.metric("Total Sirkulasi Keuntungan Global", f"Rp {total_omset:,.0f}")
    
    st.markdown("### 🗃️ Basis Data Global (Seluruh Petani)")
    df_global.index = range(1, len(df_global) + 1)
    
    # Fitur hapus data (Contoh simulasi operasional database)
    user_to_filter = st.selectbox("Saring berdasarkan Pengguna", ["Semua Pengguna"] + list(df_global['User'].unique()))
    
    if user_to_filter != "Semua Pengguna":
        st.dataframe(df_global[df_global['User'] == user_to_filter], use_container_width=True)
    else:
        st.dataframe(df_global, use_container_width=True)
        
    st.markdown("### 👥 Daftar Akun Sistem")
    st.dataframe(pd.DataFrame(semua_user), use_container_width=True)
else:
    col3.metric("Total Sirkulasi Keuntungan Global", "Rp 0")
    st.info("Basis data operasional masih kosong.")
