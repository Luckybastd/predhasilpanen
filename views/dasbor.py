import streamlit as st
import pandas as pd
import numpy as np
from pymongo import MongoClient

if not st.session_state.get("logged_in") or st.session_state.get("role") == "admin":
    st.warning("Akses ditolak. Halaman ini khusus Petani.")
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
    
    # Mapping bulan ke angka untuk validasi matematis
    bulan_dict = {"Januari": 1, "Februari": 2, "Maret": 3, "April": 4, "Mei": 5, "Juni": 6, "Juli": 7, "Agustus": 8, "September": 9, "Oktober": 10, "November": 11, "Desember": 12}
    daftar_bulan = list(bulan_dict.keys())
    
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1: bulan_tanam = st.selectbox("Bulan Tanam", daftar_bulan, index=3)
    with col_t2: tahun_tanam = st.number_input("Tahun Tanam", min_value=2000, max_value=2050, value=2026)
    with col_t3: bulan_panen = st.selectbox("Bulan Panen", daftar_bulan, index=4)
    with col_t4: tahun_panen = st.number_input("Tahun Panen", min_value=2000, max_value=2050, value=2026)
    
    periode = f"{bulan_tanam} {tahun_tanam} - {bulan_panen} {tahun_panen}"
    jenis_tanaman = st.selectbox("Jenis Komoditas Tanaman", ["Cabai Merah", "Bawang Merah", "Jagung", "Kedelai", "Padi", "Lainnya"])
    
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

    # LOGIKA VALIDASI INPUT
    waktu_tanam_val = (tahun_tanam * 12) + bulan_dict[bulan_tanam]
    waktu_panen_val = (tahun_panen * 12) + bulan_dict[bulan_panen]
    
    input_valid = True
    pesan_error = ""
    
    if waktu_panen_val <= waktu_tanam_val:
        input_valid = False
        pesan_error = "Waktu panen tidak rasional. Waktu panen harus terjadi setelah waktu tanam."
    elif luas_lahan <= 0:
        input_valid = False
        pesan_error = "Luas lahan harus lebih besar dari 0."

    if st.button("Simpan Data Pencatatan", type="primary"):
        if not input_valid:
            st.error(f"Gagal Menyimpan: {pesan_error}")
        else:
            dokumen = {
                "User": user_aktif, "Periode": periode, "Jenis_Tanaman": jenis_tanaman,
                "Luas_Lahan": luas_lahan, "Biaya_Lahan": b_lahan, "Biaya_Bibit": b_bibit,
                "Biaya_Pupuk": b_pupuk, "Biaya_Perawatan": b_perawatan, "Hasil_Panen_Kg": hasil_kg,
                "Harga_Jual": harga_jual, "Keuntungan": keuntungan, "Status": status
            }
            collection.insert_one(dokumen)
            st.success("Data berhasil diverifikasi dan disimpan ke basis data.")

with tab2:
    st.subheader("Manajemen Rekam Jejak Data")
    data_hist = list(collection.find({"User": user_aktif}))
    
    if data_hist:
        df = pd.DataFrame(data_hist)
        df.index = range(1, len(df) + 1)
        df["Tandai Hapus"] = False
        
        # Fitur Filter Data
        with st.expander("Saring Data Pencatatan", expanded=True):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filter_tanaman = st.selectbox("Saring berdasarkan Jenis Tanaman", ["Semua"] + list(df['Jenis_Tanaman'].unique()))
            with col_f2:
                filter_status = st.selectbox("Saring berdasarkan Status Keuangan", ["Semua", "UNTUNG", "RUGI"])
                
        # Aplikasi Filter
        df_tampil = df.copy()
        if filter_tanaman != "Semua":
            df_tampil = df_tampil[df_tampil['Jenis_Tanaman'] == filter_tanaman]
        if filter_status != "Semua":
            df_tampil = df_tampil[df_tampil['Status'] == filter_status]
        
        if not df_tampil.empty:
            kolom_tampil = ["Periode", "Jenis_Tanaman", "Luas_Lahan", "Biaya_Lahan", "Biaya_Bibit", "Biaya_Pupuk", "Biaya_Perawatan", "Hasil_Panen_Kg", "Harga_Jual", "Keuntungan", "Status", "Tandai Hapus"]
            
            st.write("Centang kotak pada kolom paling kanan untuk menghapus data terpilih.")
            edited_df = st.data_editor(
                df_tampil[kolom_tampil],
                use_container_width=True,
                disabled=["Periode", "Jenis_Tanaman", "Luas_Lahan", "Biaya_Lahan", "Biaya_Bibit", "Biaya_Pupuk", "Biaya_Perawatan", "Hasil_Panen_Kg", "Harga_Jual", "Keuntungan", "Status"],
                column_config={"Tandai Hapus": st.column_config.CheckboxColumn("Tandai Hapus", default=False)}
            )
            
            baris_dihapus = edited_df[edited_df["Tandai Hapus"] == True]
            if not baris_dihapus.empty:
                st.markdown("---")
                with st.popover("Konfirmasi Penghapusan Data"):
                    st.write("Apakah anda yakin ingin menghapus data ini secara permanen?")
                    col_ya, col_tidak = st.columns(2)
                    with col_ya:
                        if st.button("Ya, Hapus", type="primary"):
                            for idx in baris_dihapus.index:
                                id_dokumen = df.loc[idx, '_id'] # Menggunakan indeks df asli
                                collection.delete_one({"_id": id_dokumen})
                            st.rerun()
                    with col_tidak:
                        if st.button("Batal"):
                            st.rerun()
        else:
            st.info("Tidak ada data yang sesuai dengan kriteria filter Anda.")
    else:
        st.write("Belum ada data pencatatan.")

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
            luas_total = st.number_input("Luas Keseluruhan Lahan (m2)", min_value=1.0, value=1000.0)
            luas_ubin = st.number_input("Luas Kotak Ubinan (m2)", min_value=0.1, value=6.25)
        with c_u2:
            berat_ubin = st.number_input("Berat Panen dalam Ubinan (Kg)", min_value=0.0, value=5.0)
        
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
                jumlah_partisi = st.number_input("Jumlah Partisi Iterasi", min_value=1, max_value=50, value=36)
                
            st.latex(r"y = y_1 + \frac{(x - x_1)(y_2 - y_1)}{(x_2 - x_1)}")
            
            if x2 - x1 == 0:
                st.error("Titik koordinat x1 dan x2 bernilai sama. Gradien tidak terdefinisi (pembagian dengan nol).")
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
                    st.write(f"Partisi {i}: Luas Lahan = {x_step:.2f} m² $\\rightarrow$ Proyeksi Panen = {y_step:.2f} Kg")
                
                y_final = y1 + ((target_luas - x1) * gradien)
                st.success(f"Kesimpulan: Target Luas Lahan {target_luas} m² diproyeksikan menghasilkan {y_final:.2f} Kg.")
        else:
            st.warning("Dibutuhkan minimal 2 rekaman data historis.")

with tab4:
    st.subheader("Visualisasi Tren Data (Sesuai Filter)")
    data_hist = list(collection.find({"User": user_aktif}))
    if data_hist:
        df_vis = pd.DataFrame(data_hist)
        
        # Fitur Filter Visualisasi
        pilihan_tanaman_vis = st.selectbox("Filter Tanaman untuk Grafik", ["Semua"] + list(df_vis['Jenis_Tanaman'].unique()))
        if pilihan_tanaman_vis != "Semua":
            df_vis = df_vis[df_vis['Jenis_Tanaman'] == pilihan_tanaman_vis]
        
        if not df_vis.empty:
            col_vis1, col_vis2 = st.columns(2)
            with col_vis1:
                st.write("Hasil Panen per Periode (Kg)")
                st.bar_chart(df_vis.set_index("Periode")["Hasil_Panen_Kg"])
            with col_vis2:
                st.write("Analisis Keuntungan (Rp)")
                st.line_chart(df_vis.set_index("Periode")["Keuntungan"])
        else:
            st.info("Tidak ada data untuk divisualisasikan pada filter tersebut.")
    else:
        st.write("Belum ada data untuk ditampilkan.")
