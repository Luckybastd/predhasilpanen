import streamlit as st
import pandas as pd
from pymongo import MongoClient

# Konfigurasi Halaman Utama
st.set_page_config(page_title="Sistem Rencana Produksi Pertanian", layout="wide")

# Custom CSS untuk Tema Pertanian Profesional (Hijau, Putih, Coklat Tanah)
st.markdown("""
    <style>
    .main { background-color: #f8faf5; }
    .stButton>button { background-color: #3b592d; color: white; border-radius: 4px; border: none; font-weight: bold; }
    .stButton>button:hover { background-color: #2e4d23; color: white; }
    h1, h2, h3 { color: #2e4d23; font-family: 'Segoe UI', Tahoma, sans-serif; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 8px; border-left: 6px solid #558b2f; box-shadow: 1px 1px 4px rgba(0,0,0,0.1); }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: transparent; border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px; padding-bottom: 10px; color: #3b592d; font-weight: bold;}
    .stTabs [aria-selected="true"] { background-color: #e8f5e9; border-bottom: 3px solid #3b592d; }
    </style>
    """, unsafe_allow_html=True)

# Inisialisasi Koneksi MongoDB
@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongo"]["uri"])

try:
    client = init_connection()
    # Membuat database "pertanian_db" dan collection "pencatatan"
    db = client.pertanian_db
    collection = db.pencatatan
except Exception as e:
    st.error("Gagal terhubung ke Database. Periksa pengaturan Secrets Anda.")
    st.stop()

# Header Aplikasi
st.title("Sistem Rencana & Prediksi Produksi Pertanian")
st.write("Aplikasi Manajemen Finansial dan Estimasi Panen. Tahun Aktif: 2026.")

# Sidebar untuk Isolasi Pengguna
with st.sidebar:
    st.header("Identitas Pengguna")
    user_id = st.text_input("Masukkan ID/Username Anda", value="Petani_Unggul_01")
    st.info("Sistem ini menggunakan isolasi data. Setiap pengguna hanya dapat mengakses dan memprediksi data historis berdasarkan ID masing-masing.")

# Membagi Antarmuka menjadi 2 Tab
tab1, tab2 = st.tabs(["Pencatatan Produksi", "Prediksi & Analisis Hasil"])

# TAB 1: PENCATATAN PRODUKSI
with tab1:
    st.subheader("Formulir Komponen Biaya & Hasil")
    
    col1, col2 = st.columns(2)
    with col1:
        tahun_input = st.number_input("Tahun Pencatatan", min_value=2010, max_value=2050, value=2026)
        b_lahan = st.number_input("Biaya Pengolahan Lahan (Rp)", min_value=0, step=50000)
        b_bibit = st.number_input("Biaya Bibit (Rp)", min_value=0, step=50000)
    with col2:
        b_pupuk = st.number_input("Biaya Pupuk (Rp)", min_value=0, step=50000)
        b_perawatan = st.number_input("Biaya Perawatan (Rp)", min_value=0, step=50000)
        
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    with col3:
        hasil_kg = st.number_input("Hasil Panen Total (Kg)", min_value=0.0, step=10.0)
    with col4:
        harga_jual = st.number_input("Harga Jual Per Kg (Rp)", min_value=0, step=500)
    
    # Kalkulasi Otomatis
    total_biaya = b_lahan + b_bibit + b_pupuk + b_perawatan
    pendapatan = hasil_kg * harga_jual
    keuntungan = pendapatan - total_biaya
    
    st.metric("Estimasi Keuntungan Bersih", f"Rp {keuntungan:,.0f}")
    
    # Tombol Simpan ke MongoDB
    if st.button("Simpan Data Pencatatan"):
        if user_id.strip() == "":
            st.warning("Mohon isi ID Pengguna di panel sebelah kiri terlebih dahulu.")
        else:
            dokumen_baru = {
                "User": user_id,
                "Tahun": tahun_input,
                "Biaya_Lahan": b_lahan,
                "Biaya_Bibit": b_bibit,
                "Biaya_Pupuk": b_pupuk,
                "Biaya_Perawatan": b_perawatan,
                "Hasil_Panen_Kg": hasil_kg,
                "Harga_Jual": harga_jual,
                "Keuntungan": keuntungan
            }
            collection.insert_one(dokumen_baru)
            st.success("Data berhasil diamankan ke dalam database.")

# TAB 2: PREDIKSI & ANALISIS
with tab2:
    st.subheader("Estimasi Menggunakan Metode Ubinan")
    
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        luas_lahan_total = st.number_input("Luas Lahan Sebenarnya (m2)", min_value=1.0, value=10000.0)
        luas_sampel_ubinan = st.number_input("Luas Sampel Ubinan (m2)", min_value=0.1, value=6.25)
    with col_u2:
        berat_sampel = st.number_input("Berat Hasil Ubinan (Kg)", min_value=0.0, value=5.0)
        
    if luas_sampel_ubinan > 0:
        prediksi_ubinan = (luas_lahan_total / luas_sampel_ubinan) * berat_sampel
        st.metric("Prediksi Total Panen (Metode Ubinan)", f"{prediksi_ubinan:,.2f} Kg")

    st.markdown("---")
    
    st.subheader("Peramalan Berdasarkan Data Historis")
    # Menarik data dari MongoDB khusus untuk user yang sedang login
    data_historis = list(collection.find({"User": user_id}, {"_id": 0}))
    
    if len(data_historis) > 0:
        df = pd.DataFrame(data_historis)
        df = df.sort_values(by="Tahun")
        
        if len(df) >= 2:
            st.write(f"Menampilkan tren hasil panen untuk: **{user_id}**")
            # Simple Moving Average (Rata-rata)
            prediksi_tahun_depan = df["Hasil_Panen_Kg"].mean()
            st.metric("Prediksi Hasil Panen Musim Berikutnya (Rata-rata Historis)", f"{prediksi_tahun_depan:,.2f} Kg")
            
            # Visualisasi
            st.line_chart(df.set_index("Tahun")["Hasil_Panen_Kg"])
            
            # Menampilkan Tabel Data
            with st.expander("Lihat Rincian Data Historis Anda"):
                st.dataframe(df, use_container_width=True)
        else:
            st.info("Anda memiliki 1 data catatan. Sistem memerlukan minimal 2 tahun data historis untuk menghasilkan grafik dan peramalan.")
    else:
        st.write("Belum ada data riwayat pencatatan untuk pengguna ini. Silakan isi formulir di tab sebelumnya.")