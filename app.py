import streamlit as st

# Konfigurasi halaman wajib di file utama (tanpa emoji)
st.set_page_config(page_title="TANIKITA", layout="wide")

# Inisialisasi Session State dasar
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

# Mendefinisikan halaman-halaman yang ada di folder views
beranda_page = st.Page("views/beranda.py", title="Beranda Utama")
login_page = st.Page("views/login.py", title="Otentikasi Sistem")
dasbor_page = st.Page("views/dasbor.py", title="Dasbor Manajemen Produksi")
admin_page = st.Page("views/admin.py", title="Panel Kendali Administrator")

# Logika Routing (Navigasi Dinamis)
if not st.session_state.logged_in:
    # Jika belum login, hanya tampilkan Beranda dan Login
    nav = st.navigation([beranda_page, login_page])
else:
    # Jika sudah login, arahkan sesuai peran (Role)
    if st.session_state.role == "admin":
        nav = st.navigation([admin_page])
    else:
        nav = st.navigation([dasbor_page])

# Menjalankan navigasi
nav.run()
