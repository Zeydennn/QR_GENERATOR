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
