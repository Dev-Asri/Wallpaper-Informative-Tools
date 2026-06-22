"""Wallpaper image generation - utility functions."""

import ctypes
import os
from PIL import Image, ImageDraw, ImageFont


def get_screen_size():
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def render_wallpaper(items, bg_type="color", bg_color="#1e1e2e", bg_image_path="",
                     width=None, height=None):
    if width is None or height is None:
        width, height = get_screen_size()

    if bg_type == "image" and bg_image_path and os.path.isfile(bg_image_path):
        img = Image.open(bg_image_path).convert("RGB")
        img = img.resize((width, height), Image.LANCZOS)
    else:
        hex_color = bg_color.lstrip("#")
        try:
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except (ValueError, IndexError):
            rgb = (30, 30, 46)
        img = Image.new("RGB", (width, height), rgb)

    draw = ImageDraw.Draw(img)

    for item in items:
        try:
            if item.get("show_label", True):
                try:
                    lfont = ImageFont.truetype(item.get("label_font_name", "Consolas"),
                                              item.get("label_font_size", 14))
                except (OSError, IOError):
                    lfont = ImageFont.load_default()

                lc = item.get("label_font_color", "#ffffff").lstrip("#")
                lrgb = tuple(int(lc[i:i+2], 16) for i in (0, 2, 4)) if len(lc) == 6 else (255, 255, 255)
                draw.text((item.get("label_x", 20), item.get("label_y", 20)),
                         f"{item.get('label', '')}:", fill=lrgb, font=lfont)

            if item.get("show_value", True):
                try:
                    vfont = ImageFont.truetype(item.get("value_font_name", "Consolas"),
                                              item.get("value_font_size", 14))
                except (OSError, IOError):
                    vfont = ImageFont.load_default()

                vc = item.get("value_font_color", "#00ff00").lstrip("#")
                vrgb = tuple(int(vc[i:i+2], 16) for i in (0, 2, 4)) if len(vc) == 6 else (0, 255, 0)
                draw.text((item.get("value_x", 20), item.get("value_y", 20)),
                         item.get("value", ""), fill=vrgb, font=vfont)
        except Exception:
            continue

    return img


def set_wallpaper(img, temp_path=None):
    if temp_path is None:
        temp_path = os.path.join(os.environ["TEMP"], "wallpaper_info_temp.bmp")
    img.save(temp_path, "BMP")

    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, temp_path,
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE,
    )
    return temp_path
