"""Entry point aplikasi CLI Sistem Pengolahan Data Mahasiswa Baru (PMB)."""

import os
import sys
from typing import Any, Dict, List

from pmb_manager import (
    classify_admission_status,
    confirm_reregistration,
    export_clean_applicants_to_csv,
    export_recap_to_json,
    filter_applicants,
    generate_pmb_recap,
    load_applicants_from_csv,
    remove_duplicate_applicants,
    search_applicants,
)

INPUT_CSV_PATH = os.path.join("data", "data_camaba.csv")
OUTPUT_CSV_PATH = os.path.join("data", "data_camaba_bersih.csv")
OUTPUT_JSON_PATH = os.path.join("data", "output_rekap_pmb.json")


def print_applicants_table(applicants: List[Dict[str, Any]]) -> None:
    """Menampilkan data calon mahasiswa baru dalam format tabel rapi di terminal."""
    if not applicants:
        print("\n[INFO] Tidak ada data calon mahasiswa yang sesuai untuk ditampilkan.")
        return

    header = (
        f"{'No.Daftar':<9} | {'Nama Lengkap':<22} | {'Prodi Pilihan':<17} | "
        f"{'Jalur':<7} | {'Nilai':<6} | {'Kelulusan':<11} | {'Daftar Ulang':<12}"
    )
    print("\n" + "-" * len(header))
    print(header)
    print("-" * len(header))

    for item in applicants:
        nama_potong = (item["nama"][:19] + "...") if len(item["nama"]) > 22 else item["nama"]
        print(
            f"{item['no_daftar']:<9} | {nama_potong:<22} | {item['prodi_pilihan']:<17} | "
            f"{item['jalur_masuk']:<7} | {item['nilai_seleksi']:<6.2f} | "
            f"{item['status_kelulusan']:<11} | {item['status_daftar_ulang']:<12}"
        )
    print("-" * len(header))


def display_menu() -> None:
    """Menampilkan daftar menu utama aplikasi CLI."""
    print("\n=== SISTEM PENGOLAHAN DATA MAHASISWA BARU (PMB) CLI ===")
    print("1. Tampilkan Seluruh Data Pendaftar (Bersih & Terklasifikasi)")
    print("2. Cari Pendaftar (Nama / No. Pendaftaran / Asal Sekolah)")
    print("3. Filter Pendaftar Berdasarkan Program Studi & Kelulusan")
    print("4. Konfirmasi Daftar Ulang Mahasiswa Baru")
    print("5. Lihat Rekapitulasi Statistik PMB & Ekspor ke JSON/CSV")
    print("0. Keluar Aplikasi")


def main() -> None:
    """Fungsi utama untuk menjalankan siklus aplikasi CLI."""
    print("Memuat dataset awal dari:", INPUT_CSV_PATH)
    try:
        raw_applicants, warnings = load_applicants_from_csv(INPUT_CSV_PATH)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[FATAL ERROR] {exc}")
        print("Pastikan file 'data/data_camaba.csv' tersedia sebelum menjalankan program.")
        sys.exit(1)

    if warnings:
        print("\n[PERINGATAN VALIDASI DATA]")
        for warn in warnings:
            print(" -", warn)

    unique_applicants, dup_count = remove_duplicate_applicants(raw_applicants)
    applicants = classify_admission_status(unique_applicants)
    print(f"[SUKSES] {len(applicants)} data mahasiswa baru valid dimuat ({dup_count} duplikat dihapus).")

    while True:
        display_menu()
        try:
            choice = input("Pilih menu (0-5): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nProgram dihentikan oleh pengguna.")
            break

        if choice == "1":
            print_applicants_table(applicants)

        elif choice == "2":
            keyword = input("Masukkan kata kunci (nama / no_daftar / asal sekolah): ")
            results = search_applicants(applicants, keyword)
            print_applicants_table(results)

        elif choice == "3":
            daftar_prodi = sorted({item["prodi_pilihan"] for item in applicants})
            print("Prodi tersedia:", ", ".join(daftar_prodi) if daftar_prodi else "-")
            prodi_input = input("Masukkan nama prodi (atau ketik 'SEMUA'): ")
            hanya_lulus = input("Tampilkan hanya yang Lulus seleksi? (y/n): ").strip().lower() == "y"
            results = filter_applicants(applicants, prodi_input, only_passed=hanya_lulus)
            print_applicants_table(results)

        elif choice == "4":
            reg_id = input("Masukkan Nomor Pendaftaran (contoh: PMB004): ")
            success, message = confirm_reregistration(applicants, reg_id)
            print(f"\n[{'OK' if success else 'INFO'}] {message}")

        elif choice == "5":
            recap = generate_pmb_recap(applicants)
            print("\n--- REKAPITULASI STATISTIK PENERIMAAN MAHASISWA BARU ---")
            print(f"Passing Grade Kelulusan   : {recap['passing_grade']}")
            print(f"Total Pendaftar Unik      : {recap['total_pendaftar_unik']} orang")
            print(f"Total Lulus Seleksi       : {recap['total_lulus']} orang")
            print(f"Total Tidak Lulus         : {recap['total_tidak_lulus']} orang")
            print(f"Sudah Daftar Ulang        : {recap['total_sudah_daftar_ulang']} orang")
            print(f"Persentase Kelulusan      : {recap['persentase_kelulusan']}%")
            print(f"Rata-rata Nilai Global    : {recap['rata_rata_nilai_global']}")
            print("\nRincian per Program Studi:")
            for prodi, stat in recap["rekap_per_prodi"].items():
                print(
                    f" - {prodi:<18}: {stat['jumlah_pendaftar']} pendaftar | "
                    f"Lulus: {stat['jumlah_lulus']} | Daftar Ulang: {stat['sudah_daftar_ulang']} | "
                    f"Rata-rata Nilai: {stat['rata_rata_nilai']}"
                )

            json_ok = export_recap_to_json(OUTPUT_JSON_PATH, recap)
            csv_ok = export_clean_applicants_to_csv(OUTPUT_CSV_PATH, applicants)
            if json_ok and csv_ok:
                print(f"\n[EKSPOR BERHASIL] Output tersimpan ke '{OUTPUT_JSON_PATH}' dan '{OUTPUT_CSV_PATH}'.")

        elif choice == "0":
            print("Terima kasih telah menggunakan Sistem Pengolahan Data Mahasiswa Baru.")
            break

        else:
            print("[PERINGATAN] Pilihan menu tidak valid. Masukkan angka 0 sampai 5.")


if __name__ == "__main__":
    main()
