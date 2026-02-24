#!/usr/bin/env python3
"""
Generate 80x80 placeholder PNG logos for AI sales tools.

Each logo is a solid colored circle with white initials centered on it.
Colors cycle through a professional palette for visual variety.
"""

import os
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SIZE = 80  # px
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "img", "logos")

# Professional color palette (hex)
PALETTE = [
    "#1B2A4A",  # navy
    "#0D7377",  # teal
    "#E76F51",  # coral
    "#6C4AB6",  # purple
    "#2D6A4F",  # green
    "#D4A373",  # warm tan
    "#3A86FF",  # bright blue
    "#8338EC",  # vivid purple
    "#FF006E",  # hot pink
    "#2EC4B6",  # aqua
    "#E63946",  # red
    "#457B9D",  # steel blue
    "#264653",  # dark teal
    "#F4A261",  # sandy orange
    "#6A994E",  # olive green
]

# slug -> initials mapping
TOOLS = {
    "11x": "11",
    "artisan": "AR",
    "aisdr": "AI",
    "salesforge": "SF",
    "aviso": "AV",
    "boostup": "BU",
    "revenue-grid": "RG",
    "bombora": "BO",
    "usergems": "UG",
    "warmly": "WA",
    "leadfeeder": "LF",
    "second-nature": "SN",
    "mindtickle": "MT",
    "allego": "AL",
    "hyperbound": "HB",
    "highspot": "HS",
    "showpad": "SP",
    "mailshake": "MS",
    "saleshandy": "SH",
    "woodpecker": "WP",
    "leadiq": "LI",
    "cognism": "CO",
    "kaspr": "KA",
    "people-data-labs": "PD",
    "fullenrich": "FE",
    "avoma": "AV",
    "fireflies": "FF",
    "revenue-io": "RI",
    "klenty": "KL",
    "mixmax": "MX",
    "monday-crm": "MC",
    "freshsales": "FS",
    "close": "CL",
    "heygen": "HG",
    "autobound": "AB",
    "regie": "RE",
    "koncert": "KO",
    "justcall": "JC",
    "reclaim": "RC",
    "kronologic": "KR",
}


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert a hex color string to an (R, G, B) tuple."""
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def get_font(size: int):
    """Try to load a clean system font; fall back to PIL default."""
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSText.ttf",
        "/System/Library/Fonts/SFCompact.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    # Ultimate fallback
    return ImageFont.load_default()


def generate_logo(slug: str, initials: str, color_rgb: tuple, output_dir: str):
    """Create and save an 80x80 PNG with a colored circle and white initials."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw filled circle
    draw.ellipse([0, 0, SIZE - 1, SIZE - 1], fill=color_rgb)

    # Pick a font size that fits nicely inside the circle
    font_size = 28 if len(initials) <= 2 else 22
    font = get_font(font_size)

    # Center the text using textbbox
    bbox = draw.textbbox((0, 0), initials, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (SIZE - text_w) / 2 - bbox[0]
    y = (SIZE - text_h) / 2 - bbox[1]

    draw.text((x, y), initials, fill=(255, 255, 255), font=font)

    filepath = os.path.join(output_dir, f"{slug}.png")
    img.save(filepath, "PNG")
    return filepath


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    palette_rgb = [hex_to_rgb(c) for c in PALETTE]
    generated = []

    for idx, (slug, initials) in enumerate(TOOLS.items()):
        color = palette_rgb[idx % len(palette_rgb)]
        path = generate_logo(slug, initials, color, OUTPUT_DIR)
        generated.append(path)
        print(f"  [OK] {slug}.png  ({initials})  color={PALETTE[idx % len(PALETTE)]}")

    print(f"\nGenerated {len(generated)} logos in {os.path.abspath(OUTPUT_DIR)}")


if __name__ == "__main__":
    main()
