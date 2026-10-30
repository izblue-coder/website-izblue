import streamlit as st

st.set_page_config(page_title="Website Izham")

st.title("Welcome to My Website")
st.subheader("Program by Izham")

nama = st.text_input("Masukkan nama kamu")

if st.button("Kirim"):
    st.write(f"Halo, {nama}!")
    st.success("Website berhasil dijalankan!")
  
