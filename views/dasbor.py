import streamlit as st
import pandas as pd
import numpy as np
from pymongo import MongoClient
from bson.objectid import ObjectId

# Proteksi Akses Lapis Kedua
if not st.session_state.get("logged_in") or st.session_state.get("role") == "admin":
    st.warning("Akses ditolak.")
    st.stop()

user_aktif = st.session_state.username

st.sidebar.success(f"Petani Aktif: {user_aktif}")
if st.sidebar.button("Keluar (Logout)"):
    st.session_state.clear()
    st.rerun()

@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongo"]["uri"])

client = init_connection()
db = client.pertanian_db
collection = db.pencatatan

st.title("Dasbor Manajemen Produksi")
st.write("Catat, analisis, dan proyeksikan hasil pertanian Anda.")

tab1, tab2, tab3, tab4 = st.tabs(["Pencatatan Baru", "Manajemen Data (CRUD)", "Kalkulasi & Prediksi", "Visualisasi"])

with tab1:
    st.subheader("Formulir Data Produksi")
    col_p1, col_p2, col_p3 = st.columns(3)
    daftar_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    
    with col_p1: bulan_tanam = st.selectbox("Bulan Tanam", daftar_bulan, index=3)
    with col_p2: bulan_panen = st.selectbox("Bulan Panen", daftar_bulan, index=4)
    with col_p3: tahun_periode = st.number_input("Tahun", min_value=2020, max_value=2050, value=2026)
    
    periode = f"{bulan_tanam} - {bulan_panen} {tahun_periode}"
    jenis_tanaman = st.selectbox("Jenis Komoditas Tanaman", ["Cabai Merah", "Bawang Merah", "Jagung", "Lainnya"])
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        luas_lahan = st.number_input("Luas Lahan Tanam (m2)", min_value=1.0, value=1000.0)
        b_lahan = st.number_input("Biaya Pengolahan Lahan (Rp)", min_value=0)
        b_bibit = st.number_input("Biaya Bibit (Rp)", min_value=0)
    with col2:
        hasil_kg = st.number_input("Hasil Panen Aktual (Kg)", min_value=0.0)
        b_pupuk = st.number_input("Biaya Pupuk (Rp)", min_value=0)
        b_perawatan = st.number_input("Biaya Perawatan (Rp)", min_value=0)
        
    harga_jual = st.number_input("Harga Jual Per Kg (Rp)", min_value=0)
    
    total_biaya = b_lahan + b_bibit + b_pupuk + b_perawatan
    pendapatan = hasil_kg * harga_jual
    keuntungan = pendapatan - total_biaya
    status = "UNTUNG" if keuntungan > 0 else "RUGI"
    
    st.info(f"Estimasi Keuntungan: Rp {keuntungan:,.0f} | Status: {status}")

    if st.button("Simpan Data Pencatatan", type="primary"):
        dokumen = {
            "User": user_aktif, "Periode": periode, "Jenis_Tanaman": jenis_tanaman,
            "Luas_Lahan": luas_lahan, "Biaya_Lahan": b_lahan, "Biaya_Bibit": b_bibit,
            "Biaya_Pupuk": b_pupuk, "Biaya_Perawatan": b_perawatan, "Hasil_Panen_Kg": hasil_kg,
            "Harga_Jual": harga_jual, "Keuntungan": keuntungan, "Status": status
        }
        collection.insert_one(dokumen)
        st.success("Data berhasil disimpan ke basis data.")

with tab2:
    st.subheader("Manajemen Rekam Jejak (Update & Delete)")
    data_hist = list(collection.find({"User": user_aktif}))
    
    if data_hist:
        df_edit = pd.DataFrame(data_hist)
        df_edit['_id'] = df_edit['_id'].astype(str)
        st.dataframe(df_edit.drop(columns=["User"]), use_container_width=True)
        
        st.markdown("#### Hapus Data Permanen")
        id_to_delete = st.selectbox("Pilih ID Data yang akan dihapus", df_edit['_id'].tolist())
        if st.button("Hapus Data Terpilih"):
            collection.delete_one({"_id": ObjectId(id_to_delete)})
            st.success("Data berhasil dihapus. Silakan muat ulang halaman.")
            st.rerun()
    else:
        st.write("Belum ada data untuk dikelola.")

with tab3:
    st.subheader("Modul Prediksi dan Kalkulasi")
    metode_prediksi = st.radio("Pilih Algoritma Prediksi", 
                               ["Metode Ubinan (Sampel Acak)", 
                                "Interpolasi Linear (Historis Tunggal)", 
                                "Ekstrapolasi Matematis Berjenjang"], horizontal=True)
    
    st.markdown("---")
    
    if metode_prediksi == "Metode Ubinan (Sampel Acak)":
        c_u1, c_u2 = st.columns(2)
        with c_u1:
            luas_total = st.number_input("Luas Keseluruhan Lahan (m2)", value=1000.0)
            luas_ubin = st.number_input("Luas Kotak Ubinan (m2)", value=6.25)
        with c_u2:
            berat_ubin = st.number_input("Berat Panen dalam Ubinan (Kg)", value=5.0)
        
        if luas_ubin > 0:
            pred = (luas_total / luas_ubin) * berat_ubin
            st.metric("Total Prediksi Panen", f"{pred:,.2f} Kg")
            
    elif metode_prediksi == "Interpolasi Linear (Historis Tunggal)":
        data_hist = list(collection.find({"User": user_aktif}).sort("_id", 1))
        if len(data_hist) >= 2:
            x_hist = [d.get('Luas_Lahan', 1000) for d in data_hist]
            y_hist = [d['Hasil_Panen_Kg'] for d in data_hist]
            
            luas_target = st.number_input("Luas Lahan yang Direncanakan (m2)", value=1500.0)
            hasil_interp = np.interp(luas_target, x_hist, y_hist)
            st.metric("Prediksi Interpolasi", f"{hasil_interp:,.2f} Kg")
        else:
            st.warning("Dibutuhkan minimal 2 rekaman data sebelumnya.")
            
    elif metode_prediksi == "Ekstrapolasi Matematis Berjenjang":
        data_hist = list(collection.find({"User": user_aktif}).sort("_id", 1))
        if len(data_hist) >= 2:
            x_hist = [d.get('Luas_Lahan', 1000) for d in data_hist]
            y_hist = [d['Hasil_Panen_Kg'] for d in data_hist]
            
            x1, y1 = x_hist[-2], y_hist[-2]
            x2, y2 = x_hist[-1], y_hist[-1]
            
            col_target, col_partisi = st.columns(2)
            with col_target:
                target_luas = st.number_input("Target Luas Lahan (m2)", value=2000.0)
            with col_partisi:
                jumlah_partisi = st.number_input("Jumlah Partisi Iterasi", min_value=1, max_value=36, value=10)
                
            st.latex(r"y = y_1 + \frac{(x - x_1)(y_2 - y_1)}{(x_2 - x_1)}")
            
            if x2 - x1 == 0:
                st.error("Titik koordinat x1 dan x2 bernilai sama. Gradien tidak terdefinisi.")
            else:
                gradien = (y2 - y1) / (x2 - x1)
                st.write(f"- Titik Dasar 1: ({x1} m², {y1} Kg)")
                st.write(f"- Titik Dasar 2: ({x2} m², {y2} Kg)")
                st.write(f"- Gradien Fungsi: {gradien:.4f}")
                
                selisih_total = target_luas - x2
                step_increment = selisih_total / jumlah_partisi
                
                st.write("**Rincian Iterasi Partisi Ekstrapolasi:**")
                for i in range(1, jumlah_partisi + 1):
                    x_step = x2 + (step_increment * i)
                    y_step = y1 + ((x_step - x1) * gradien)
                    st.write(f"Partisi ke-{i}: Luas Lahan = {x_step:.2f} m² $\\rightarrow$ Proyeksi Panen = {y_step:.2f} Kg")
                
                y_final = y1 + ((target_luas - x1) * gradien)
                st.success(f"Kesimpulan: Target Luas Lahan {target_luas} m² diproyeksikan menghasilkan {y_final:.2f} Kg.")
        else:
            st.warning("Dibutuhkan minimal 2 rekaman data historis.")

with tab4:
    st.subheader("Visualisasi Keuangan Produksi")
    data_hist = list(collection.find({"User": user_aktif}))
    if data_hist:
        df_vis = pd.DataFrame(data_hist)
        st.line_chart(df_vis.set_index("Periode")["Keuntungan"])
    else:
        st.write("Belum ada data untuk ditampilkan.")
