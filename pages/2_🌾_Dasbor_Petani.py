import streamlit as st
import pandas as pd
import numpy as np
from pymongo import MongoClient

st.set_page_config(page_title="TANIKITA | Dasbor", page_icon="🌾", layout="wide")

# Pengecekan Akses (Wajib Login)
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("🔒 Akses Ditolak. Anda harus Login terlebih dahulu.")
    st.stop()

# Tampilkan ID User yang sedang aktif
user_aktif = st.session_state['username']
st.sidebar.success(f"👤 Masuk sebagai: **{user_aktif}**")
if st.sidebar.button("Keluar (Logout)"):
    st.session_state.clear()
    st.rerun()

@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongo"]["uri"])

client = init_connection()
db = client.pertanian_db
collection = db.pencatatan

st.title(f"Dasbor Manajemen Produksi")
st.write(f"Selamat bekerja, {user_aktif}. Rencanakan dan analisis aktivitas pertanian Anda.")

tab1, tab2, tab3 = st.tabs(["Pencatatan", "Kalkulasi & Prediksi", "Visualisasi Data"])

with tab1:
    st.subheader("Data Periode Produksi")
    col_p1, col_p2, col_p3 = st.columns(3)
    daftar_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    
    with col_p1: bulan_tanam = st.selectbox("Bulan Tanam", daftar_bulan, index=3)
    with col_p2: bulan_panen = st.selectbox("Bulan Panen", daftar_bulan, index=4)
    with col_p3: tahun_periode = st.number_input("Tahun", min_value=2020, max_value=2050, value=2026)
    
    periode = f"{bulan_tanam} - {bulan_panen} {tahun_periode}"
    jenis_tanaman = st.selectbox("Jenis Komoditas Tanaman", ["Cabai Merah (Hortikultura)", "Bawang Merah (Hortikultura)", "Jagung (Palawija)", "Lainnya"])
    
    col1, col2 = st.columns(2)
    with col1:
        b_lahan = st.number_input("Biaya Pengolahan Lahan (Rp)", min_value=0)
        b_bibit = st.number_input("Biaya Bibit (Rp)", min_value=0)
    with col2:
        b_pupuk = st.number_input("Biaya Pupuk (Rp)", min_value=0)
        b_perawatan = st.number_input("Biaya Perawatan (Rp)", min_value=0)
        
    st.markdown("### Hasil Aktual")
    col3, col4, col5 = st.columns(3)
    with col3: luas_lahan = st.number_input("Luas Lahan Tanam (m2)", min_value=1.0, value=1000.0)
    with col4: hasil_kg = st.number_input("Hasil Panen (Kg)", min_value=0.0)
    with col5: harga_jual = st.number_input("Harga Jual Per Kg (Rp)", min_value=0)
    
    total_biaya = b_lahan + b_bibit + b_pupuk + b_perawatan
    pendapatan = hasil_kg * harga_jual
    keuntungan = pendapatan - total_biaya
    status = "UNTUNG" if keuntungan > 0 else "RUGI"
    
    st.info(f"Kalkulasi Keuntungan Bersih: **Rp {keuntungan:,.0f}** | Status: **{status}**")

    if st.button("Simpan Data Pencatatan", type="primary"):
        dokumen = {
            "User": user_aktif, "Periode": periode, "Jenis_Tanaman": jenis_tanaman,
            "Luas_Lahan": luas_lahan, "Biaya_Lahan": b_lahan, "Biaya_Bibit": b_bibit,
            "Biaya_Pupuk": b_pupuk, "Biaya_Perawatan": b_perawatan, "Hasil_Panen_Kg": hasil_kg,
            "Harga_Jual": harga_jual, "Keuntungan": keuntungan, "Status": status
        }
        collection.insert_one(dokumen)
        st.success("Data berhasil diamankan ke basis data TANIKITA.")

with tab2:
    st.subheader("Ekstrapolasi Matematis Berdasarkan Histori Luas Lahan")
    data_hist = list(collection.find({"User": user_aktif}).sort("_id", 1))
    
    if len(data_hist) >= 2:
        st.write("Sistem mendeteksi data historis. Menjalankan model proyeksi ekstrapolasi linear.")
        x_hist = [d.get('Luas_Lahan', 1000) for d in data_hist]
        y_hist = [d['Hasil_Panen_Kg'] for d in data_hist]
        
        # Ambil 2 titik data terakhir untuk ekstrapolasi (x1, y1) dan (x2, y2)
        x1, y1 = x_hist[-2], y_hist[-2]
        x2, y2 = x_hist[-1], y_hist[-1]
        
        target_ekspansi = st.number_input("Masukkan Target Eksekusi Luas Lahan (m2) Berikutnya", min_value=1.0, value=2000.0)
        
        st.markdown("### Detail Perhitungan (Langkah demi Langkah)")
        st.latex(r"y = y_1 + \frac{(x - x_1)(y_2 - y_1)}{(x_2 - x_1)}")
        
        if x2 - x1 == 0:
            st.error("Titik koordinat luas lahan (x1 dan x2) bernilai sama. Sistem tidak dapat menghitung gradien (pembagian dengan nol).")
        else:
            gradien = (y2 - y1) / (x2 - x1)
            
            st.write("**Iterasi Ekstrapolasi Bertahap (Partisi Proyeksi Peningkatan):**")
            st.write(f"- Titik Dasar 1 ($x_1, y_1$): ({x1} m², {y1} Kg)")
            st.write(f"- Titik Dasar 2 ($x_2, y_2$): ({x2} m², {y2} Kg)")
            st.write(f"- Derajat Kemiringan (Gradien): {gradien:.4f}")
            
            selisih = target_ekspansi - x2
            step = selisih / 5 if selisih > 0 else 100
            
            # Menampilkan masing-masing partisi perhitungan secara eksplisit
            for i in range(1, 6):
                x_step = x2 + (step * i)
                y_step = y1 + ((x_step - x1) * gradien)
                st.write(f"**Tahap {i}:** Jika Luas Lahan = {x_step:.1f} m² $\\rightarrow$ Proyeksi Panen = {y_step:.2f} Kg")
            
            y_final = y1 + ((target_ekspansi - x1) * gradien)
            st.success(f"**Kesimpulan Ekstrapolasi:** Target Luas Lahan {target_ekspansi} m² diproyeksikan menghasilkan **{y_final:.2f} Kg** hasil panen.")
    else:
        st.warning("Dibutuhkan minimal 2 pencatatan periode untuk mengaktifkan model perhitungan matematis.")

with tab3:
    st.subheader("Rekapitulasi Visual")
    if data_hist:
        df = pd.DataFrame(data_hist)
        df.index = range(1, len(df) + 1)
        
        columns_to_show = ["Periode", "Jenis_Tanaman", "Luas_Lahan", "Biaya_Lahan", "Biaya_Bibit", "Biaya_Pupuk", "Biaya_Perawatan", "Hasil_Panen_Kg", "Keuntungan", "Status"]
        styled_df = df[columns_to_show].style.set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#2d5a27'), ('color', 'white'), ('text-align', 'center')]}
        ])
        
        st.dataframe(styled_df, use_container_width=True)
        st.bar_chart(df.set_index("Periode")["Keuntungan"])
    else:
        st.info("Kumpulan data riwayat masih kosong.")
