# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  python-ocr-helper
# FileName:     image_utils.py
# Description:  图片相关工具
# Author:       zhouhanlin
# CreateDate:   2025/12/27
# Copyright ©2011-2025. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
import io
import base64
from PIL import Image
from pathlib import Path
from urllib.parse import quote_plus


def get_file_content_as_base64(path, urlencoded=False):
    """
    获取文件base64编码
    :param path: 文件路径
    :param urlencoded: 是否对结果进行urlencoded
    :return: base64编码信息
    """
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = quote_plus(content)
    return content


def check_image_size(path: str):
    with Image.open(path) as img:
        width, height = img.size  # (宽, 高)

    short_side = min(width, height)
    long_side = max(width, height)

    return {
        "width": width,
        "height": height,
        "short_side": short_side,
        "long_side": long_side,
        "short_ok": short_side >= 64,
        "long_ok": long_side <= 8192,
        "size_ok": short_side >= 64 and long_side <= 8192,
    }


def image_to_base64_with_check(
        *, image_path: str | Path,
        min_side: int = 64,
        max_side: int = 8192,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        urlencoded: bool = False,
) -> dict:
    """
    图片处理一条龙：
    - 校验/修正尺寸
    - base64
    - 可选 urlencode
    - 校验大小 <= 10MB
    :return: dict
    """
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(image_path)

    if image_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        raise ValueError("仅支持 jpg / jpeg / png 格式")

    # --- 打开图片 ---
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        w, h = img.size

        short_side = min(w, h)
        long_side = max(w, h)

        # --- 等比放大（最短边 < min_side） ---
        scale_up = 1.0
        if short_side < min_side:
            scale_up = min_side / short_side

        # --- 等比缩小（最长边 > max_side） ---
        scale_down = 1.0
        if long_side * scale_up > max_side:
            scale_down = max_side / (long_side * scale_up)

        scale = scale_up * scale_down

        if scale != 1.0:
            new_w = int(round(w * scale))
            new_h = int(round(h * scale))
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        else:
            new_w, new_h = w, h

        # --- 转为 bytes ---
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()

    # --- base64 ---
    b64_str = base64.b64encode(img_bytes).decode("utf-8")

    if urlencoded:
        b64_str = quote_plus(b64_str)

    final_size = len(b64_str.encode("utf-8"))

    if final_size > max_bytes:
        raise ValueError(
            f"base64{' + urlencode' if urlencoded else ''} 后大小超限: "
            f"{final_size / 1024 / 1024:.2f}MB"
        )

    return {
        "base64": b64_str,
        "width": new_w,
        "height": new_h,
        "short_side": min(new_w, new_h),
        "long_side": max(new_w, new_h),
        "size_bytes": final_size,
        "size_mb": round(final_size / 1024 / 1024, 3),
        "urlencoded": urlencoded,
    }
