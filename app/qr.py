"""QRコード生成（イベント会場での掲示・印刷用）"""

import io

import qrcode


def generate_qr_png(data: str) -> bytes:
    img = qrcode.make(data, box_size=10, border=4)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
