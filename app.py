import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from streamlit_option_menu import option_menu
import datetime

st.markdown(
    """
    <style>
    /* Menargetkan khusus kotak input yang bertipe password */
    input[type="password"] {
        color: transparent !important;       /* Membuat teks/titik menjadi transparan */
        text-shadow: none !important;        /* Memastikan tidak ada bayangan teks yang tertinggal */
        caret-color: transparent !important; /* Menghilangkan garis kursor yang berkedip */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="Semester 3", page_icon="🎓", layout="centered")

@st.cache_resource
def init_connection():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
    client = gspread.authorize(creds)
    
    spreadsheet = client.open("Semester 3")
    return spreadsheet

if 'login_sukses' not in st.session_state:
    st.session_state['login_sukses'] = False

if not st.session_state['login_sukses']:
    st.title('3rd Semester Journal')
    st.write("Enter the password")
    
    password = st.text_input("Password:", type="password")
    if st.button("Sign In"):
        # Cek password dari Streamlit Secrets
        if password == st.secrets["APP_PASSWORD"]:
            st.session_state['login_sukses'] = True
            st.rerun()
        else:
            st.error("❌ Password salah!")

if st.session_state['login_sukses']:
    
    try:
        spreadsheet = init_connection()
    except Exception as e:
        st.error(f"Gagal terhubung ke Google Sheets: {e}")
        st.stop()

    with st.sidebar:
        if st.button("🚪 Keluar (Logout)", key="btn_logout_sidebar"):
            st.session_state['login_sukses'] = False
            st.rerun()
            
        st.divider()
        
        pilihan_menu = option_menu(
            menu_title="Main Menu",  # Judul menu
            options=["Jadwal Kuliah", "Tugas", "Jadwal UTS", "Jadwal UAS"],
            icons=["calendar-week", "pencil-square", "journal-text", "mortarboard"], 
            menu_icon="cast", 
            default_index=1, 
        )

    # --- HALAMAN: JADWAL KULIAH ---
    if pilihan_menu == "Jadwal Kuliah":
        st.title("📅 Jadwal Kuliah")
        st.write("Jadwal perkuliahan mingguan.")
        try:
            st.image('Jadwal.png')
        except FileNotFoundError:
            st.error('Gambar tidak ditemukan')

    # --- HALAMAN: MANAJEMEN TUGAS ---
    elif pilihan_menu == "Tugas":
        st.title("📝 Manajemen Tugas")
        st.write("Selamat datang, Arga! Silakan kelola jadwal tugasmu di sini.")
        
        tab_input, tab_daftar, semuatugas = st.tabs(["➕ Tambah Tugas", "📋 Tugas Pending", '📋 Semua Tugas'])
        
        # TAB 1: FORM INPUT
        with tab_input:
            st.subheader("Input Tugas Baru")
            
            with st.form(key="form_tambah_tugas"):
                daftar_matkul = [
                    "Kecerdasan Buatan", 
                    "BING", 
                    "ADS", 
                    "Metode Numerik", 
                    "Agama Islam", 
                    "LMD",
                    'Praktikum ADS',
                    'PANCASILA'
                ]
                mata_kuliah = st.selectbox("Mata Kuliah", daftar_matkul)
                
                nama_tugas = st.text_input("Isi Tugas")
                
                kolom_opsi1, kolom_opsi2 = st.columns(2)
                with kolom_opsi1:
                    # 3. Kolom C: SIFAT
                    sifat_tugas = st.selectbox("Sifat Tugas", ["Individu", "Kelompok"])
                    # 4. Kolom D: DIBUAT
                    tanggal_dibuat = st.date_input("Tanggal Dibuat")
                with kolom_opsi2:
                    # 7. Kolom G: PENGUMPULAN
                    tempat_kumpul = st.selectbox("Tempat Pengumpulan", ["GCR", "E-Learning", "Offline"])
                    # 5. Kolom E: DEADLINE
                    tanggal_pengumpulan = st.date_input("Tanggal Deadline")
                
                # 6. Kolom F: STATUS
                status = st.selectbox("Status Tugas", ["PROSES", "SELESAI", "TERLAMBAT"])
                
                submit_btn = st.form_submit_button("Simpan ke Tabel")
                
            if submit_btn:
                if mata_kuliah == "Pilih Mata Kuliah...":
                    st.warning("⚠️ Silakan pilih Mata Kuliah terlebih dahulu!")
                elif nama_tugas == "":
                    st.warning("⚠️ Isi tugas tidak boleh kosong!")
                else:
                    try:
                        sheet_tugas = spreadsheet.worksheet("Tugas")
                        
                        kolom_a = sheet_tugas.col_values(1) 
                        baris_baru = len(kolom_a) + 1
                        
                        data_baru = [
                            mata_kuliah,                              # A: Matkul
                            nama_tugas,                               # B: Isi Tugas
                            sifat_tugas,                              # C: Sifat
                            tanggal_dibuat.strftime("%d-%m-%Y"),      # D: Dibuat
                            tanggal_pengumpulan.strftime("%d-%m-%Y"), # E: Deadline
                            status,                                   # F: Status
                            tempat_kumpul                             # G: Pengumpulan
                        ]
                        
                        rentang_sel = f"A{baris_baru}:G{baris_baru}"
                        
                        sheet_tugas.update(
                            range_name=rentang_sel,
                            values=[data_baru],
                            value_input_option="USER_ENTERED"
                        )
                        
                        st.success(f"✅ Berhasil! Tugas '{nama_tugas}' untuk {mata_kuliah} telah ditambahkan.")
                        
                    except Exception as e:
                        st.error(f"❌ Gagal menyimpan data: {e}")

        # TAB 2: DAFTAR TUGAS PROSES
        with tab_daftar:
            st.subheader("Daftar Tugas Yang Masih PROSES")
            
            # Tombol refresh dengan key unik
            if st.button("🔄 Segarkan Data", key="btn_refresh_tugas_proses"):
                st.rerun()
                
            try:
                # Mengakses worksheet "Tugas"
                sheet_tugas = spreadsheet.worksheet("Tugas")
                semua_data = sheet_tugas.get("A1:G")
                
                if len(semua_data) > 1:
                    # Menjadikan baris pertama (index 0) sebagai nama kolom (header)
                    df = pd.DataFrame(semua_data[1:], columns=semua_data[0])
                    # Bersihkan nama kolom: hilangkan spasi tersembunyi & jadikan HURUF BESAR
                    df.columns = df.columns.astype(str).str.strip().str.upper()
                    # Cek apakah kata "STATUS" ada di daftar nama kolom yang sudah dibersihkan
                    if "STATUS" in df.columns:
                        # Filter hanya baris yang kolom STATUS-nya berisi kata "PROSES"
                        df_proses = df[df["STATUS"].astype(str).str.strip().str.upper() == "PROSES"]
                        if not df_proses.empty:
                            # Tampilkan tabel tanpa nomor index dari Pandas
                            st.dataframe(df_proses, use_container_width=True, hide_index=True)
                        else:
                            st.info("🎉 Hore! Tidak ada tugas yang pending.")
                    else:
                        st.error("Kolom 'Status' tidak ditemukan di rentang A1:G.")
                        st.write("Kolom yang terbaca saat ini adalah:", df.columns.tolist())
                else:
                    st.info("Tabel masih kosong atau header belum dibuat.")
            except Exception as e:
                st.error(f"Gagal memuat data: {e}")

        with semuatugas:
            st.subheader('Daftar Semua Tugas')
            if st.button('🔄 Segarkan Data', key='btn_refresh-daftartugas'):
                st.rerun()
            try:
                sheet_tugas = spreadsheet.worksheet("Tugas")
                semua_data = sheet_tugas.get('A1:G')

                if len(semua_data) > 1:
                    df_all = pd.DataFrame(semua_data[1:], columns=semua_data[0])
                    st.dataframe(df_all, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f'Gagal memuat data : {e}')
                

    # --- HALAMAN: JADWAL UTS ---
    elif pilihan_menu == "Jadwal UTS":
        st.title("✍️ Jadwal UTS")
        try:
            sheet_uts = spreadsheet.worksheet("Jadwal UTS")
            st.dataframe(pd.DataFrame(sheet_uts.get_all_records()), use_container_width=True)
        except Exception:
            st.info("Tab 'Jadwal UTS' belum tersedia atau tidak ada data.")

    # --- HALAMAN: JADWAL UAS ---
    elif pilihan_menu == "Jadwal UAS":
        st.title("🎓 Jadwal UAS")
        try:
            sheet_uas = spreadsheet.worksheet("Jadwal UAS")
            st.dataframe(pd.DataFrame(sheet_uas.get_all_records()), use_container_width=True)
        except Exception:
            st.info("Tab 'Jadwal UAS' belum tersedia atau tidak ada data.")