import tkinter as tk
from tkinter import filedialog
from urllib.parse import quote
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageTk

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


class QRGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(False, False)
        self.root.configure(bg=PAGE_BG)

        self.qr_image = None
        self.photo = None
        self.content_type = "url"
        self.wifi_security = "WPA"
        self._after_id = None

        self.vars = {}
        for key, info in CONTENT_TYPES.items():
            self.vars[key] = {}
            for field_key, _ in info["fields"]:
                var = tk.StringVar()
                var.trace_add("write", lambda *args: self.schedule_update())
                self.vars[key][field_key] = var

        self.create_navbar()
        self.create_hero()

        body = tk.Frame(self.root, bg=PAGE_BG)
        body.pack(fill="both", expand=True, padx=32, pady=(14, 18))
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=0)
        body.rowconfigure(0, weight=1)

        self.left_card = tk.Frame(
            body, bg=WHITE, padx=26, pady=16,
            highlightthickness=1, highlightbackground=BORDER
        )
        self.left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        self.right_card = tk.Frame(
            body, bg=WHITE, padx=26, pady=16, width=360,
            highlightthickness=1, highlightbackground=BORDER
        )
        self.right_card.grid(row=0, column=1, sticky="ns")
        self.right_card.grid_propagate(False)
        self.right_card.pack_propagate(False)

        self.create_type_section()
        self.create_content_section()
        self.create_design_section()
        self.create_preview_section()

        self.build_fields()

    def create_navbar(self):
        nav = tk.Frame(self.root, bg=WHITE, height=64)
        nav.pack(fill="x")
        nav.pack_propagate(False)

        logo = tk.Frame(nav, bg=PRIMARY, width=34, height=34)
        logo.pack(side="left", padx=(32, 10), pady=15)
        logo.pack_propagate(False)
        tk.Label(logo, text="QR", bg=PRIMARY, fg="white",
                 font=(FONT, 11, "bold")).pack(expand=True)

        tk.Label(nav, text="QR-Maker", bg=WHITE, fg=TEXT,
                 font=(FONT, 15, "bold")).pack(side="left")

        tk.Label(nav, text="Gratis  •  Tanpa daftar  •  Langsung unduh",
                 bg=WHITE, fg=MUTED, font=(FONT, 10)).pack(side="right", padx=32)

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

    def create_hero(self):
        hero = tk.Frame(self.root, bg=PAGE_BG)
        hero.pack(fill="x", pady=(14, 0))
        tk.Label(
            hero, text="Pembuat Kode QR Gratis",
            bg=PAGE_BG, fg=TEXT, font=(FONT, 24, "bold")
        ).pack()
        tk.Label(
            hero, text="Pilih jenis, isi konten, atur desain. Kode QR langsung muncul.",
            bg=PAGE_BG, fg=MUTED, font=(FONT, 11)
        ).pack(pady=(4, 0))

    def step_header(self, number, title, top=0):
        row = tk.Frame(self.left_card, bg=WHITE)
        row.pack(fill="x", pady=(top, 10))
        tk.Label(
            row, text=str(number), bg=PRIMARY, fg="white",
            font=(FONT, 9, "bold"), width=2
        ).pack(side="left")
        tk.Label(
            row, text=title, bg=WHITE, fg=TEXT, font=(FONT, 12, "bold")
        ).pack(side="left", padx=(10, 0))

    def create_type_section(self):
        self.step_header(1, "Pilih jenis konten")

        row = tk.Frame(self.left_card, bg=WHITE)
        row.pack(fill="x")
        self.tiles = {}
        for i, (key, info) in enumerate(CONTENT_TYPES.items()):
            row.columnconfigure(i, weight=1, uniform="tile")
            tile = tk.Frame(
                row, bg=WHITE, highlightthickness=2,
                highlightbackground=BORDER, cursor="hand2", height=66
            )
            tile.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 8, 0))
            tile.pack_propagate(False)

            glyph = tk.Label(tile, text=info["glyph"], bg=WHITE, fg=PRIMARY,
                             font=(FONT, 14, "bold"), cursor="hand2")
            glyph.pack(pady=(9, 0))
            caption = tk.Label(tile, text=info["caption"], bg=WHITE, fg=TEXT,
                               font=(FONT, 9), cursor="hand2")
            caption.pack()

            for widget in (tile, glyph, caption):
                widget.bind("<Button-1>", lambda e, k=key: self.select_type(k))
            self.tiles[key] = (tile, glyph, caption)
        self.refresh_tiles()

    def refresh_tiles(self):
        for key, (tile, glyph, caption) in self.tiles.items():
            selected = key == self.content_type
            bg = PRIMARY_SOFT if selected else WHITE
            tile.config(
                bg=bg, highlightbackground=PRIMARY if selected else BORDER
            )
            glyph.config(bg=bg)
            caption.config(bg=bg)

    def create_content_section(self):
        self.step_header(2, "Isi konten", top=16)
        self.fields_frame = tk.Frame(self.left_card, bg=WHITE, height=190)
        self.fields_frame.pack(fill="x")
        self.fields_frame.pack_propagate(False)

    def build_fields(self):
        for child in self.fields_frame.winfo_children():
            child.destroy()

        first_entry = None
        info = CONTENT_TYPES[self.content_type]
        for field_key, label in info["fields"]:
            tk.Label(
                self.fields_frame, text=label, bg=WHITE, fg=MUTED,
                font=(FONT, 9)
            ).pack(anchor="w")
            entry = tk.Entry(
                self.fields_frame, textvariable=self.vars[self.content_type][field_key],
                font=(FONT, 11), bg=WHITE, fg=TEXT, insertbackground=TEXT,
                relief="flat", highlightthickness=1,
                highlightbackground=BORDER, highlightcolor=PRIMARY
            )
            entry.pack(fill="x", ipady=5, pady=(3, 8))
            if first_entry is None:
                first_entry = entry

        if self.content_type == "wifi":
            tk.Label(
                self.fields_frame, text="Keamanan", bg=WHITE, fg=MUTED,
                font=(FONT, 9)
            ).pack(anchor="w")
            Segmented(
                self.fields_frame, ["WPA", "WEP", "Tanpa"],
                self.wifi_security, self.set_wifi_security
            ).pack(fill="x", pady=(3, 0))

        if first_entry is not None:
            first_entry.focus()

    def create_design_section(self):
        self.step_header(3, "Atur desain", top=12)

        grid = tk.Frame(self.left_card, bg=WHITE)
        grid.pack(fill="x")
        grid.columnconfigure(0, weight=1, uniform="design")
        grid.columnconfigure(1, weight=1, uniform="design")

        def caption(row, column, text):
            tk.Label(
                grid, text=text, bg=WHITE, fg=MUTED, font=(FONT, 9)
            ).grid(row=row, column=column, sticky="w", pady=(0, 6))

        caption(0, 0, "Warna QR")
        self.fg_picker = ColorPicker(grid, FG_COLORS, "Hitam", lambda n: self.schedule_update(True))
        self.fg_picker.grid(row=1, column=0, sticky="w", pady=(0, 10))

        caption(0, 1, "Warna latar")
        self.bg_picker = ColorPicker(grid, BG_COLORS, "Putih", lambda n: self.schedule_update(True))
        self.bg_picker.grid(row=1, column=1, sticky="w", pady=(0, 10))

        caption(2, 0, "Bingkai")
        self.frame_seg = Segmented(
            grid, ["Tanpa", "SCAN ME"], "Tanpa",
            lambda o: self.schedule_update(True)
        )
        self.frame_seg.grid(row=3, column=0, sticky="ew", padx=(0, 20))

        caption(2, 1, "Kualitas QR (keterbacaan)")
        quality = tk.Frame(grid, bg=WHITE)
        quality.grid(row=3, column=1, sticky="new")
        self.quality_trough = tk.Frame(quality, bg=SECOND, height=10)
        self.quality_trough.pack(fill="x", pady=(8, 0))
        self.quality_fill = tk.Frame(self.quality_trough, bg=SUCCESS)
        self.quality_label = tk.Label(
            quality, text="Belum ada kode QR", bg=WHITE, fg=MUTED,
            font=(FONT, 9), anchor="w"
        )
        self.quality_label.pack(fill="x", pady=(6, 0))

    def create_preview_section(self):
        card = self.right_card

        tk.Label(
            card, text="Pratinjau", bg=WHITE, fg=TEXT, font=(FONT, 12, "bold")
        ).pack(anchor="w")

        box = tk.Frame(
            card, bg=PAGE_BG, width=PREVIEW_SIZE + 40, height=PREVIEW_SIZE + 40,
            highlightthickness=1, highlightbackground=BORDER
        )
        box.pack(pady=(12, 0))
        box.pack_propagate(False)

        self.preview_label = tk.Label(
            box, text="Kode QR akan\nmuncul di sini",
            bg=PAGE_BG, fg=MUTED, font=(FONT, 11)
        )
        self.preview_label.pack(expand=True)

        self.info_label = tk.Label(
            card, text="", bg=WHITE, fg=MUTED, font=(FONT, 9)
        )
        self.info_label.pack(pady=(8, 0))

        tk.Label(
            card, text="Format unduhan", bg=WHITE, fg=MUTED, font=(FONT, 9)
        ).pack(anchor="w", pady=(10, 6))
        self.format_seg = Segmented(card, ["PNG", "JPG"], "PNG", lambda o: None)
        self.format_seg.pack(fill="x")

        FlatButton(
            card, "Unduh Kode QR", self.save_qr,
            PRIMARY, PRIMARY_HOVER, "white", pady=12
        ).pack(fill="x", pady=(12, 0))
        FlatButton(
            card, "Hapus semua", self.clear_all,
            SECOND, SECOND_HOVER, TEXT
        ).pack(fill="x", pady=(8, 0))

        self.status = tk.Label(
            card, text="Isi konten untuk membuat kode QR",
            bg=WHITE, fg=MUTED, font=(FONT, 9), wraplength=300, justify="left"
        )
        self.status.pack(anchor="w", pady=(10, 0))

    def select_type(self, key):
        self.content_type = key
        self.refresh_tiles()
        self.build_fields()
        self.schedule_update(True)

    def set_wifi_security(self, value):
        self.wifi_security = value
        self.schedule_update(True)

    def schedule_update(self, immediate=False):
        pass

    def set_status(self, message, color=MUTED):
        self.status.config(text=message, fg=color)

    def save_qr(self):
        pass

    def clear_all(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = QRGeneratorApp(root)
    root.mainloop()
