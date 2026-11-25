import csv
import os
FILE = "danhba.csv"
danhba = {}
if os.path.exists(FILE):
    f = open(FILE, "r")
    reader = csv.reader(f)
    for dong in reader:
        if len(dong) == 2:
            danhba[dong[0]] = dong[1]
    f.close()
while True:
    chon = input("Chon: ")
    if chon == "1":
        ten = input("Ten: ")
        sdt = input("SDT: ")
        danhba[ten] = sdt
    elif chon == "2":
        ten = input("Ten: ")
        if ten in danhba:
            print(ten, ":", danhba[ten])
        else:
            print("Khong tim thay")
    elif chon == "3":
        ten = input("Ten: ")
        if ten in danhba:
            del danhba[ten]
        else:
            print("Khong tim thay")
    elif chon == "4":
        for ten in sorted(danhba):
            print(ten, ":", danhba[ten])
    elif chon == "0":
        f = open(FILE, "w", newline="")
        writer = csv.writer(f)
        for ten in danhba:
            writer.writerow([ten, danhba[ten]])
        f.close()
        break