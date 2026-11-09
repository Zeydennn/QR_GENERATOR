import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageTk

from qr_code import buat_qr

UKURAN_PRATINJAU = 300


class Aplikasi(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QR Generator")
        self.resizable(False, False)

        self.gambar = None
        self.foto = None

        utama = ttk.Frame(self, padding=16)
        utama.pack()

        ttk.Label(utama, text="Teks atau tautan:").pack(anchor="w")

        baris_input = ttk.Frame(utama)
        baris_input.pack(fill="x", pady=(2, 12))
        self.kolom_input = ttk.Entry(baris_input, width=40)
        self.kolom_input.pack(side="left", fill="x", expand=True)
        self.kolom_input.focus()
        ttk.Button(baris_input, text="Buat QR", command=self.buat).pack(
            side="left", padx=(8, 0)
        )

        self.kanvas = tk.Canvas(
            utama,
            width=UKURAN_PRATINJAU,
            height=UKURAN_PRATINJAU,
            bg="white",
            highlightthickness=1,
            highlightbackground="#cccccc",
        )
        self.kanvas.pack()

        self.tampilkan_placeholder()

    def tampilkan_placeholder(self):
        self.kanvas.delete("all")
        self.kanvas.create_text(
            UKURAN_PRATINJAU // 2,
            UKURAN_PRATINJAU // 2,
            text="Pratinjau QR tampil di sini",
            fill="#888888",
        )

    def tampilkan(self, gambar):
        sisi = max(gambar.size)
        if sisi < UKURAN_PRATINJAU:
            kelipatan = UKURAN_PRATINJAU // sisi
            pratinjau = gambar.resize(
                (gambar.width * kelipatan, gambar.height * kelipatan),
                Image.Resampling.NEAREST,
            )
        else:
            pratinjau = gambar.copy()
            pratinjau.thumbnail(
                (UKURAN_PRATINJAU, UKURAN_PRATINJAU), Image.Resampling.NEAREST
            )

        self.foto = ImageTk.PhotoImage(pratinjau)
        self.kanvas.delete("all")
        self.kanvas.create_image(
            UKURAN_PRATINJAU // 2, UKURAN_PRATINJAU // 2, image=self.foto
        )

    def buat(self):
        try:
            self.gambar = buat_qr(self.kolom_input.get())
        except ValueError as galat:
            messagebox.showwarning("Peringatan", str(galat))
            return
        self.tampilkan(self.gambar)


def main():
    Aplikasi().mainloop()


if __name__ == "__main__":
    main()
