import streamlit as st
import pandas as pd
from pymongo import MongoClient

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
        df_global["Tandai Hapus"] = False
        
        c1, c2 = st.columns(2)
        c1.metric("Total Pencatatan", len(df_global))
        c2.metric("Total Keuntungan Keseluruhan", f"Rp {df_global['Keuntungan'].sum():,.0f}")
        
        kolom_tampil = ["User", "Periode", "Jenis_Tanaman", "Luas_Lahan", "Biaya_Lahan", "Biaya_Bibit", "Biaya_Pupuk", "Biaya_Perawatan", "Hasil_Panen_Kg", "Harga_Jual", "Keuntungan", "Status", "Tandai Hapus"]
        df_tampil_global = df_global[kolom_tampil]
        
        st.write("Centang kotak pada kolom paling kanan untuk menghapus transaksi dari server.")
        edited_global = st.data_editor(
            df_tampil_global,
            use_container_width=True,
            disabled=["User", "Periode", "Jenis_Tanaman", "Luas_Lahan", "Biaya_Lahan", "Biaya_Bibit", "Biaya_Pupuk", "Biaya_Perawatan", "Hasil_Panen_Kg", "Harga_Jual", "Keuntungan", "Status"],
            column_config={
                "Tandai Hapus": st.column_config.CheckboxColumn("Tandai Hapus", default=False)
            }
        )
        
        baris_dihapus_global = edited_global[edited_global["Tandai Hapus"] == True]
        if not baris_dihapus_global.empty:
            st.markdown("---")
            with st.popover("Konfirmasi Penghapusan Data"):
                st.write("Apakah anda ingin menghapus data ini?")
                col_ya, col_tidak = st.columns(2)
                with col_ya:
                    if st.button("Ya", type="primary"):
                        for idx in baris_dihapus_global.index:
                            id_dok = df_global.loc[idx, '_id']
                            db.pencatatan.delete_one({"_id": id_dok})
                        st.rerun()
                with col_tidak:
                    if st.button("Tidak"):
                        st.rerun()
    else:
        st.info("Basis data transaksi kosong.")

with tab_users:
    st.subheader("Pengelolaan Akun Pengguna")
    semua_user = list(db.users.find({}, {"password": 0}))
    
    if semua_user:
        df_users = pd.DataFrame(semua_user)
        df_users.index = range(1, len(df_users) + 1)
        df_users["Tandai Hapus"] = False
        
        st.write("Centang kotak pada kolom paling kanan untuk menghapus pengguna beserta seluruh datanya.")
        edited_users = st.data_editor(
            df_users[["username", "role", "Tandai Hapus"]],
            use_container_width=True,
            disabled=["username", "role"],
            column_config={
                "Tandai Hapus": st.column_config.CheckboxColumn("Tandai Hapus", default=False)
            }
        )
        
        user_dihapus = edited_users[edited_users["Hapus Data"] == True]
        if not user_dihapus.empty:
            st.markdown("---")
            with st.popover("Konfirmasi Penghapusan Pengguna"):
                st.write("Apakah anda ingin menghapus pengguna ini beserta datanya?")
                col_y, col_t = st.columns(2)
                with col_y:
                    if st.button("Ya", type="primary"):
                        for idx in user_dihapus.index:
                            nama_user = df_users.loc[idx, 'username']
                            id_user = df_users.loc[idx, '_id']
                            if nama_user != 'admin':
                                db.users.delete_one({"_id": id_user})
                                db.pencatatan.delete_many({"User": nama_user})
                        st.rerun()
                with col_t:
                    if st.button("Tidak", key="batal_user"):
                        st.rerun()
