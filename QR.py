import tkinter as tk
from tkinter import messagebox
import qrcode
from PIL import Image, ImageTk
APP_TITLE = "QR-Maker - Pembuat Kode QR Gratis"
WINDOW_SIZE = "1060x760"
PREVIEW_SIZE = 260

PAGE_BG = "#f4f6fb"
WHITE = "#ffffff"
BORDER = "#e2e6f0"
TEXT = "#1a1f36"
MUTED = "#6b7390"
PRIMARY = "#3b5bfd"
PRIMARY_HOVER = "#2f49d6"
PRIMARY_SOFT = "#eef1ff"
SECOND = "#eef0f6"
SECOND_HOVER = "#e1e5f0"
DANGER = "#dc2626"
SUCCESS = "#059669"
WARNING = "#d97706"

FONT = "Segoe UI"

EC_LEVELS = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}

EC_DEFAULT = "M"

FG_COLORS = {
    "Hitam": "#111111",
    "Biru": "#1d4ed8",
    "Hijau": "#047857",
    "Ungu": "#6d28d9",
    "Merah": "#b91c1c",
}

BG_COLORS = {
    "Putih": "#ffffff",
    "Krem": "#fff8e7",
    "Biru muda": "#e8f0ff",
    "Hijau muda": "#e6f7ee",
}

CONTENT_TYPES = {
    "url": {
        "glyph": "www", "caption": "Tautan",
        "fields": [("url", "Alamat situs web (contoh: google.com)")],
    },
    "text": {
        "glyph": "Aa", "caption": "Teks",
        "fields": [("text", "Teks bebas")],
    },
    "wifi": {
        "glyph": "WiFi", "caption": "Wi-Fi",
        "fields": [("ssid", "Nama jaringan (SSID)"), ("password", "Kata sandi")],
    },
    "email": {
        "glyph": "@", "caption": "Email",
        "fields": [("to", "Alamat email"), ("subject", "Subjek"), ("body", "Pesan")],
    },
}
class FlatButton(tk.Label):
    def __init__(self, parent, text, command, bg, hover, fg, pady=11):
        super().__init__(
            parent, text=text, bg=bg, fg=fg,
            font=(FONT, 11, "bold"), pady=pady, cursor="hand2"
        )
        self.normal_bg = bg
        self.hover_bg = hover
        self.command = command
        self.bind("<Enter>", lambda e: self.config(bg=self.hover_bg))
        self.bind("<Leave>", lambda e: self.config(bg=self.normal_bg))
        self.bind("<Button-1>", lambda e: self.command())


class Segmented(tk.Frame):
    def __init__(self, parent, options, value, command, bg=WHITE):
        super().__init__(parent, bg=bg)
        self.value = value
        self.command = command
        self.buttons = {}
        for i, option in enumerate(options):
            self.columnconfigure(i, weight=1)
            btn = tk.Label(
                self, text=option, font=(FONT, 10, "bold"),
                pady=6, padx=10, cursor="hand2"
            )
            btn.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 3, 0))
            btn.bind("<Button-1>", lambda e, o=option: self.select(o))
            self.buttons[option] = btn
        self.refresh()

    def refresh(self):
        for option, btn in self.buttons.items():
            if option == self.value:
                btn.config(bg=PRIMARY, fg="white")
            else:
                btn.config(bg=SECOND, fg=MUTED)

    def select(self, option):
        self.value = option
        self.refresh()
        self.command(option)


class ColorPicker(tk.Frame):
    def __init__(self, parent, colors, value, command, bg=WHITE):
        super().__init__(parent, bg=bg)
        self.colors = colors
        self.value = value
        self.command = command
        self.swatches = {}
        for name, hex_color in colors.items():
            swatch = tk.Frame(
                self, width=30, height=30, bg=hex_color,
                highlightthickness=2, highlightbackground=BORDER,
                cursor="hand2"
            )
            swatch.pack(side="left", padx=(0, 8))
            swatch.bind("<Button-1>", lambda e, n=name: self.select(n))
            self.swatches[name] = swatch
        self.refresh()

    def refresh(self):
        for name, swatch in self.swatches.items():
            swatch.config(
                highlightbackground=PRIMARY if name == self.value else BORDER
            )

    def select(self, name):
        self.value = name
        self.refresh()
        self.command(name)

    def hex(self):
        return self.colors[self.value]
def load_font(size):
    for name in ("arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def add_frame(img, fg_color, bg_color, label="SCAN ME"):
    w, h = img.size
    pad = 28
    band = 80
    total_w, total_h = w + pad * 2, h + pad + band

    canvas = Image.new("RGB", (total_w, total_h), bg_color)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        [0, 0, total_w - 1, total_h - 1], radius=30, fill=fg_color
    )
    canvas.paste(img, (pad, pad))

    font = load_font(38)
    box = draw.textbbox((0, 0), label, font=font)
    text_w, text_h = box[2] - box[0], box[3] - box[1]
    x = (total_w - text_w) / 2 - box[0]
    y = pad + h + (band - text_h) / 2 - box[1]
    draw.text((x, y), label, font=font, fill="white")
    return canvas
