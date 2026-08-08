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
    st.subheader("Pengelolaan Data Transaksi")
    semua_data = list(db.pencatatan.find())
    
    if semua_data:
        # Header Tabel Kustom
        col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns([2, 2, 2, 2, 2])
        col_h1.markdown("**User**")
        col_h2.markdown("**Periode**")
        col_h3.markdown("**Tanaman**")
        col_h4.markdown("**Keuntungan (Rp)**")
        col_h5.markdown("**Aksi**")
        st.markdown("---")
        
        for item in semua_data:
            c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 2, 2])
            c1.write(item.get('User', 'Unknown'))
            c2.write(item['Periode'])
            c3.write(item['Jenis_Tanaman'])
            c4.write(f"{item['Keuntungan']:,.0f}")
            
            with c5:
                with st.popover("Hapus"):
                    st.write("Apakah Anda ingin menghapus data ini?")
                    col_ya, col_tidak = st.columns(2)
                    with col_ya:
                        if st.button("Ya", key=f"yad_{item['_id']}", type="primary"):
                            db.pencatatan.delete_one({"_id": item['_id']})
                            st.rerun()
                    with col_tidak:
                        if st.button("Tidak", key=f"tdkd_{item['_id']}"):
                            st.rerun()
            st.markdown("<hr style='margin:0px; padding:0px; opacity: 0.3;'>", unsafe_allow_html=True)
    else:
        st.info("Basis data transaksi kosong.")

with tab_users:
    st.subheader("Pengelolaan Akun Pengguna")
    semua_user = list(db.users.find({}, {"password": 0}))
    
    if semua_user:
        u_h1, u_h2, u_h3 = st.columns([3, 3, 3])
        u_h1.markdown("**Username**")
        u_h2.markdown("**Role (Peran)**")
        u_h3.markdown("**Aksi**")
        st.markdown("---")
        
        for u in semua_user:
            uc1, uc2, uc3 = st.columns([3, 3, 3])
            uc1.write(u['username'])
            uc2.write(u['role'])
            
            with uc3:
                if u['username'] == 'admin':
                    st.write("-")
                else:
                    with st.popover("Hapus"):
                        st.write(f"Apakah Anda ingin menghapus pengguna {u['username']} beserta seluruh datanya?")
                        uy, ut = st.columns(2)
                        with uy:
                            if st.button("Ya", key=f"yau_{u['_id']}", type="primary"):
                                db.users.delete_one({"_id": u['_id']})
                                db.pencatatan.delete_many({"User": u['username']})
                                st.rerun()
                        with ut:
                            if st.button("Tidak", key=f"tdku_{u['_id']}"):
                                st.rerun()
            st.markdown("<hr style='margin:0px; padding:0px; opacity: 0.3;'>", unsafe_allow_html=True)
