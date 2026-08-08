import streamlit as st
import bcrypt
from pymongo import MongoClient

@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongo"]["uri"])

try:
    client = init_connection()
    db = client.pertanian_db
    users_collection = db.users
except Exception as e:
    st.error("Gagal terhubung ke server database.")
    st.stop()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

st.title("Pintu Masuk TANIKITA")

# Menggunakan Radio button agar bisa dikontrol state-nya
aksi = st.radio("Pilih Tindakan", ["Masuk ke Akun", "Daftar Akun Baru"], horizontal=True)

if aksi == "Masuk ke Akun":
    st.subheader("Masuk (Login)")
    login_username = st.text_input("Username")
    login_password = st.text_input("Password", type="password")
    
    if st.button("Masuk Sistem", type="primary"):
        user_data = users_collection.find_one({"username": login_username})
        
        if user_data and verify_password(login_password, user_data['password']):
            st.session_state.logged_in = True
            st.session_state.username = login_username
            st.session_state.role = user_data.get('role', 'petani')
            # Rerun akan memicu navigasi otomatis di app.py
            st.rerun()
        else:
            st.error("Username atau Password tidak valid.")

elif aksi == "Daftar Akun Baru":
    st.subheader("Pendaftaran Petani Baru")
    reg_username = st.text_input("Buat Username Baru")
    reg_password = st.text_input("Buat Password", type="password")
    reg_confirm = st.text_input("Konfirmasi Password", type="password")
    
    if st.button("Daftar Akun"):
        if reg_password != reg_confirm:
            st.warning("Password tidak cocok!")
        elif len(reg_password) < 6:
            st.warning("Password minimal 6 karakter.")
        elif users_collection.find_one({"username": reg_username}):
            st.warning("Username sudah terdaftar. Silakan gunakan nama lain.")
        else:
            user_role = 'admin' if reg_username.lower() == 'admin' else 'petani'
            users_collection.insert_one({
                "username": reg_username,
                "password": hash_password(reg_password),
                "role": user_role
            })
            st.success("Pendaftaran berhasil! Silakan pilih opsi 'Masuk ke Akun' di atas untuk masuk.")
