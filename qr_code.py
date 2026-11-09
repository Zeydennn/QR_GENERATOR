import qrcode


def buat_qr(data):
    """Buat gambar kode QR (PIL Image) dari teks atau tautan."""
    if data is None or not data.strip():
        raise ValueError("Teks atau tautan tidak boleh kosong.")

    qr = qrcode.QRCode(border=4)
    qr.add_data(data.strip())
    qr.make(fit=True)

    gambar = qr.make_image(fill_color="black", back_color="white")
    if hasattr(gambar, "get_image"):
        gambar = gambar.get_image()
    return gambar.convert("RGB")
