"""Module file_handler untuk membaca data CSV dan menyimpan hasil ke JSON/CSV."""

import csv
import json
import os
from typing import Any, Dict, List, Tuple

from .validator import validate_applicant_row


def load_applicants_from_csv(filepath: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Membaca data calon mahasiswa baru dari file CSV dan memvalidasi setiap baris.

    Args:
        filepath: Lokasi path file CSV input.

    Returns:
        Tuple berisi (list_pendaftar_valid, list_peringatan_validasi).

    Raises:
        FileNotFoundError: Jika file CSV tidak ditemukan.
        ValueError: Jika file CSV kosong atau strukturnya rusak.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File input tidak ditemukan di path: '{filepath}'")

    valid_applicants: List[Dict[str, Any]] = []
    warnings: List[str] = []

    try:
        with open(filepath, mode="r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                raise ValueError("File CSV kosong atau tidak memiliki baris header.")

            for line_num, row in enumerate(reader, start=2):
                is_valid, result = validate_applicant_row(row, line_num)
                if is_valid:
                    valid_applicants.append(result)
                else:
                    warnings.append(result)
    except csv.Error as exc:
        raise ValueError(f"Terjadi kesalahan parsing CSV: {exc}") from exc

    return valid_applicants, warnings


def export_recap_to_json(filepath: str, recap_data: Dict[str, Any]) -> bool:
    """Menyimpan hasil rekapitulasi PMB ke dalam file JSON.

    Args:
        filepath: Path tujuan penyimpanan file JSON.
        recap_data: Dictionary berisi hasil analisis dan statistik PMB.

    Returns:
        True jika penyimpanan berhasil, False jika gagal.
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, mode="w", encoding="utf-8") as file:
            json.dump(recap_data, file, indent=4, ensure_ascii=False)
        return True
    except (OSError, TypeError) as exc:
        print(f"[ERROR] Gagal menyimpan laporan JSON: {exc}")
        return False


def export_clean_applicants_to_csv(filepath: str, applicants: List[Dict[str, Any]]) -> bool:
    """Menyimpan data calon mahasiswa baru yang sudah bersih dan terklasifikasi ke CSV.

    Args:
        filepath: Path tujuan penyimpanan file CSV output.
        applicants: List dictionary data calon mahasiswa baru.

    Returns:
        True jika penyimpanan berhasil, False jika gagal.
    """
    fieldnames = [
        "no_daftar",
        "nama",
        "asal_sekolah",
        "prodi_pilihan",
        "jalur_masuk",
        "nilai_seleksi",
        "status_kelulusan",
        "status_daftar_ulang",
    ]
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(applicants)
        return True
    except OSError as exc:
        print(f"[ERROR] Gagal menyimpan file CSV bersih: {exc}")
        return False
