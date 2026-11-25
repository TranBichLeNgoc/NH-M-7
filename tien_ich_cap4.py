import unicodedata
import csv


def bo_dau_tieng_viet(chuoi):
    """Chuyển chuỗi tiếng Việt có dấu thành không dấu và viết thường."""
    chuoi = chuoi.replace("đ", "d").replace("Đ", "D")
    nfkd = unicodedata.normalize("NFKD", chuoi)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def tim_kiem_khong_dau(ds_phim):
    """Tìm kiếm phim theo tên (hỗ trợ gõ không dấu và không phân biệt hoa/thường)."""
    tu_khoa = input("Nhập tên phim cần tìm (có dấu hoặc không dấu): ").strip()
    tu_khoa_khong_dau = bo_dau_tieng_viet(tu_khoa)

    ket_qua = [
        p for p in ds_phim
        if tu_khoa_khong_dau in bo_dau_tieng_viet(p["ten"])
    ]

    if not ket_qua:
        print("Không tìm thấy phim nào khớp với từ khóa.")
        return

    print(f"\nTìm thấy {len(ket_qua)} phim:")
    for p in ket_qua:
        print(f"- [{p['ma']}] {p['ten']} ({p['nam']}) | Thể loại: {p['the_loai']} | Điểm: {p['diem_chung']}")


def xuat_danh_sach_muon_xem(ten_user, ds_phim):
    """Cho phép chọn các mã phim muốn xem và xuất ra tệp CSV riêng của người dùng."""
    nhap_ma = input("Nhập các mã phim muốn lưu (cách nhau dấu phẩy, vd: P0001, P0004): ")
    ds_ma_chon = [m.strip().upper() for m in nhap_ma.split(",") if m.strip()]

    phim_hop_le = [p for p in ds_phim if p["ma"] in ds_ma_chon]
    if not phim_hop_le:
        print("Không có mã phim hợp lệ nào được chọn.")
        return

    ten_file_xuat = f"muon_xem_{ten_user}.csv"
    with open(ten_file_xuat, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ma", "ten", "nam", "the_loai", "diem_chung"])
        for p in phim_hop_le:
            writer.writerow([p["ma"], p["ten"], p["nam"], p["the_loai"], p["diem_chung"]])

    print(f"Đã xuất {len(phim_hop_le)} phim ra tệp '{ten_file_xuat}' thành công!")