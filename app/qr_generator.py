"""
QR code generatori — prognoz rasm ichiga Telegram havola.
"""
import qrcode
from io import BytesIO
from PIL import Image


def generate_qr(url="https://t.me/uzhydromet", size=120):
    """QR code rasmini yaratadi (PIL Image)."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0d2137", back_color="white")
    img = img.resize((size, size), Image.LANCZOS)
    return img


def qr_to_numpy(url="https://t.me/uzhydromet", size=120):
    """QR code ni numpy array sifatida qaytaradi (matplotlib uchun)."""
    import numpy as np
    img = generate_qr(url, size)
    return np.array(img.convert("RGBA"))
