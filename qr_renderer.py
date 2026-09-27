"""
qr_renderer.py
Renders QR codes with support for custom module styles, gradients, embedded badges,
SVG export, and PDF printable cards.
"""

import io
import os
import tempfile
from typing import Optional, Tuple
from PIL import Image, ImageDraw
import qrcode
import qrcode.image.svg
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (
    SquareModuleDrawer,
    RoundedModuleDrawer,
    CircleModuleDrawer,
    GappedSquareModuleDrawer,
    HorizontalBarsDrawer,
    VerticalBarsDrawer
)
from qrcode.image.styles.colormasks import (
    SolidFillColorMask,
    RadialGradiantColorMask,
    SquareGradiantColorMask,
    HorizontalGradiantColorMask
)
from fpdf import FPDF


def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    """Convert hex string '#RRGGBB' to (R, G, B) tuple."""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join([c * 2 for c in hex_str])
    return int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)


def get_error_correction_constant(level: str):
    mapping = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H,
    }
    return mapping.get(level.upper(), qrcode.constants.ERROR_CORRECT_M)


def render_qr_image(
    payload: str,
    box_size: int = 10,
    border: int = 3,
    error_correction: str = "H",
    module_style: str = "rounded",
    color_mode: str = "solid",
    front_color_hex: str = "#0F172A",
    front_color_2_hex: str = "#2563EB",
    back_color_hex: str = "#FFFFFF",
    transparent_bg: bool = False,
    logo_img: Optional[Image.Image] = None,
    logo_scale: float = 0.22,
) -> Tuple[Image.Image, bytes]:
    """
    Renders a high-resolution PIL Image and PNG bytes for the given payload.
    """
    # Always upgrade to error correction H if a logo is embedded to ensure 100% scan reliability
    if logo_img is not None:
        ec_const = qrcode.constants.ERROR_CORRECT_H
    else:
        ec_const = get_error_correction_constant(error_correction)

    qr = qrcode.QRCode(
        version=None,
        error_correction=ec_const,
        box_size=box_size,
        border=border,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    # Resolve module drawer
    drawer_map = {
        "square": SquareModuleDrawer(),
        "rounded": RoundedModuleDrawer(),
        "circle": CircleModuleDrawer(),
        "gapped": GappedSquareModuleDrawer(),
        "horizontal_bars": HorizontalBarsDrawer(),
        "vertical_bars": VerticalBarsDrawer(),
    }
    drawer = drawer_map.get(module_style.lower(), RoundedModuleDrawer())

    front_rgb = hex_to_rgb(front_color_hex)
    front2_rgb = hex_to_rgb(front_color_2_hex)
    back_rgb = hex_to_rgb(back_color_hex)

    # Resolve color mask
    if color_mode == "radial_gradient":
        color_mask = RadialGradiantColorMask(
            back_color=back_rgb,
            center_color=front_rgb,
            edge_color=front2_rgb
        )
    elif color_mode == "square_gradient":
        color_mask = SquareGradiantColorMask(
            back_color=back_rgb,
            center_color=front_rgb,
            edge_color=front2_rgb
        )
    elif color_mode == "horizontal_gradient":
        color_mask = HorizontalGradiantColorMask(
            back_color=back_rgb,
            left_color=front_rgb,
            right_color=front2_rgb
        )
    else:
        color_mask = SolidFillColorMask(
            back_color=back_rgb,
            front_color=front_rgb
        )

    # Render base styled image
    styled_img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=drawer,
        color_mask=color_mask,
    )
    pil_img = styled_img.convert("RGBA")

    # If transparent background requested, make pixels matching back_rgb transparent
    if transparent_bg:
        datas = pil_img.getdata()
        new_data = []
        # tolerance
        br, bg, bb = back_rgb
        for item in datas:
            if abs(item[0] - br) < 15 and abs(item[1] - bg) < 15 and abs(item[2] - bb) < 15:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        pil_img.putdata(new_data)

    # Embed logo if provided
    if logo_img is not None:
        pil_img = embed_center_badge(pil_img, logo_img, back_rgb, logo_scale)

    png_buf = io.BytesIO()
    pil_img.save(png_buf, format="PNG", dpi=(300, 300))
    png_bytes = png_buf.getvalue()

    return pil_img, png_bytes


def embed_center_badge(
    qr_img: Image.Image,
    logo_img: Image.Image,
    back_color_rgb: Tuple[int, int, int],
    scale: float = 0.22
) -> Image.Image:
    """
    Safely overlays a logo in the center of the QR code with an anti-aliased
    protective background pad so QR modules don't visually interfere.
    """
    qr_w, qr_h = qr_img.size
    badge_size = int(min(qr_w, qr_h) * max(0.18, min(scale, 0.28)))
    logo_inner_size = int(badge_size * 0.82)

    # Create background circle/rounded badge
    badge = Image.new("RGBA", (badge_size, badge_size), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(badge)
    # Circle badge with soft border
    pad_bg = (back_color_rgb[0], back_color_rgb[1], back_color_rgb[2], 255)
    border_color = (200, 200, 210, 200)
    b_draw.ellipse((1, 1, badge_size - 2, badge_size - 2), fill=pad_bg, outline=border_color, width=2)

    # Resize logo with high quality anti-aliasing
    logo_copy = logo_img.convert("RGBA").copy()
    logo_resized = logo_copy.resize((logo_inner_size, logo_inner_size), Image.Resampling.LANCZOS)

    offset = (badge_size - logo_inner_size) // 2
    badge.paste(logo_resized, (offset, offset), mask=logo_resized)

    # Center on QR code
    pos = ((qr_w - badge_size) // 2, (qr_h - badge_size) // 2)
    qr_img.paste(badge, pos, mask=badge)
    return qr_img


def render_qr_svg(
    payload: str,
    box_size: int = 10,
    border: int = 3,
    error_correction: str = "M",
    front_color_hex: str = "#0F172A",
    back_color_hex: str = "#FFFFFF"
) -> str:
    """
    Renders pure scalable vector graphics (SVG) string.
    """
    ec_const = get_error_correction_constant(error_correction)
    qr = qrcode.QRCode(
        version=None,
        error_correction=ec_const,
        box_size=box_size,
        border=border,
        image_factory=qrcode.image.svg.SvgPathImage
    )
    qr.add_data(payload)
    qr.make(fit=True)

    svg_img = qr.make_image()
    buf = io.BytesIO()
    svg_img.save(buf)
    svg_str = buf.getvalue().decode('utf-8')

    # Inject custom fill colors into SVG
    if front_color_hex and front_color_hex.lower() != "#000000":
        svg_str = svg_str.replace('fill="#000000"', f'fill="{front_color_hex}"')
        svg_str = svg_str.replace('fill="black"', f'fill="{front_color_hex}"')

    return svg_str


def generate_pdf_contact_card(
    qr_img: Image.Image,
    title_text: str = "Scan to Save Contact",
    contact_name: str = "",
    job_org: str = "",
    phone: str = "",
    email: str = "",
    website: str = "",
    note: str = ""
) -> bytes:
    """
    Generates a printable luxury A6 (105mm x 148mm) or standard business card badge PDF.
    """
    class CardPDF(FPDF):
        def header(self):
            pass
        def footer(self):
            pass

    pdf = CardPDF(orientation='P', unit='mm', format=(105, 148))
    pdf.set_auto_page_break(False)
    pdf.add_page()

    # Draw modern top banner
    pdf.set_fill_color(15, 23, 42) # Deep slate
    pdf.rect(0, 0, 105, 26, 'F')

    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(0, 7)
    pdf.cell(105, 6, "DIGITAL CONTACT BADGE", ln=1, align='C')

    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(148, 163, 184)
    pdf.set_xy(0, 14)
    pdf.cell(105, 5, "Scan with any iOS or Android Camera to Save", ln=1, align='C')

    # Save QR image to temp file for FPDF insertion
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        qr_img.save(tmp.name, format='PNG')
        tmp_path = tmp.name

    try:
        # Place QR Code centered
        qr_size = 55 # mm
        qr_x = (105 - qr_size) / 2
        qr_y = 30
        pdf.image(tmp_path, x=qr_x, y=qr_y, w=qr_size, h=qr_size)

        # Contact Details Card box
        info_y = qr_y + qr_size + 4
        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(226, 232, 240)
        pdf.rect(8, info_y, 89, 48, 'FD')

        # Name
        pdf.set_font('Helvetica', 'B', 13)
        pdf.set_text_color(15, 23, 42)
        pdf.set_xy(10, info_y + 4)
        pdf.cell(85, 6, contact_name[:36] if contact_name else "Contact Card", ln=1, align='C')

        # Title & Org
        if job_org:
            pdf.set_font('Helvetica', '', 8)
            pdf.set_text_color(71, 85, 105)
            pdf.set_xy(10, info_y + 11)
            pdf.cell(85, 5, job_org[:48], ln=1, align='C')

        # Contact details list
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(51, 65, 85)
        curr_y = info_y + 18
        if phone:
            pdf.set_xy(14, curr_y)
            pdf.cell(78, 4, f"Phone: {phone}", ln=1, align='L')
            curr_y += 5
        if email:
            pdf.set_xy(14, curr_y)
            pdf.cell(78, 4, f"Email: {email}", ln=1, align='L')
            curr_y += 5
        if website:
            pdf.set_xy(14, curr_y)
            pdf.cell(78, 4, f"Web: {website}", ln=1, align='L')
            curr_y += 5

        # Footer instruction
        pdf.set_font('Helvetica', 'I', 7)
        pdf.set_text_color(148, 163, 184)
        pdf.set_xy(0, 140)
        pdf.cell(105, 4, "Universal vCard 3.0 Standard - Compatible with Apple iOS & Android", ln=1, align='C')

        pdf_buf = pdf.output(dest='S')
        if isinstance(pdf_buf, str):
            pdf_buf = pdf_buf.encode('latin1')
        return bytes(pdf_buf)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
