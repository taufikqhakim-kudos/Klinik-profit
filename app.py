import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Rekap Harian TPMD", layout="centered")

# Inisialisasi 'Buku Catatan' di memori aplikasi
if 'rekap_harian' not in st.session_state:
    st.session_state.rekap_harian = []

st.title("📑 Rekap Harian & Margin Klinik")

# --- SIDEBAR: PENGATURAN ---
st.sidebar.header("⚙️ Harga Paket")
harga_paket = st.sidebar.number_input("Harga Paket (Rp)", value=50000)

# --- UPLOAD DATA STOK ---
uploaded_file = st.file_uploader("Upload Master Harga Obat (Excel)", type=['xlsx'])

if uploaded_file:
    df_stok = pd.read_excel(uploaded_file)
    kolom_merk = [c for c in df_stok.columns if 'merk' in c.lower()][0]
    kolom_harga = [c for c in df_stok.columns if 'harga' in c.lower()][0]

    # --- FORM INPUT PASIEN ---
    with st.form("form_pasien"):
        st.subheader("➕ Tambah Transaksi Pasien")
        nama_pasien = st.text_input("Nama Pasien (Opsional)")
        obat_dipakai = st.multiselect("Obat yang diberikan:", df_stok[kolom_merk].unique())
        submit = st.form_submit_button("Simpan ke Rekap Hari Ini")

        if submit and obat_dipakai:
            # Hitung modal obat untuk pasien ini
            data_obat = df_stok[df_stok[kolom_merk].isin(obat_dipakai)]
            total_modal = data_obat[kolom_harga].sum()
            margin = harga_paket - total_modal
            
            # Masukkan ke catatan
            st.session_state.rekap_harian.append({
                "Waktu": datetime.now().strftime("%H:%M"),
                "Pasien": nama_pasien if nama_pasien else "Anonim",
                "Modal Obat": total_modal,
                "Laba Bersih": margin
            })
            st.success("Data berhasil ditambahkan!")

    # --- TABEL REKAP ---
    if st.session_state.rekap_harian:
        st.divider()
        st.subheader("📊 Ringkasan Hari Ini")
        df_rekap = pd.DataFrame(st.session_state.rekap_harian)
        
        # Tampilan Metrik Utama
        c1, c2, c3 = st.columns(3)
        total_modal_all = df_rekap["Modal Obat"].sum()
        total_laba_all = df_rekap["Laba Bersih"].sum()
        
        c1.metric("Total Pasien", len(df_rekap))
        c2.metric("Dana Belanja Obat", f"Rp {total_modal_all:,.0f}", help="Sisihkan uang ini untuk beli obat lagi")
        c3.metric("Margin (Laba)", f"Rp {total_laba_all:,.0f}")

        # Tabel Detail
        st.dataframe(df_rekap, use_container_width=True)

        # Tombol Reset & Download
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🗑️ Hapus Semua Data (Reset Hari)"):
                st.session_state.rekap_harian = []
                st.rerun()
        with col_btn2:
            output = io.BytesIO()
            df_rekap.to_excel(output, index=False)
            st.download_button("📥 Download Rekap (Excel)", data=output.getvalue(), file_name=f"rekap_{datetime.now().date()}.xlsx")
    else:
        st.info("Belum ada data pasien hari ini. Silakan input di form atas.")

else:
    st.info("Silakan unggah file Excel stok obat Anda.")
