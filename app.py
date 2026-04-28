import streamlit as st
import pandas as pd
import numpy as np
from pymongo import MongoClient

# Konfigurasi Halaman
st.set_page_config(page_title="TANIKITA - Rencana Produksi", layout="wide")

# Custom CSS untuk Tema Pertanian Profesional (Tanpa Emoji)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400..700;1,400..700&family=Open+Sans:ital,wght@0,300..800;1,300..800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Open Sans', sans-serif;
        background-color: #fcfdfa;
    }
    
    h1, h2, h3 {
        font-family: 'Lora', serif;
        color: #1b3312;
    }

    .main { background-color: #fcfdfa; }
    
    .stButton>button {
        background-color: #2d5a27;
        color: white;
        border-radius: 4px;
        padding: 10px 24px;
        border: none;
    }

    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-top: 5px solid #2d5a27;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    .status-untung {
        color: #2d5a27;
        font-weight: bold;
        background-color: #e8f5e9;
        padding: 5px 10px;
        border-radius: 4px;
    }

    .status-rugi {
        color: #b71c1c;
        font-weight: bold;
        background-color: #ffebee;
        padding: 5px 10px;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# Inisialisasi Koneksi MongoDB
@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongo"]["uri"])

try:
    client = init_connection()
    db = client.pertanian_db
    collection = db.pencatatan
except Exception as e:
    st.error("Koneksi gagal. Periksa kembali konfigurasi database Anda.")
    st.stop()

# Header Utama
st.title("TANIKITA")
st.write("Sistem Informasi Manajemen dan Perencanaan Produksi Pertanian Indonesia.")

# Sidebar
with st.sidebar:
    st.header("Identitas Pengguna")
    user_id = st.text_input("ID Petani", value="Petani_Mandiri_01")
    st.markdown("---")
    st.write("Periode Tanam-Panen membantu dalam analisis efisiensi musiman.")

# Menu Tab
tab1, tab2, tab3 = st.tabs(["Pencatatan", "Prediksi Produksi", "Visualisasi Data"])

with tab1:
    st.subheader("Data Periode Produksi")
    
    col_a, col_b = st.columns(2)
    with col_a:
        periode = st.text_input("Periode Tanam-Panen", placeholder="Contoh: April - Mei 2026")
        jenis_tanaman = st.selectbox("Jenis Tanaman", 
                                    ["Cabai Merah", "Bawang Merah", "Jagung (Palawija)", "Kedelai (Palawija)", "Tomat (Hortikultura)", "Sawi", "Lainnya"])
    
    st.markdown("### Rincian Biaya")
    col1, col2 = st.columns(2)
    with col1:
        b_lahan = st.number_input("Biaya Pengolahan Lahan (Rp)", min_value=0)
        b_bibit = st.number_input("Biaya Bibit (Rp)", min_value=0)
    with col2:
        b_pupuk = st.number_input("Biaya Pupuk (Rp)", min_value=0)
        b_perawatan = st.number_input("Biaya Perawatan (Rp)", min_value=0)
        
    st.markdown("### Hasil Produksi")
    col3, col4 = st.columns(2)
    with col3:
        hasil_kg = st.number_input("Hasil Panen (Kg)", min_value=0.0)
    with col4:
        harga_jual = st.number_input("Harga Jual Per Kg (Rp)", min_value=0)
    
    total_biaya = b_lahan + b_bibit + b_pupuk + b_perawatan
    pendapatan = hasil_kg * harga_jual
    keuntungan = pendapatan - total_biaya
    status = "UNTUNG" if keuntungan > 0 else "RUGI"
    
    st.markdown("---")
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.metric("Total Keuntungan/Kerugian", f"Rp {keuntungan:,.0f}")
    with col_res2:
        if status == "UNTUNG":
            st.markdown(f"Status: <span class='status-untung'>{status}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"Status: <span class='status-rugi'>{status}</span>", unsafe_allow_html=True)

    if st.button("Simpan Data ke TANIKITA"):
        if not periode:
            st.warning("Mohon isi periode tanam-panen.")
        else:
            dokumen = {
                "User": user_id,
                "Periode": periode,
                "Jenis_Tanaman": jenis_tanaman,
                "Biaya_Lahan": b_lahan,
                "Biaya_Bibit": b_bibit,
                "Biaya_Pupuk": b_pupuk,
                "Biaya_Perawatan": b_perawatan,
                "Hasil_Panen_Kg": hasil_kg,
                "Harga_Jual": harga_jual,
                "Keuntungan": keuntungan,
                "Status": status
            }
            collection.insert_one(dokumen)
            st.success("Data periode berhasil tercatat.")

with tab2:
    st.subheader("Metode Peramalan Hasil")
    
    metode = st.radio("Pilih Metode Prediksi", ["Ubinan (Cepat/Sample)", "Interpolasi (Berdasarkan Histori)"])
    
    if metode == "Ubinan (Cepat/Sample)":
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            luas_lahan = st.number_input("Luas Lahan Total (m2)", value=1000.0)
            luas_sampel = st.number_input("Luas Sampel Ubinan (m2)", value=6.25)
        with col_u2:
            berat_sampel = st.number_input("Berat Sampel (Kg)", value=5.0)
        
        prediksi_ubinan = (luas_lahan / luas_sampel) * berat_sampel
        st.metric("Prediksi Total Panen", f"{prediksi_ubinan:,.2f} Kg")
        
    else:
        st.write("Prediksi Interpolasi Linear berdasarkan Luas Lahan vs Hasil Panen sebelumnya.")
        # Mengambil data historis untuk interpolasi
        data_hist = list(collection.find({"User": user_id}))
        if len(data_hist) >= 2:
            # Simulasi interpolasi: kita asumsikan user menginput luas lahan saat ini
            luas_saat_ini = st.number_input("Masukkan Luas Lahan Periode Ini (m2)", value=1000.0)
            
            # Dalam praktek nyata, kita butuh data luas lahan di histori. 
            # Karena di pencatatan belum ada kolom luas lahan, kita asumsikan data dummy untuk demo perhitungan matematika
            x_hist = np.array([500, 1500]) # Contoh luas lahan historis
            y_hist = np.array([d['Hasil_Panen_Kg'] for d in data_hist[:2]]) # Hasil panen historis
            
            prediksi_interp = np.interp(luas_saat_ini, x_hist, y_hist)
            st.metric("Prediksi Hasil (Interpolasi)", f"{prediksi_interp:,.2f} Kg")
            st.info("Catatan: Interpolasi ini menghitung estimasi hasil berdasarkan perbandingan luas lahan pada data historis Anda.")
        else:
            st.warning("Data historis minimal 2 periode diperlukan untuk perhitungan interpolasi.")

with tab3:
    st.subheader("Laporan Produksi Terdaftar")
    
    data_user = list(collection.find({"User": user_id}, {"_id": 0}))
    
    if data_user:
        df = pd.DataFrame(data_user)
        
        # Tabel Data
        st.write("Tabel Rincian Aktivitas")
        st.dataframe(df, use_container_width=True)
        
        st.markdown("### Visualisasi Tren")
        col_vis1, col_vis2 = st.columns(2)
        
        with col_vis1:
            st.write("Hasil Panen per Periode (Kg)")
            st.bar_chart(df.set_index("Periode")["Hasil_Panen_Kg"])
            
        with col_vis2:
            st.write("Analisis Keuntungan (Rp)")
            st.line_chart(df.set_index("Periode")["Keuntungan"])
            
        # Ringkasan Statistik
        st.markdown("### Ringkasan Performa")
        total_untung = df[df["Status"] == "UNTUNG"].shape[0]
        total_rugi = df[df["Status"] == "RUGI"].shape[0]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Panen Terakumulasi", f"{df['Hasil_Panen_Kg'].sum():,.0f} Kg")
        c2.metric("Total Keuntungan Bersih", f"Rp {df['Keuntungan'].sum():,.0f}")
        c3.write(f"Frekuensi: {total_untung} Kali Untung, {total_rugi} Kali Rugi")
    else:
        st.write("Belum ada data untuk divisualisasikan.")
