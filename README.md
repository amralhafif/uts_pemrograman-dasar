# Sistem Pengolahan Data Mahasiswa Baru (PMB) CLI

Aplikasi berbasis Command Line Interface (CLI) untuk memvalidasi, membersihkan duplikat, mengklasifikasikan kelulusan, dan merekapitulasi data calon mahasiswa baru dari file CSV ke format JSON dan CSV bersih. Dibuat untuk memenuhi Ujian Tengah Semester (UTS) Pemrograman Dasar (TK091) Universitas Amikom Yogyakarta.

## Struktur Program
```text
uts_pmb_cli/
├── main.py                      # Entry point aplikasi CLI & menu interaktif
├── README.md                    # Dokumentasi proyek
├── data/
│   ├── data_camaba.csv          # Dataset input pengujian
│   ├── data_camaba_bersih.csv   # Dataset output bersih (hasil ekspor menu 5)
│   └── output_rekap_pmb.json    # Laporan statistik JSON (hasil ekspor menu 5)
└── pmb_manager/                 # Package buatan sendiri
    ├── __init__.py              # Ekspos fungsi utama package
    ├── validator.py             # Validasi integritas baris CSV & defensive programming
    ├── file_handler.py          # Operasi baca/tulis file CSV dan JSON
    └── processor.py             # Deduplikasi, klasifikasi, pencarian, filter, & rekap
```

## Package & Dependency
- **Python 3.8+**
- **Python Standard Library**: `csv`, `json`, `os`, `sys`, `typing` (tidak menggunakan library eksternal).

## Cara Menjalankan Aplikasi
1. Buka terminal/CMD (atau Terminal di VS Code) dan arahkan ke direktori proyek:
   ```bash
   cd uts_pmb_cli
   ```
2. Pastikan file `data/data_camaba.csv` tersedia.
3. Jalankan perintah berikut:
   ```bash
   python main.py
   ```
4. Pilih menu `1`–`5` untuk mengoperasikan fitur aplikasi. Pilih menu `5` untuk menghasilkan file keluaran `data/output_rekap_pmb.json` dan `data/data_camaba_bersih.csv`.
