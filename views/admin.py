import streamlit as st
import pandas as pd
from pymongo import MongoClient
from bson.objectid import ObjectId

if not st.session_state.get("logged_in") or st.session_state.get("role") != "admin":
    st.error("Akses Ditolak. Halaman ini khusus Administrator.")
    st.stop()

st.sidebar.info("Sistem Pemantauan Administrator Aktif")
if st.sidebar.button("Keluar (Logout)"):
    st.session_state.clear()
    st.rerun()

st.title("Panel Kendali Administrator")
st.write("Kelola aktivitas seluruh basis data produksi.")

@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongo"]["uri"])

client = init_connection()
db = client.pertanian_db

tab_data, tab_users = st.tabs(["Basis Data Transaksi", "Manajemen Akun"])

with tab_data:
    semua_data = list(db.pencatatan.find())
    if semua_data:
        df_global = pd.DataFrame(semua_data)
        df_global['_id'] = df_global['_id'].astype(str)
        
        c1, c2 = st.columns(2)
        c1.metric("Total Pencatatan", len(df_global))
        c2.metric("Total Keuntungan Keseluruhan", f"Rp {df_global['Keuntungan'].sum():,.0f}")
        
        st.dataframe(df_global, use_container_width=True)
        
        st.markdown("### Penghapusan Data Transaksi (Force Delete)")
        id_hapus = st.selectbox("Pilih ID Transaksi untuk dihapus", df_global['_id'].tolist())
        if st.button("Hapus Transaksi Secara Paksa", type="primary"):
            db.pencatatan.delete_one({"_id": ObjectId(id_hapus)})
            st.success("Transaksi berhasil dihapus dari sistem.")
            st.rerun()
    else:
        st.info("Basis data transaksi kosong.")

with tab_users:
    semua_user = list(db.users.find({}, {"password": 0}))
    if semua_user:
        df_users = pd.DataFrame(semua_user)
        df_users['_id'] = df_users['_id'].astype(str)
        st.dataframe(df_users, use_container_width=True)
        
        st.markdown("### Penghapusan Akun Pengguna")
        user_hapus = st.selectbox("Pilih Username yang akan dihapus", df_users['username'].tolist())
        if st.button("Hapus Akun Pengguna", type="primary"):
            if user_hapus == "admin":
                st.error("Akun Administrator utama tidak dapat dihapus.")
            else:
                db.users.delete_one({"username": user_hapus})
                db.pencatatan.delete_many({"User": user_hapus}) # Hapus juga semua data miliknya
                st.success(f"Akun {user_hapus} beserta datanya telah dihapus.")
                st.rerun()
