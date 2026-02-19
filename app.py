import streamlit as st
import pandas as pd
import io

# Konfigurasi Halaman untuk Mobile & Desktop
st.set_page_config(page_title="Profit Klinik TPMD", layout="centered")

# Custom CSS agar tampilan lebih cantik di HP
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_value=True)

st.title("🏥 Profit Klinik TPMD")
st.info("Gunakan aplikasi ini untuk simulasi keuntungan paket pemeriksaan.")

# --- SIDEBAR PENGATURAN ---
st.sidebar.header("⚙️ Parameter Bisnis")
harga_paket = st.sidebar.number_input("Harga Paket (Rp)", value=50000, step=5000)
jumlah_pasien = st.sidebar.number_input("Estimasi Pasien/Hari", min_value=1, value=10)
hari_kerja = st.sidebar.slider("Hari Kerja/Bulan", 1, 31, 26)

# --- UPLOAD DATA ---
uploaded_file = st.file_uploader("Upload Excel Stok Obat", type=['xlsx'])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        
        # Identifikasi Kolom Otomatis
        # Kita cari kolom yang mengandung kata 'Merk' dan 'Harga'
        kolom_merk = [c for c in df.columns if 'merk' in c.lower()][0]
        kolom_harga = [c for c in df.columns if 'harga' in c.lower()][0]
        
        st.subheader("💊 Simulasi Obat")
        obat_resep = st.multiselect("Pilih obat dalam paket:", df[kolom_merk].unique())

        if obat_resep:
            # Filter data
            data_resep = df[df[kolom_merk].isin(obat_resep)].copy()
            modal_obat = data_resep[kolom_harga].sum()
            
            # Perhitungan
            untung_per_pasien = harga_paket - modal_obat
            untung_harian = untung_per_pasien * jumlah_pasien
            untung_bulanan = untung_harian * hari_kerja
            margin = (untung_per_pasien / harga_paket) * 100

            # --- DISPLAY METRIK ---
            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Modal Obat", f"Rp {modal_obat:,.0f}")
                st.metric("Untung/Pasien", f"Rp {untung_per_pasien:,.0f}")
            with c2:
                st.metric("Untung Harian", f"Rp {untung_harian:,.0f}")
                st.metric("Untung Bulanan", f"Rp {untung_bulanan:,.0f}")

            # Indikator Kesehatan Bisnis
            st.write(f"**Margin Keuntungan: {margin:.1f}%**")
            if margin < 30:
                st.error("⚠️ Margin rendah! Evaluasi biaya obat.")
            else:
                st.success("✅ Margin Sehat.")

            # --- DOWNLOAD REPORT ---
            st.divider()
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Ringkasan
                summary_df = pd.DataFrame({
                    'Parameter': ['Harga Paket', 'Modal Obat', 'Untung/Pasien', 'Pasien/Hari', 'Total Untung Bulanan'],
                    'Nilai': [harga_paket, modal_obat, untung_per_pasien, jumlah_pasien, untung_bulanan]
                })
                summary_df.to_excel(writer, index=False, sheet_name='Ringkasan')
                data_resep.to_excel(writer, index=False, sheet_name='Detail_Obat')
            
            st.download_button(
                label="📥 Download Laporan ke Excel",
                data=output.getvalue(),
                file_name=f'Laporan_Profit_Klinik.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.warning("Pilih minimal satu obat untuk melihat hasil.")

    except Exception as e:
        st.error(f"Terjadi kesalahan: Pastikan kolom 'Merk' dan 'Harga obat' tersedia di file Excel.")
else:
    st.info("Silakan unggah file Excel stok obat Anda untuk memulai.")
