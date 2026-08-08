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
        df_global = pd.DataFrame(semua_data)
        df_global.index = range(1, len(df_global) + 1)
        df_global.index.name = "Baris"
        
        c1, c2 = st.columns(2)
        c1.metric("Total Pencatatan", len(df_global))
        c2.metric("Total Keuntungan Keseluruhan", f"Rp {df_global['Keuntungan'].sum():,.0f}")
        
        kolom_tampil = ["User", "Periode", "Jenis_Tanaman", "Luas_Lahan", "Biaya_Lahan", "Biaya_Bibit", "Biaya_Pupuk", "Biaya_Perawatan", "Hasil_Panen_Kg", "Harga_Jual", "Keuntungan", "Status"]
        
        styled_df_global = df_global[kolom_tampil].style.set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#1b3312'), ('color', 'white'), ('text-align', 'center')]}
        ])
        
        st.write("Basis Data Lengkap (Semua Petani)")
        st.dataframe(styled_df_global, use_container_width=True)
        
        st.markdown("---")
        st.write("Tindakan: Hapus Data Transaksi")
        
        for i, item in enumerate(semua_data, 1):
            col_teks, col_tombol = st.columns([8, 2])
            col_teks.write(f"**Baris {i}**: {item.get('User', 'Unknown')} | {item['Periode']} | {item['Jenis_Tanaman']}")
            with col_tombol:
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
    else:
        st.info("Basis data transaksi kosong.")

with tab_users:
    st.subheader("Pengelolaan Akun Pengguna")
    semua_user = list(db.users.find({}, {"password": 0}))
    
    if semua_user:
        df_users = pd.DataFrame(semua_user)
        df_users.index = range(1, len(df_users) + 1)
        st.dataframe(df_users[['username', 'role']], use_container_width=True)
        
        st.markdown("---")
        st.write("Tindakan: Hapus Akun")
        
        for u in semua_user:
            cu_teks, cu_tombol = st.columns([8, 2])
            cu_teks.write(f"Akun: **{u['username']}** | Peran: {u['role']}")
            
            with cu_tombol:
                if u['username'] == 'admin':
                    st.write("-")
                else:
                    with st.popover("Hapus"):
                        st.write(f"Apakah Anda ingin menghapus data ini?")
                        uy, ut = st.columns(2)
                        with uy:
                            if st.button("Ya", key=f"yau_{u['_id']}", type="primary"):
                                db.users.delete_one({"_id": u['_id']})
                                db.pencatatan.delete_many({"User": u['username']})
                                st.rerun()
                        with ut:
                            if st.button("Tidak", key=f"tdku_{u['_id']}"):
                                st.rerun()
