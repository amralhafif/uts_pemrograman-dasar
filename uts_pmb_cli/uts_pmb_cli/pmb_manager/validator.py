"""Module validator untuk memeriksa validitas baris data calon mahasiswa baru."""

from typing import Any, Dict, Tuple


def validate_applicant_row(row: Dict[str, str], line_number: int) -> Tuple[bool, Any]:
    """Memvalidasi dan membersihkan satu baris data pendaftar dari file CSV.

    Args:
        row: Dictionary mentah hasil pembacaan csv.DictReader.
        line_number: Nomor baris pada file CSV untuk pelaporan error.

    Returns:
        Tuple (True, dict_camaba_bersih) jika valid, atau
        Tuple (False, pesan_error) jika ditemukan format data tidak valid.
    """
    required_columns = [
        "no_daftar",
        "nama",
        "asal_sekolah",
        "prodi_pilihan",
        "jalur_masuk",
        "nilai_seleksi",
        "status_daftar_ulang",
    ]

    for col in required_columns:
        if col not in row or row[col] is None or str(row[col]).strip() == "":
            return False, f"Baris {line_number}: Kolom '{col}' kosong atau tidak ditemukan."

    no_daftar = row["no_daftar"].strip().upper()
    nama = row["nama"].strip()
    asal_sekolah = row["asal_sekolah"].strip()
    prodi_pilihan = row["prodi_pilihan"].strip().title()
    jalur_masuk = row["jalur_masuk"].strip().upper()
    status_daftar_ulang = row["status_daftar_ulang"].strip().title()

    try:
        nilai_seleksi = float(row["nilai_seleksi"].strip())
    except ValueError:
        return (
            False,
            f"Baris {line_number} ({no_daftar}): Nilai seleksi '{row['nilai_seleksi']}' bukan angka valid.",
        )

    if nilai_seleksi < 0.0 or nilai_seleksi > 100.0:
        return (
            False,
            f"Baris {line_number} ({no_daftar}): Nilai seleksi ({nilai_seleksi}) harus di antara 0 - 100.",
        )

    if status_daftar_ulang not in {"Sudah", "Belum"}:
        return (
            False,
            f"Baris {line_number} ({no_daftar}): Status daftar ulang harus 'Sudah' atau 'Belum'.",
        )

    cleaned_record = {
        "no_daftar": no_daftar,
        "nama": nama,
        "asal_sekolah": asal_sekolah,
        "prodi_pilihan": prodi_pilihan,
        "jalur_masuk": jalur_masuk,
        "nilai_seleksi": round(nilai_seleksi, 2),
        "status_daftar_ulang": status_daftar_ulang,
    }
    return True, cleaned_record
