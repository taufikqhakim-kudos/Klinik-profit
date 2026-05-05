import streamlit as st
import pandas as pd
import io
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(page_title="Klinik Dr. Taufik", layout="centered")

# Custom CSS untuk Flyer
st.markdown("""
    <style>
    .flyer-box {
        border: 4px double #007bff;
        padding: 20px;
        border-radius: 15px;
        background-color: #ffffff;
        color: #333333;
    }
    .flyer-header { text-align: center; color: #007bff; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'rekap_harian' not in st.session_state:
    st.session_state.rekap_harian = []

st.title("🏥 Manajemen & Edukasi Klinik")

tab1, tab2 = st.tabs(["📊 Rekap & Margin", "📱 Flyer Edukasi"])

# --- TAB 1: REKAP & MARGIN ---
with tab1:
    st.sidebar.header("⚙️ Pengaturan")
    harga_paket = st.sidebar.number_input("Harga Paket (Rp)", value=50000)
    
    uploaded_file = st.file_uploader("Upload Data Harga Obat (Excel)", type=['xlsx'])
    
    if uploaded_file:
        df_stok = pd.read_excel(uploaded_file)
        kolom_merk = [c for c in df_stok.columns if 'merk' in c.lower()][0]
        kolom_harga = [c for c in df_stok.columns if 'harga' in c.lower()][0]

        with st.form("form_transaksi", clear_on_submit=True):
            st.subheader("➕ Input Penggunaan Obat")
            nama_p = st.text_input("Nama Pasien (Opsional)")
            obat_p = st.selectbox("Pilih Obat:", ["-- Pilih --"] + list(df_stok[kolom_merk].unique()))
            jumlah_p = st.number_input("Jumlah Terpakai:", min_value=1, value=1)
            submit = st.form_submit_button("Tambahkan ke Daftar")

            if submit and obat_p != "-- Pilih --":
                harga_satuan = df_stok[df_stok[kolom_merk] == obat_p][kolom_harga].values[0]
                total_modal_item = harga_satuan * jumlah_p
                
                st.session_state.rekap_harian.append({
                    "Waktu": datetime.now().strftime("%H:%M"),
                    "Pasien": nama_p if nama_p else "Anonim",
                    "Item": obat_p,
                    "Qty": jumlah_p,
                    "Total Modal": total_modal_item,
                    "Margin": harga_paket - total_modal_item
                })
                st.success(f"Berhasil menambah {obat_p}")

        if st.session_state.rekap_harian:
            st.divider()
            df_rekap = pd.DataFrame(st.session_state.rekap_harian)
            c1, c2 = st.columns(2)
            c1.metric("Dana Stok Ulang", f"Rp {df_rekap['Total Modal'].sum():,.0f}")
            c2.metric("Total Margin Bersih", f"Rp {df_rekap['Margin'].sum():,.0f}")
            st.dataframe(df_rekap, use_container_width=True)
            if st.button("🗑️ Reset Data Hari Ini"):
                st.session_state.rekap_harian = []
                st.rerun()

# --- TAB 2: FLYER EDUKASI (DITAMBAH DM) ---
with tab2:
    st.subheader("Generator Pesan Edukasi")
    dict_edukasi = {
        "Umum": "Istirahat cukup (7-8 jam), minum air putih 2 liter/hari, dan minum obat tepat waktu.",
        "Demam/Flu": "Kompres hangat jika demam, gunakan masker, hindari es, dan perbanyak buah.",
        "Maag/Lambung": "Makan sedikit tapi sering, hindari pedas, asam, kopi, dan santan sementara.",
        "Diabetes (Gula Darah)": "Batasi nasi putih/tepung/manis, rutin olahraga jalan kaki 30 menit, rutin cek gula darah, dan periksa kebersihan kaki setiap hari.",
        "Darah Tinggi": "Kurangi garam dan lemak, kelola stres, dan rutin cek tekanan darah.",
        "Gatal/Alergi": "Jangan digaruk, hindari pemicu alergi, dan jaga kebersihan pakaian."
    }
    
    pilihan = st.selectbox("Pilih Topik:", list(dict_edukasi.keys()))
    nama_f = st.text_input("Nama Pasien untuk Flyer:", "Bapak/Ibu")
    
    st.markdown(f"""
    <div class="flyer-box">
        <h2 class="flyer-header">🏥 KLINIK DR. TAUFIK</h2>
        <hr>
        <p><b>Halo, {nama_f}</b></p>
        <p>Anjuran pemulihan:</p>
        <p>✅ <i>{dict_edukasi[pilihan]}</i></p>
        <br>
        <p style="color: red; font-size: 0.8em;">⚠️ <b>Segera ke UGD jika:</b> Sesak napas, penurunan kesadaran, atau luka yang sulit sembuh.</p>
        <hr>
        <p style="text-align: center; font-size: 0.7em;"><i>Semoga Lekas Sembuh!</i></p>
    </div>
    """, unsafe_allow_html=True)
