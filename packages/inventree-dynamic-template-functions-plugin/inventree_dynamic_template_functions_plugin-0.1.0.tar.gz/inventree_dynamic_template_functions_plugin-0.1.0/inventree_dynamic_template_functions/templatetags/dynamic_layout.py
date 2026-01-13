from __future__ import annotations

from django import template
import qrcode.constants as ECL
from qrcode.exceptions import DataOverflowError
from qrcode.main import QRCode
import math
import report.helpers
from django.utils.safestring import mark_safe
from inventree_dynamic_template_functions.text_formatter import TextFormatter

register = template.Library()

def image_data(img, fmt='PNG') -> str:
    return report.helpers.encode_image_base64(img, fmt)


from dataclasses import dataclass

@dataclass
class QrCode:
    element: str
    width: int
    height: int

    def __html__(self):
        return mark_safe(self.element)

@register.filter
def get_width(qrcode: QrCode) -> str:
    return qrcode.width

@register.filter
def get_height(qrcode: QrCode) -> str:
    return qrcode.height

def generate_contraint_qr_code(data, desired_size, min_module_size, min_error_correction):
    if min_error_correction == "L":
        error_correction_modes = [ECL.ERROR_CORRECT_H, ECL.ERROR_CORRECT_Q, ECL.ERROR_CORRECT_M, ECL.ERROR_CORRECT_L]
    elif min_error_correction == "M":
        error_correction_modes = [ECL.ERROR_CORRECT_H, ECL.ERROR_CORRECT_Q, ECL.ERROR_CORRECT_M]
    elif min_error_correction == "Q":
        error_correction_modes = [ECL.ERROR_CORRECT_H, ECL.ERROR_CORRECT_Q]
    elif min_error_correction == "H":
        error_correction_modes = [ECL.ERROR_CORRECT_H]
    else:
        raise ValueError(f"min_error_correction \"{min_error_correction}\" is not valid for 'pixel_aligned_qrcode' template tag, must be one of L, M, Q, or H")

    max_possible_version = math.floor(((desired_size/min_module_size)-21) / 4 + 1)

    for version in range(1, max_possible_version + 1):
        num_modules = 21 + 4 * (version - 1)
        module_size = math.floor(desired_size / num_modules)

        for error_correction_mode in error_correction_modes:
            print(f"Trying version {version} with mode {error_correction_mode}")

            qr = QRCode(**{
                'box_size': module_size,
                'border': 0,
                'version': version,
                'error_correction': error_correction_mode,
            })
            qr.add_data(data, optimize=True)

            try:
                qr.make(fit=False)
                image = qr.make_image().get_image()

                print(f"QR code generated with: version: {version}, num_modules: {num_modules}, module_size: {module_size}, pixel_size: {module_size*num_modules},error_correction: {error_correction_mode}, width: {image.width}, height: {image.height}")

                return image
            except DataOverflowError as e:
                print(f"Did not fit, trying next. {e}")
                next

    raise ValueError("The given data does not fit a qr code using the given contraints.")


@register.simple_tag()
def pixel_aligned_qrcode(data: str, **kwargs) -> str:
    """Return a byte-encoded QR code image.

    Arguments:
        data: Data to encode

    Keyword Arguments:
        desired_size: Maximum size of the QR code
        pad_vertically: Pad to desired size vertically
        pad_horizontally: Pad to desired size horizontally
        min_module_size: Minimum size of each QR pixel
        min_error_correction: Minimum correction level (L: 7%, M: 15%, Q: 25%, H: 30%) (default = 'M')

    Returns:
        image (str): base64 encoded image data

    """
    data = str(data).strip()

    if not data:
        raise ValueError("No data provided to 'pixel_aligned_qrcode' template tag")

    if not kwargs["desired_size"]:
        raise ValueError("No desired size provided to 'pixel_aligned_qrcode' template tag")

    # Extract other arguments from kwargs
    desired_size = kwargs["desired_size"]
    pad_vertically = kwargs.pop('pad_vertically', False)
    pad_horizontally = kwargs.pop('pad_horizontally', False)
    min_module_size = kwargs.pop('min_module_size', 2)
    min_error_correction = kwargs.pop('min_error_correction', "M")

    image = generate_contraint_qr_code(data, desired_size, min_module_size, min_error_correction)

    image_tag_styles = "width: {image.width}px; height: {image.height}px; "
    height = image.height
    width = image.width

    if pad_vertically:
        remaining_space = desired_size - image.height
        height = desired_size
        image_tag_styles += f"padding-top: {math.floor(remaining_space / 2)}px; padding-bottom: {math.ceil(remaining_space / 2)}px; "

    if pad_horizontally:
        remaining_space = desired_size - image.height
        width = desired_size
        image_tag_styles += f"padding-left: {math.floor(remaining_space / 2)}px; padding-right: {math.ceil(remaining_space / 2)}px; "

    qr_code = QrCode(mark_safe(f"<img class='pixel-aligned-qr' style='{image_tag_styles}' src='{image_data(image)}'>"), width, height)

    return qr_code


@register.simple_tag
def dynamic_text_lines(text: str, height: int, max_lines: int, max_width: int, font: str, font_size: int, min_lines: int = 2, preferred_width: int = None, style: str = "", wrapper_class: str = "dynamic-text-lines") -> str:
    if not preferred_width:
        preferred_width = max_width

    text_formatter = TextFormatter(text=text, font=font, font_size=font_size,
                                   preferred_width=preferred_width, max_width=max_width, max_lines=max_lines)
    lines, font_size, line_count = text_formatter.format()

    html = f"<div class='{wrapper_class}' position: relative; style='width: {max_width}px; height: {height}px; font-size: {font_size}px; {style}'>"

    for line in lines:
        print(line)
        line_height = height / max(line_count, min_lines)
        html += f"<div class='dynamic-text-line' style='width: {max_width}px; height: {line_height}px; line-height: {line_height}px; vertical-align: middle; white-space:nowrap;'>{line}</div>"

    html += "</div>"
    print(html)
    return mark_safe(html)

@register.filter
def subtract(value, arg):
    return value - arg
