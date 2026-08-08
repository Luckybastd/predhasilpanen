import streamlit as st

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400..700;1,400..700&family=Open+Sans:ital,wght@0,300..800;1,300..800&display=swap');
    html, body, [class*="css"] { font-family: 'Open Sans', sans-serif; background-color: #fcfdfa; }
    h1, h2, h3 { font-family: 'Lora', serif; color: #1b3312; }
    .hero-section { background-color: #e8f5e9; padding: 50px; border-radius: 10px; text-align: center; margin-bottom: 30px; border-bottom: 5px solid #2d5a27;}
    .feature-box { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); height: 100%; border-top: 4px solid #4CAF50;}
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <div class="hero-section">
        <h1 style='font-size: 3rem;'>Selamat Datang di TANIKITA</h1>
        <p style='font-size: 1.5rem; color: #3b592d;'>Sistem Informasi Manajemen, Pencatatan Finansial, dan Kalkulasi Hasil Panen Terpadu.</p>
    </div>
""", unsafe_allow_html=True)

st.write("### Mengapa Menggunakan TANIKITA?")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3>Pencatatan Akurat</h3>
        <p>Kelola biaya operasional (lahan, bibit, pupuk) dan pantau margin keuntungan bersih secara terstruktur.</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="feature-box">
        <h3>Ekstrapolasi Matematis</h3>
        <p>Gunakan data historis untuk memprediksi hasil panen di masa depan dengan perhitungan algoritma berulang yang mendetail.</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="feature-box">
        <h3>Keamanan Data</h3>
        <p>Data dilindungi dengan sistem multi-user tersertifikasi menggunakan standar hashing tingkat tinggi. Privasi Anda terjaga.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.info("Silakan navigasi ke menu Otentikasi Sistem di sebelah kiri untuk mulai merencanakan produksi Anda.")
