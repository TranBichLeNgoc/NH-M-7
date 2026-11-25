import csv
import os
from datetime import datetime

# --- CẤU HÌNH THAM SỐ TẬP TRUNG (Yêu cầu chung) ---
TRONG_SO_PHU_HOP = 0.6
TRONG_SO_DIEM_CHUNG = 0.4
SO_GOI_Y_MAC_DINH = 5

FILE_KHO = "kho.csv"
FILE_NGUOI_DUNG = "nguoidung.csv"
FILE_DANH_GIA = "danhgia.csv"


def doc_kho_phim(ten_file):
    """Đọc danh sách phim từ tệp CSV và trả về danh sách các từ điển."""
    ds_phim = []
    if not os.path.exists(ten_file):
        return ds_phim
    with open(ten_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["nam"] = int(row["nam"])
            row["diem_chung"] = float(row["diem_chung"])
            # Chuyển chuỗi thể loại thành tập hợp (set) để dùng phép giao
            row["tap_the_loai"] = set(row["the_loai"].split("|"))
            ds_phim.append(row)
    return ds_phim


def doc_nguoi_dung(ten_file):
    """Đọc dữ liệu người dùng từ CSV, trả về dict {ten_dang_nhap: set_the_loai}."""
    nguoi_dung = {}
    if not os.path.exists(ten_file):
        return nguoi_dung
    with open(ten_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tl = set(row["the_loai_yeu_thich"].split("|")) if row["the_loai_yeu_thich"] else set()
            nguoi_dung[row["ten_dang_nhap"]] = tl
    return nguoi_dung


def luu_nguoi_dung(ten_file, ds_nguoi_dung):
    """Ghi đè toàn bộ thông tin người dùng vào tệp CSV."""
    with open(ten_file, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ten_dang_nhap", "the_loai_yeu_thich"])
        for user, tap_tl in ds_nguoi_dung.items():
            writer.writerow([user, "|".join(sorted(tap_tl))])


def doc_danh_gia(ten_file):
    """Đọc lịch sử đánh giá của tất cả người dùng."""
    ds_dg = []
    if not os.path.exists(ten_file):
        return ds_dg
    with open(ten_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["diem_ca_nhan"] = int(row["diem_ca_nhan"])
            ds_dg.append(row)
    return ds_dg


def luu_danh_gia_moi(ten_file, ten_user, ma_phim, diem):
    """Thêm một lượt đánh giá mới vào tệp danhgia.csv."""
    file_ton_tai = os.path.exists(ten_file)
    ngay_hom_nay = datetime.now().strftime("%Y-%m-%d")
    with open(ten_file, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if not file_ton_tai:
            writer.writerow(["ten_dang_nhap", "ma_phim", "diem_ca_nhan", "ngay"])
        writer.writerow([ten_user, ma_phim, diem, ngay_hom_nay])


def lay_phim_da_xem(ten_user, ds_danh_gia):
    """Trả về tập hợp (set) các mã phim mà người dùng hiện tại đã xem."""
    return {dg["ma_phim"] for dg in ds_danh_gia if dg["ten_dang_nhap"] == ten_user}


def tinh_diem_goi_y(phim, tap_tl_yeu_thich):
    """
    Tính điểm gợi ý theo công thức Cấp 3:
    Độ phù hợp = |Tm ∩ Tu| / |Tm|
    Điểm gợi ý = (0.6 * Độ phù hợp + 0.4 * (Rm / 10)) * 100
    """
    tm = phim["tap_the_loai"]
    tu = tap_tl_yeu_thich
    giao = tm.intersection(tu)
    
    if len(tm) == 0:
        do_phu_hop = 0
    else:
        do_phu_hop = len(giao) / len(tm)
        
    diem_tho = TRONG_SO_PHU_HOP * do_phu_hop + TRONG_SO_DIEM_CHUNG * (phim["diem_chung"] / 10.0)
    diem_thang_100 = round(diem_tho * 100)
    return diem_thang_100, giao


def hien_thi_goi_y(ten_user, tap_tl_yeu_thich, ds_phim, ds_danh_gia):
    """Lọc phim chưa xem, tính điểm, sắp xếp và in danh sách gợi ý kèm lý do."""
    da_xem = lay_phim_da_xem(ten_user, ds_danh_gia)
    ket_qua = []

    for phim in ds_phim:
        if phim["ma"] in da_xem:
            continue
        diem_gy, giao = tinh_diem_goi_y(phim, tap_tl_yeu_thich)
        # Chỉ gợi ý những phim có ít nhất 1 thể loại khớp
        if len(giao) > 0:
            ket_qua.append((diem_gy, phim, giao))

    # Sắp xếp giảm dần theo điểm gợi ý, nếu bằng nhau thì xét điểm chung
    ket_qua.sort(key=lambda x: (x[0], x[1]["diem_chung"]), reverse=True)

    print(f"\n{'#':<3} {'Phim':<25} {'Năm':<6} {'Điểm chung':<12} {'Điểm gợi ý':<10}")
    print("-" * 60)
    for idx, (diem_gy, phim, giao) in enumerate(ket_qua[:SO_GOI_Y_MAC_DINH], start=1):
        diem_chung_str = str(phim["diem_chung"]).replace(".", ",")
        print(f"{idx:<3} {phim['ten']:<25} {phim['nam']:<6} {diem_chung_str:<12} {diem_gy:<10}")
        ds_tl_khop = ", ".join(sorted(giao))
        print(f"    Vì sao: {ds_tl_khop} (khớp {len(giao)}/{len(phim['tap_the_loai'])} thể loại của phim)")


def dang_nhap(ds_nguoi_dung, ds_phim):
    """Xử lý đăng nhập hoặc tạo hồ sơ sở thích cho người dùng mới."""
    ten_user = input("Nhập tên đăng nhập: ").strip()
    if ten_user not in ds_nguoi_dung:
        print(f"Tài khoản '{ten_user}' chưa tồn tại. Tiến hành tạo hồ sơ mới!")
        # Lấy toàn bộ thể loại có trong kho
        tat_ca_tl = sorted({tl for p in ds_phim for tl in p["tap_the_loai"]})
        print("Các thể loại hiện có:", ", ".join(tat_ca_tl))
        nhap_tl = input("Nhập các thể loại yêu thích (cách nhau bằng dấu phẩy): ")
        tap_chon = {x.strip() for x in nhap_tl.split(",") if x.strip() in tat_ca_tl}
        ds_nguoi_dung[ten_user] = tap_chon
        luu_nguoi_dung(FILE_NGUOI_DUNG, ds_nguoi_dung)
    return ten_user


def danh_dau_da_xem(ten_user, ds_phim, ds_danh_gia):
    """Cho phép người dùng nhập mã phim đã xem, chấm điểm 1-5 và lưu vào CSV."""
    ma_phim = input("Mã phim: ").strip().upper()
    ma_hop_le = {p["ma"] for p in ds_phim}
    
    if ma_phim not in ma_hop_le:
        print("Lỗi: Mã phim không tồn tại trong kho!")
        return

    while True:
        try:
            diem = int(input("Điểm của bạn (1-5): "))
            if 1 <= diem <= 5:
                break
            print("Vui lòng chỉ nhập số nguyên từ 1 đến 5.")
        except ValueError:
            print("Dữ liệu không hợp lệ, hãy nhập một số.")

    luu_danh_gia_moi(FILE_DANH_GIA, ten_user, ma_phim, diem)
    # Cập nhật ngay trên bộ nhớ
    ds_danh_gia.append({
        "ten_dang_nhap": ten_user,
        "ma_phim": ma_phim,
        "diem_ca_nhan": diem,
        "ngay": datetime.now().strftime("%Y-%m-%d")
    })
    print("Đã lưu. Danh sách gợi ý sẽ được cập nhật.")


def main():
    ds_phim = doc_kho_phim(FILE_KHO)
    ds_nguoi_dung = doc_nguoi_dung(FILE_NGUOI_DUNG)
    ds_danh_gia = doc_danh_gia(FILE_DANH_GIA)

    if not ds_phim:
        print("Không tìm thấy dữ liệu trong kho.csv!")
        return

    print("===== GỢI Ý PHIM =====")
    ten_user = dang_nhap(ds_nguoi_dung, ds_phim)

    while True:
        tap_tl = ds_nguoi_dung[ten_user]
        print("\n" + "=" * 22)
        print(f"Người dùng: {ten_user}")
        print(f"Thể loại yêu thích: {', '.join(sorted(tap_tl))}")
        print("1. Xem danh sách phim trong kho")
        print("2. Cập nhật thể loại yêu thích")
        print("3. Gợi ý cho tôi")
        print("4. Đánh dấu đã xem")
        print("0. Thoát")
        
        chon = input("Chọn chức năng: ").strip()

        if chon == "1":
            for p in ds_phim:
                print(f"[{p['ma']}] {p['ten']} ({p['nam']}) - {p['the_loai']} - Điểm: {p['diem_chung']}")
        elif chon == "2":
            tat_ca_tl = sorted({tl for p in ds_phim for tl in p["tap_the_loai"]})
            print("Thể loại hiện có:", ", ".join(tat_ca_tl))
            nhap_tl = input("Nhập lại các thể loại yêu thích (cách nhau dấu phẩy): ")
            ds_nguoi_dung[ten_user] = {x.strip() for x in nhap_tl.split(",") if x.strip() in tat_ca_tl}
            luu_nguoi_dung(FILE_NGUOI_DUNG, ds_nguoi_dung)
            print("Đã cập nhật sở thích!")
        elif chon == "3":
            hien_thi_goi_y(ten_user, tap_tl, ds_phim, ds_danh_gia)
        elif chon == "4":
            danh_dau_da_xem(ten_user, ds_phim, ds_danh_gia)
        elif chon == "0":
            print("Tạm biệt!")
            break
        else:
            print("Lựa chọn không hợp lệ, vui lòng chọn lại.")


if __name__ == "__main__":
    main()