# Aplikasi Manajemen Restoran & F&B (Tahap UTS)

Proyek mata kuliah **Perancangan dan Pemrograman Berorientasi Objek** (PPBO 11.OODP.201)
Universitas Mikroskil - Semester Ganjil 2026/2027. Topik **H2 - Aplikasi Manajemen Restoran & F&B**.

Aplikasi berbasis CLI (terminal) dengan Python. **Semua kode ada dalam satu file: `main.py`.**
Modul **Kasir** terhubung langsung ke modul **Dapur**: pesanan yang diinput kasir otomatis masuk ke
antrian dapur, stok bahan berkurang sesuai resep, dan meja kosong lagi setelah tamu membayar.

## Data awal
- **5 menu**: Nasi Goreng Special, Nasi + Ayam Goreng, Mie Goreng, Es Teh Manis, Kopi Susu
- **8 meja**: meja 1-4 (4 orang), meja 5-6 (6 orang), meja 7-8 (8 orang)

## Fitur UTS
F1 registrasi menu - F2 registrasi meja - F3 buka meja - F4 input pesanan manual - F5 error menu tidak ada -
F6 error meja tidak tersedia - F7 validasi & kurangi stok bahan - F8 kirim pesanan ke dapur -
F9 dapur update status (mulai masak / siap) - F10 hitung total.
Tambahan: kelola stok bahan, bayar tunai + kembalian, dan kosongkan meja.

## Cara Menjalankan
Butuh Python 3.8 atau lebih baru. Tidak perlu install library apa pun.

```
python main.py
```

## Contoh Alur Uji
1. Menu utama -> **1 Kasir** -> **3 Buka meja** (meja 3, 3 tamu)
2. **4 Input pesanan** (kode `MK01`, jumlah 2, catatan "tanpa sayur") lalu kosongkan kode untuk selesai
3. **5 Kirim pesanan ke dapur**, lalu **0** kembali
4. Menu utama -> **2 Dapur** -> **1 Lihat antrian**, **2 Mulai masak** (order `1`, item `1`), **3 Tandai SIAP**
5. Kembali ke **1 Kasir** -> **7 Bayar & kosongkan meja** -> isi uang -> meja 3 kosong lagi

## Isi Folder
```
restoran_app/
  main.py     seluruh kode program (class, fungsi, dan main loop)
  alur/       gambar diagram (use case, class, activity) dalam PNG
  README.md
  .gitignore
```

## Konsep OOP (UTS)
Abstract class `MenuItem` + inheritance (`Makanan`, `Minuman`), polymorphism (`waktu_persiapan()`,
`label_dapur()`), encapsulation (`@property`), dan exception handling (8 class exception).

## Rencana UAS
Split bill, diskon/voucher, pembayaran QRIS/kartu, struk, laporan penjualan, design pattern (>=2),
SOLID (>=3), unit test pytest.

## Anggota Kelompok
| Nama | NIM | Username GitHub |
|------|-----|-----------------|
|      |     |                 |
