from abc import ABC, abstractmethod


def format_rupiah(angka):
    return "Rp " + f"{angka:,}".replace(",", ".")


def input_angka(pesan):
    # Ulangi terus sampai user mengetik angka bulat
    while True:
        try:
            return int(input(pesan))
        except ValueError:
            print("Input harus berupa angka bulat! Silakan ulangi.")


# ===== EXCEPTION =====
class RestoranException(Exception): pass
class MenuItemNotFoundException(RestoranException): pass
class TableNotAvailableException(RestoranException): pass
class InsufficientStockException(RestoranException): pass
class BahanNotFoundException(RestoranException): pass
class OrderNotFoundException(RestoranException): pass
class InvalidStatusException(RestoranException): pass
class InsufficientPaymentException(RestoranException): pass


# ===== CLASS MODEL =====
class Bahan:
    def __init__(self, nama, satuan, stok, stok_minimum):
        if nama.strip() == "":
            raise ValueError("Nama bahan tidak boleh kosong.")
        if stok < 0 or stok_minimum < 0:
            raise ValueError("Stok tidak boleh negatif.")
        self._nama = nama.strip()
        self.satuan = satuan
        self._stok = stok
        self.stok_minimum = stok_minimum

    # ---------- property (getter) ----------
    @property
    def nama(self):
        return self._nama

    @property
    def stok(self):
        return self._stok

    # ---------- method ----------
    def tambah_stok(self, jumlah):
        if jumlah <= 0:
            raise ValueError("Jumlah tambah stok harus lebih dari 0.")
        self._stok += jumlah

    def kurangi_stok(self, jumlah):
        if jumlah <= 0:
            raise ValueError("Jumlah pengurangan harus lebih dari 0.")
        if jumlah > self._stok:
            raise ValueError(f"Stok {self._nama} tidak cukup.")
        self._stok -= jumlah

    def perlu_restock(self):
        return self._stok <= self.stok_minimum


class MenuItem(ABC):
    KATEGORI = "Umum"

    def __init__(self, kode, nama, harga, resep):
        MenuItem.validasi_harga(harga)
        if kode.strip() == "" or nama.strip() == "":
            raise ValueError("Kode dan nama menu tidak boleh kosong.")
        self._kode = kode.strip().upper()
        self._nama = nama.strip()
        self._harga = harga
        self._resep = {}
        for bahan in resep:
            self._resep[bahan.strip().lower()] = resep[bahan]

    # ---------- property ----------
    @property
    def kode(self):
        return self._kode

    @property
    def nama(self):
        return self._nama

    @property
    def harga(self):
        return self._harga

    @property
    def resep(self):
        return dict(self._resep)     # kirim salinan supaya data asli aman

    @property
    def kategori(self):
        return self.KATEGORI

    # ---------- static method ----------
    @staticmethod
    def validasi_harga(harga):
        if harga <= 0:
            raise ValueError("Harga menu harus lebih dari 0.")

    # ---------- method biasa ----------
    def tampil_info(self):
        return f"{self._kode} - {self._nama} ({self.KATEGORI}) {format_rupiah(self._harga)}"

    # ---------- abstract method (WAJIB di-override child) ----------
    @abstractmethod
    def waktu_persiapan(self):
        pass

    @abstractmethod
    def label_dapur(self):
        pass


class Makanan(MenuItem):
    KATEGORI = "Makanan"

    def __init__(self, kode, nama, harga, resep, level_pedas=0):
        super().__init__(kode, nama, harga, resep)
        if level_pedas < 0 or level_pedas > 3:
            raise ValueError("Level pedas harus 0 sampai 3.")
        self.level_pedas = level_pedas

    def waktu_persiapan(self):
        return 15

    def label_dapur(self):
        pedas = "tidak pedas"
        if self.level_pedas > 0:
            pedas = f"pedas lv {self.level_pedas}"
        return f"[MAKANAN] {self._nama} ({pedas})"


class Minuman(MenuItem):
    KATEGORI = "Minuman"

    def __init__(self, kode, nama, harga, resep, dingin=True):
        super().__init__(kode, nama, harga, resep)
        self.dingin = dingin

    def waktu_persiapan(self):
        return 5

    def label_dapur(self):
        suhu = "panas"
        if self.dingin:
            suhu = "dingin"
        return f"[MINUMAN] {self._nama} ({suhu})"


class Meja:
    def __init__(self, nomor, kapasitas):
        if nomor <= 0 or kapasitas <= 0:
            raise ValueError("Nomor dan kapasitas meja harus lebih dari 0.")
        self._nomor = nomor
        self._kapasitas = kapasitas
        self._status = "KOSONG"        # KOSONG atau TERISI
        self._jumlah_tamu = 0
        self.order_aktif = None

    @property
    def nomor(self):
        return self._nomor

    @property
    def kapasitas(self):
        return self._kapasitas

    @property
    def status(self):
        return self._status

    @property
    def jumlah_tamu(self):
        return self._jumlah_tamu

    def buka(self, jumlah_tamu):
        if self._status == "TERISI":
            raise TableNotAvailableException(f"Meja {self._nomor} sedang terisi.")
        if jumlah_tamu <= 0:
            raise ValueError("Jumlah tamu harus lebih dari 0.")
        if jumlah_tamu > self._kapasitas:
            raise TableNotAvailableException(
                f"Meja {self._nomor} hanya muat {self._kapasitas} orang (tamu: {jumlah_tamu}).")
        self._status = "TERISI"
        self._jumlah_tamu = jumlah_tamu

    def kosongkan(self):
        self._status = "KOSONG"
        self._jumlah_tamu = 0
        self.order_aktif = None

    def __str__(self):
        return f"Meja {self._nomor:<2} | kapasitas {self._kapasitas:<2} | {self._status}"


class OrderItem:
    # status: DIPESAN -> DIKONFIRMASI -> DIMASAK -> SIAP
    def __init__(self, no, menu, qty, catatan=""):
        if qty <= 0:
            raise ValueError("Jumlah pesanan harus lebih dari 0.")
        self.no = no
        self.menu = menu
        self.qty = qty
        self.catatan = catatan.strip()
        self._status = "DIPESAN"

    @property
    def status(self):
        return self._status

    def subtotal(self):
        return self.menu.harga * self.qty

    def konfirmasi(self):
        self._pindah_status("DIPESAN", "DIKONFIRMASI")

    def mulai_masak(self):
        self._pindah_status("DIKONFIRMASI", "DIMASAK")

    def tandai_siap(self):
        self._pindah_status("DIMASAK", "SIAP")

    def _pindah_status(self, status_asal, status_baru):
        if self._status != status_asal:
            raise InvalidStatusException(
                f"Item #{self.no} berstatus {self._status}, tidak bisa diubah ke {status_baru}.")
        self._status = status_baru


class Order:
    jumlah_order = 0     # penghitung nomor order

    def __init__(self, meja_nomor, jumlah_tamu):
        self.order_id = Order.buat_id_baru()
        self.meja_nomor = meja_nomor
        self.jumlah_tamu = jumlah_tamu
        self._items = []

    @classmethod
    def buat_id_baru(cls):
        cls.jumlah_order += 1
        return cls.jumlah_order

    @property
    def items(self):
        return list(self._items)

    def tambah_item(self, menu, qty, catatan=""):
        item = OrderItem(len(self._items) + 1, menu, qty, catatan)
        self._items.append(item)
        return item

    def cari_item(self, no):
        for item in self._items:
            if item.no == no:
                return item
        return None

    def hitung_total(self):
        total = 0
        for item in self._items:
            total += item.subtotal()
        return total

    def item_belum_dikirim(self):
        hasil = []
        for item in self._items:
            if item.status == "DIPESAN":
                hasil.append(item)
        return hasil

    def semua_siap(self):
        for item in self._items:
            if item.status != "SIAP":
                return False
        return True

    def status_ringkas(self):
        if len(self._items) == 0:
            return "KOSONG"
        if self.semua_siap():
            return "SEMUA SIAP"
        if len(self.item_belum_dikirim()) == len(self._items):
            return "BELUM DIKIRIM KE DAPUR"
        return "DIPROSES DAPUR"


# ===== CLASS SERVICE =====
class Inventori:
    def __init__(self):
        self._daftar_bahan = {}

    def tambah_bahan(self, bahan):
        if bahan.nama.lower() in self._daftar_bahan:
            raise ValueError(f"Bahan '{bahan.nama}' sudah terdaftar.")
        self._daftar_bahan[bahan.nama.lower()] = bahan

    def cari_bahan(self, nama):
        if nama.strip().lower() not in self._daftar_bahan:
            raise BahanNotFoundException(f"Bahan '{nama}' tidak terdaftar di gudang.")
        return self._daftar_bahan[nama.strip().lower()]

    def semua_bahan(self):
        return list(self._daftar_bahan.values())

    def restock(self, nama, jumlah):
        self.cari_bahan(nama).tambah_stok(jumlah)

    def bahan_menipis(self):
        hasil = []
        for bahan in self._daftar_bahan.values():
            if bahan.perlu_restock():
                hasil.append(bahan)
        return hasil

    def porsi_tersedia(self, menu):
        # porsi terkecil dari semua bahan resep
        porsi = []
        for nama, jumlah in menu.resep.items():
            if nama not in self._daftar_bahan:
                return 0
            porsi.append(self._daftar_bahan[nama].stok // jumlah)
        if len(porsi) == 0:
            return 0
        return min(porsi)

    def kurangi_untuk_pesanan(self, menu, qty):
        # cek semua bahan dulu, kalau semua cukup baru stok dikurangi
        kurang = []
        for nama, jumlah in menu.resep.items():
            butuh = jumlah * qty
            try:
                bahan = self.cari_bahan(nama)
            except BahanNotFoundException:
                kurang.append(f"{nama} (tidak terdaftar)")
                continue
            if bahan.stok < butuh:
                kurang.append(f"{bahan.nama} (butuh {butuh}, sisa {bahan.stok} {bahan.satuan})")
        if len(kurang) > 0:
            raise InsufficientStockException(f"Stok tidak cukup untuk {qty}x {menu.nama}: " + "; ".join(kurang))
        for nama, jumlah in menu.resep.items():
            self.cari_bahan(nama).kurangi_stok(jumlah * qty)


class MenuManager:
    def __init__(self):
        self._daftar_menu = {}

    def tambah(self, menu):
        if menu.kode in self._daftar_menu:
            raise ValueError(f"Kode menu '{menu.kode}' sudah dipakai.")
        self._daftar_menu[menu.kode] = menu

    def cari(self, kode):
        if kode.strip().upper() not in self._daftar_menu:
            raise MenuItemNotFoundException(f"Menu dengan kode '{kode}' tidak ditemukan.")
        return self._daftar_menu[kode.strip().upper()]

    def semua(self):
        return list(self._daftar_menu.values())


class MejaManager:
    def __init__(self):
        self._daftar_meja = {}

    def tambah(self, meja):
        if meja.nomor in self._daftar_meja:
            raise ValueError(f"Meja nomor {meja.nomor} sudah terdaftar.")
        self._daftar_meja[meja.nomor] = meja

    def cari(self, nomor):
        if nomor not in self._daftar_meja:
            raise TableNotAvailableException(f"Meja nomor {nomor} tidak ada.")
        return self._daftar_meja[nomor]

    def semua(self):
        return list(self._daftar_meja.values())


class KitchenDisplay:
    def __init__(self):
        self._antrian = {}      # kunci: nomor order

    def terima_order(self, order):
        # dipanggil Kasir saat pesanan dikirim ke dapur
        self._antrian[order.order_id] = order

    def daftar_antrian(self):
        hasil = []
        for order in self._antrian.values():
            for item in order.items:
                if item.status == "DIKONFIRMASI" or item.status == "DIMASAK":
                    hasil.append(order)
                    break
        return hasil

    def _ambil_item(self, order_id, no_item):
        if order_id not in self._antrian:
            raise OrderNotFoundException(f"Order nomor {order_id} tidak ada di antrian dapur.")
        item = self._antrian[order_id].cari_item(no_item)
        if item is None:
            raise OrderNotFoundException(f"Item #{no_item} tidak ada di order {order_id}.")
        return item

    def mulai_masak(self, order_id, no_item):
        item = self._ambil_item(order_id, no_item)
        item.mulai_masak()
        return item

    def tandai_siap(self, order_id, no_item):
        item = self._ambil_item(order_id, no_item)
        item.tandai_siap()
        return item


class Kasir:
    def __init__(self, menu_manager, meja_manager, inventori, kitchen):
        self._menu_manager = menu_manager
        self._meja_manager = meja_manager
        self._inventori = inventori
        self._kitchen = kitchen

    def buka_meja(self, nomor_meja, jumlah_tamu):
        meja = self._meja_manager.cari(nomor_meja)
        meja.buka(jumlah_tamu)
        meja.order_aktif = Order(nomor_meja, jumlah_tamu)
        return meja.order_aktif

    def ambil_order(self, nomor_meja):
        meja = self._meja_manager.cari(nomor_meja)
        if meja.status != "TERISI":
            raise TableNotAvailableException(f"Meja {nomor_meja} belum dibuka.")
        return meja.order_aktif

    def tambah_item(self, nomor_meja, kode_menu, qty, catatan=""):
        order = self.ambil_order(nomor_meja)
        menu = self._menu_manager.cari(kode_menu)
        if qty <= 0:
            raise ValueError("Jumlah pesanan harus lebih dari 0.")
        self._inventori.kurangi_untuk_pesanan(menu, qty)
        return order.tambah_item(menu, qty, catatan)

    def kirim_ke_dapur(self, nomor_meja):
        order = self.ambil_order(nomor_meja)
        item_baru = order.item_belum_dikirim()
        if len(item_baru) == 0:
            raise OrderNotFoundException("Tidak ada item baru yang perlu dikirim ke dapur.")
        for item in item_baru:
            item.konfirmasi()
        self._kitchen.terima_order(order)     # penghubung kasir dan dapur
        return len(item_baru)

    def bayar_dan_kosongkan(self, nomor_meja, uang):
        order = self.ambil_order(nomor_meja)
        if not order.semua_siap():
            raise InvalidStatusException(f"Pesanan meja {nomor_meja} belum semua siap, belum bisa dibayar.")
        total = order.hitung_total()
        if uang < total:
            raise InsufficientPaymentException(f"Uang kurang. Total {format_rupiah(total)}, dibayar {format_rupiah(uang)}.")
        self._meja_manager.cari(nomor_meja).kosongkan()
        return total, uang - total


# ===== APLIKASI (MENU) =====
class AplikasiRestoran:
    def __init__(self):
        self.menu_manager = MenuManager()
        self.meja_manager = MejaManager()
        self.inventori = Inventori()
        self.kitchen = KitchenDisplay()
        self.kasir = Kasir(self.menu_manager, self.meja_manager, self.inventori, self.kitchen)
        self.isi_data_contoh()

    def isi_data_contoh(self):
        # 9 bahan baku: nama, satuan, stok, stok minimum
        for nama, satuan, stok, minimum in [("Nasi", "gram", 5000, 1000), ("Telur", "butir", 40, 10),
                ("Ayam", "potong", 30, 8), ("Mie", "gram", 3000, 600), ("Sayur", "gram", 2000, 400),
                ("Teh", "gram", 500, 100), ("Gula", "gram", 2000, 300), ("Kopi", "gram", 800, 150),
                ("Susu", "ml", 5000, 1000)]:
            self.inventori.tambah_bahan(Bahan(nama, satuan, stok, minimum))

        # 5 menu: kode, nama, harga, resep per porsi
        self.menu_manager.tambah(Makanan("MK01", "Nasi Goreng Special", 25000, {"nasi": 200, "telur": 1, "sayur": 50}, 1))
        self.menu_manager.tambah(Makanan("MK02", "Nasi + Ayam Goreng", 28000, {"ayam": 1, "nasi": 200}))
        self.menu_manager.tambah(Makanan("MK03", "Mie Goreng", 22000, {"mie": 150, "telur": 1, "sayur": 50}, 2))
        self.menu_manager.tambah(Minuman("MN01", "Es Teh Manis", 8000, {"teh": 5, "gula": 20}))
        self.menu_manager.tambah(Minuman("MN02", "Kopi Susu", 18000, {"kopi": 15, "susu": 100, "gula": 10}, False))

        # 8 meja: meja 1-4 muat 4 orang, 5-6 muat 6 orang, 7-8 muat 8 orang
        for nomor in range(1, 9):
            kapasitas = 8
            if nomor <= 4:
                kapasitas = 4
            elif nomor <= 6:
                kapasitas = 6
            self.meja_manager.tambah(Meja(nomor, kapasitas))

    def jalankan(self):
        while True:
            print("\n=== RESTORAN NUSANTARA ===")
            print("1. Kasir / Pelayan\n2. Dapur\n3. Admin\n0. Keluar")
            pilihan = input("Pilih menu: ")
            if pilihan == "1":
                self.menu_kasir()
            elif pilihan == "2":
                self.menu_dapur()
            elif pilihan == "3":
                self.menu_admin()
            elif pilihan == "0":
                print("Program selesai. Terima kasih!")
                break
            else:
                print("Pilihan tidak valid, silakan coba lagi.\n")

    # ----- MENU KASIR -----
    def menu_kasir(self):
        while True:
            print("\n=== MENU KASIR ===")
            print("1. Lihat Menu\n2. Lihat Meja\n3. Buka Meja\n4. Input Pesanan\n5. Kirim ke Dapur\n6. Lihat Pesanan + Total\n7. Bayar & Kosongkan Meja\n0. Kembali")
            pilihan = input("Pilih menu: ")
            try:
                if pilihan == "1":
                    self.tampil_menu()
                elif pilihan == "2":
                    for meja in self.meja_manager.semua():
                        print(meja)
                elif pilihan == "3":
                    nomor = input_angka("Nomor meja: ")
                    order = self.kasir.buka_meja(nomor, input_angka("Jumlah tamu: "))
                    print(f"Meja {nomor} dibuka. Nomor order: {order.order_id}.")
                elif pilihan == "4":
                    self.aksi_input_pesanan()
                elif pilihan == "5":
                    nomor = input_angka("Nomor meja: ")
                    print(f"{self.kasir.kirim_ke_dapur(nomor)} item dari meja {nomor} terkirim ke dapur.")
                elif pilihan == "6":
                    self.tampil_rincian(self.kasir.ambil_order(input_angka("Nomor meja: ")))
                elif pilihan == "7":
                    self.aksi_bayar()
                elif pilihan == "0":
                    break
                else:
                    print("Pilihan tidak valid, silakan coba lagi.\n")
            except (RestoranException, ValueError) as e:
                print(f"GAGAL: {e}")

    def tampil_menu(self):
        print(f"\n{'KODE':<6} {'NAMA':<22} {'HARGA':>10}  PORSI TERSEDIA")
        for m in self.menu_manager.semua():
            print(f"{m.kode:<6} {m.nama:<22} {format_rupiah(m.harga):>10}  {self.inventori.porsi_tersedia(m)}")

    def aksi_input_pesanan(self):
        nomor = input_angka("Nomor meja: ")
        self.kasir.ambil_order(nomor)      # cek dulu meja sudah dibuka
        self.tampil_menu()
        print("\nKetik kode menu, lalu jumlahnya. Kosongkan kode jika sudah selesai.")
        while True:
            kode = input("Kode menu: ")
            if kode == "":
                break
            qty = input_angka("Jumlah: ")
            catatan = input("Catatan (boleh kosong): ")
            try:
                item = self.kasir.tambah_item(nomor, kode, qty, catatan)
                print(f"Ditambahkan: {item.qty}x {item.menu.nama} = {format_rupiah(item.subtotal())}")
            except (RestoranException, ValueError) as e:
                print(f"GAGAL: {e}")
        for bahan in self.inventori.bahan_menipis():
            print(f"PERINGATAN: stok {bahan.nama} menipis ({bahan.stok} {bahan.satuan})")

    def tampil_rincian(self, order):
        print(f"\nOrder No. {order.order_id} | Meja {order.meja_nomor} | Tamu {order.jumlah_tamu} | Status: {order.status_ringkas()}")
        for item in order.items:
            catatan = ""
            if item.catatan != "":
                catatan = f" ({item.catatan})"
            print(f"{item.no}. {item.qty}x {item.menu.nama}{catatan} = {format_rupiah(item.subtotal())} [{item.status}]")
        print(f"TOTAL: {format_rupiah(order.hitung_total())}")

    def aksi_bayar(self):
        nomor = input_angka("Nomor meja: ")
        order = self.kasir.ambil_order(nomor)
        self.tampil_rincian(order)
        if not order.semua_siap():
            print("Pesanan belum semua SIAP, belum bisa dibayar.")
            return
        uang = 0
        if order.hitung_total() > 0:
            uang = input_angka("Uang dibayar (Rp): ")
        total, kembalian = self.kasir.bayar_dan_kosongkan(nomor, uang)
        print(f"Pembayaran berhasil. Total {format_rupiah(total)}, kembalian {format_rupiah(kembalian)}.")
        print(f"Meja {nomor} sekarang KOSONG.")

    # ----- MENU DAPUR -----
    def menu_dapur(self):
        while True:
            print("\n=== MENU DAPUR ===")
            print("1. Lihat Antrian\n2. Mulai Masak Item\n3. Tandai Item Siap\n0. Kembali")
            pilihan = input("Pilih menu: ")
            try:
                if pilihan == "1":
                    self.tampil_antrian()
                elif pilihan == "2" or pilihan == "3":
                    no_order = input_angka("Nomor order: ")
                    no_item = input_angka("Nomor item: ")
                    if pilihan == "2":
                        item = self.kitchen.mulai_masak(no_order, no_item)
                    else:
                        item = self.kitchen.tandai_siap(no_order, no_item)
                    print(f"{item.menu.nama} -> {item.status}")
                elif pilihan == "0":
                    break
                else:
                    print("Pilihan tidak valid, silakan coba lagi.\n")
            except (RestoranException, ValueError) as e:
                print(f"GAGAL: {e}")

    def tampil_antrian(self):
        antrian = self.kitchen.daftar_antrian()
        if len(antrian) == 0:
            print("Antrian dapur kosong.")
        for order in antrian:
            print(f"\nORDER NO. {order.order_id} | Meja {order.meja_nomor}")
            for item in order.items:
                catatan = ""
                if item.catatan != "":
                    catatan = f" -- catatan: {item.catatan}"
                print(f"  {item.no}. {item.qty}x {item.menu.label_dapur()} ~{item.menu.waktu_persiapan()} mnt [{item.status}]{catatan}")

    # ----- MENU ADMIN -----
    def menu_admin(self):
        while True:
            print("\n=== MENU ADMIN ===")
            print("1. Tambah Menu\n2. Tambah Meja\n3. Lihat Stok Bahan\n4. Tambah Bahan\n5. Restock Bahan\n0. Kembali")
            pilihan = input("Pilih menu: ")
            try:
                if pilihan == "1":
                    jenis = input("Jenis menu (1=Makanan, 2=Minuman): ")
                    kode = input("Kode menu: ")
                    nama = input("Nama menu: ")
                    harga = input_angka("Harga: ")
                    resep = {}
                    print("Resep per porsi (kosongkan nama bahan jika sudah selesai):")
                    while True:
                        bahan = input("  Nama bahan: ")
                        if bahan == "":
                            break
                        self.inventori.cari_bahan(bahan)
                        resep[bahan] = input_angka("  Jumlah per porsi: ")
                    if jenis == "1":
                        menu = Makanan(kode, nama, harga, resep, input_angka("Level pedas (0-3): "))
                    elif jenis == "2":
                        menu = Minuman(kode, nama, harga, resep, input("Dingin? (y/n): ").lower() == "y")
                    else:
                        raise ValueError("Jenis menu tidak dikenal.")
                    self.menu_manager.tambah(menu)
                    print("Menu berhasil ditambahkan!")
                elif pilihan == "2":
                    self.meja_manager.tambah(Meja(input_angka("Nomor meja: "), input_angka("Kapasitas: ")))
                    print("Meja berhasil ditambahkan!")
                elif pilihan == "3":
                    for b in self.inventori.semua_bahan():
                        status = "aman"
                        if b.perlu_restock():
                            status = "MENIPIS - restock!"
                        print(f"{b.nama:<8} {b.stok:>6} {b.satuan:<7} (min {b.stok_minimum}) {status}")
                elif pilihan == "4":
                    nama = input("Nama bahan: ")
                    satuan = input("Satuan (gram/butir/ml): ")
                    self.inventori.tambah_bahan(Bahan(nama, satuan, input_angka("Stok awal: "), input_angka("Stok minimum: ")))
                    print("Bahan berhasil ditambahkan!")
                elif pilihan == "5":
                    self.inventori.restock(input("Nama bahan: "), input_angka("Jumlah tambah: "))
                    print("Stok bertambah.")
                elif pilihan == "0":
                    break
                else:
                    print("Pilihan tidak valid, silakan coba lagi.\n")
            except (RestoranException, ValueError) as e:
                print(f"GAGAL: {e}")


# ===== MAIN =====
if __name__ == "__main__":
    x = AplikasiRestoran()
    x.jalankan()
