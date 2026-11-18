"""Module processor untuk deduplikasi, klasifikasi kelulusan, pencarian, filter, dan rekap."""

from typing import Any, Dict, List, Set, Tuple

PASSING_GRADE = 70.0


def remove_duplicate_applicants(
    applicants: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], int]:
    """Menghapus data pendaftar duplikat berdasarkan no_daftar menggunakan struktur data set.

    Args:
        applicants: List dictionary data pendaftar hasil pembacaan CSV.

    Returns:
        Tuple berisi (list_pendaftar_unik, jumlah_duplikat_dihapus).
    """
    seen_ids: Set[str] = set()
    unique_applicants: List[Dict[str, Any]] = []
    duplicate_count = 0

    for item in applicants:
        reg_id = item["no_daftar"]
        if reg_id in seen_ids:
            duplicate_count += 1
        else:
            seen_ids.add(reg_id)
            unique_applicants.append(item)

    return unique_applicants, duplicate_count


def classify_admission_status(
    applicants: List[Dict[str, Any]], passing_grade: float = PASSING_GRADE
) -> List[Dict[str, Any]]:
    """Menambahkan status_kelulusan ('Lulus' / 'Tidak Lulus') pada setiap pendaftar.

    Args:
        applicants: List dictionary pendaftar unik.
        passing_grade: Batas minimum nilai kelulusan (default 70.0).

    Returns:
        List dictionary baru dengan kolom tambahan status_kelulusan.
    """
    classified: List[Dict[str, Any]] = []
    for item in applicants:
        record = dict(item)
        if record["nilai_seleksi"] >= passing_grade:
            record["status_kelulusan"] = "Lulus"
        else:
            record["status_kelulusan"] = "Tidak Lulus"
            # Edge case defensive: peserta yang tidak lulus tidak bisa berstatus Sudah daftar ulang
            record["status_daftar_ulang"] = "Belum"
        classified.append(record)
    return classified


def search_applicants(applicants: List[Dict[str, Any]], keyword: str) -> List[Dict[str, Any]]:
    """Mencari pendaftar berdasarkan nama, nomor pendaftaran, atau asal sekolah.

    Args:
        applicants: List dictionary data pendaftar.
        keyword: Kata kunci pencarian.

    Returns:
        List pendaftar yang cocok dengan kata kunci.
    """
    clean_kw = keyword.strip().lower()
    if not clean_kw:
        return []

    return [
        item
        for item in applicants
        if clean_kw in item["nama"].lower()
        or clean_kw in item["no_daftar"].lower()
        or clean_kw in item["asal_sekolah"].lower()
    ]


def filter_applicants(
    applicants: List[Dict[str, Any]], prodi: str, only_passed: bool = False
) -> List[Dict[str, Any]]:
    """Memfilter pendaftar berdasarkan program studi pilihan dan status kelulusan.

    Args:
        applicants: List dictionary data pendaftar.
        prodi: Nama program studi (atau 'SEMUA').
        only_passed: Jika True, hanya mengembalikan peserta dengan status 'Lulus'.

    Returns:
        List pendaftar yang memenuhi kriteria filter.
    """
    target_prodi = prodi.strip().lower()
    return [
        item
        for item in applicants
        if (target_prodi == "semua" or item["prodi_pilihan"].lower() == target_prodi)
        and (not only_passed or item["status_kelulusan"] == "Lulus")
    ]


def confirm_reregistration(applicants: List[Dict[str, Any]], no_daftar: str) -> Tuple[bool, str]:
    """Memperbarui status daftar ulang menjadi 'Sudah' bagi pendaftar yang Lulus.

    Args:
        applicants: List dictionary data pendaftar.
        no_daftar: Nomor pendaftaran mahasiswa baru.

    Returns:
        Tuple (status_berhasil, pesan_informasi).
    """
    target_id = no_daftar.strip().upper()
    for item in applicants:
        if item["no_daftar"] == target_id:
            if item["status_kelulusan"] != "Lulus":
                return (
                    False,
                    f"Ditolak: {item['nama']} ({target_id}) berstatus 'Tidak Lulus', tidak dapat daftar ulang.",
                )
            if item["status_daftar_ulang"] == "Sudah":
                return (
                    False,
                    f"Info: {item['nama']} ({target_id}) sudah melakukan daftar ulang sebelumnya.",
                )
            item["status_daftar_ulang"] = "Sudah"
            return (
                True,
                f"Berhasil: Daftar ulang atas nama {item['nama']} ({target_id}) telah dikonfirmasi.",
            )

    return False, f"Gagal: Nomor pendaftaran '{target_id}' tidak ditemukan."


def generate_pmb_recap(applicants: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Menghitung rekapitulasi statistik PMB secara global dan per program studi.

    Args:
        applicants: List dictionary data pendaftar terklasifikasi.

    Returns:
        Dictionary terstruktur berisi ringkasan total dan rincian tiap prodi.
    """
    if not applicants:
        return {
            "passing_grade": PASSING_GRADE,
            "total_pendaftar_unik": 0,
            "total_lulus": 0,
            "total_tidak_lulus": 0,
            "total_sudah_daftar_ulang": 0,
            "persentase_kelulusan": 0.0,
            "rata_rata_nilai_global": 0.0,
            "rekap_per_prodi": {},
        }

    # Set comprehension untuk mengekstrak daftar program studi unik
    unique_prodi: Set[str] = {item["prodi_pilihan"] for item in applicants}

    total_pendaftar = len(applicants)
    total_lulus = sum(1 for item in applicants if item["status_kelulusan"] == "Lulus")
    total_tidak_lulus = total_pendaftar - total_lulus
    total_daftar_ulang = sum(1 for item in applicants if item["status_daftar_ulang"] == "Sudah")
    avg_global = round(sum(item["nilai_seleksi"] for item in applicants) / total_pendaftar, 2)
    pass_rate = round((total_lulus / total_pendaftar) * 100, 2)

    # Dictionary comprehension untuk menyusun rekapitulasi per program studi
    recap_by_prodi: Dict[str, Dict[str, Any]] = {
        prodi: {
            "jumlah_pendaftar": len([a for a in applicants if a["prodi_pilihan"] == prodi]),
            "jumlah_lulus": sum(
                1
                for a in applicants
                if a["prodi_pilihan"] == prodi and a["status_kelulusan"] == "Lulus"
            ),
            "sudah_daftar_ulang": sum(
                1
                for a in applicants
                if a["prodi_pilihan"] == prodi and a["status_daftar_ulang"] == "Sudah"
            ),
            "rata_rata_nilai": round(
                sum(a["nilai_seleksi"] for a in applicants if a["prodi_pilihan"] == prodi)
                / len([a for a in applicants if a["prodi_pilihan"] == prodi]),
                2,
            ),
        }
        for prodi in sorted(unique_prodi)
    }

    return {
        "passing_grade": PASSING_GRADE,
        "total_pendaftar_unik": total_pendaftar,
        "total_lulus": total_lulus,
        "total_tidak_lulus": total_tidak_lulus,
        "total_sudah_daftar_ulang": total_daftar_ulang,
        "persentase_kelulusan": pass_rate,
        "rata_rata_nilai_global": avg_global,
        "rekap_per_prodi": recap_by_prodi,
    }
