#!/usr/bin/env python3
"""Scan root emblem images and update README.md and docs/assets/banner.svg."""

from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import quote

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
README_PATH = REPO_ROOT / "README.md"
BANNER_PATH = REPO_ROOT / "docs" / "assets" / "banner.svg"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
GALLERY_COLUMNS = 4


def collect_assets() -> list[dict]:
    assets = []
    for entry in sorted(REPO_ROOT.iterdir(), key=lambda p: p.name.lower()):
        if not entry.is_file():
            continue
        ext = entry.suffix.lower()
        if ext not in IMAGE_EXTENSIONS:
            continue

        size_mb = entry.stat().st_size / (1024 * 1024)
        with Image.open(entry) as img:
            width, height = img.size
            rgb = img.convert("RGB")
            r, g, b = rgb.getpixel((min(10, width - 1), min(10, height - 1)))
            bg_hex = f"#{r:02X}{g:02X}{b:02X}"

        assets.append(
            {
                "name": entry.name,
                "stem": entry.stem,
                "url": quote(entry.name),
                "fmt": ext.lstrip(".").upper(),
                "norm_fmt": "JPEG" if ext in {".jpg", ".jpeg"} else ext.lstrip(".").upper(),
                "width": width,
                "height": height,
                "size_mb": f"{size_mb:.2f} MB",
                "bg_hex": bg_hex,
            }
        )
    return assets


def format_list(assets: list[dict]) -> list[str]:
    order = ["PNG", "JPEG", "WEBP"]
    present = {a["norm_fmt"] for a in assets}
    return [fmt for fmt in order if fmt in present]


def resolution_label(assets: list[dict]) -> str:
    if not assets:
        return "0px"
    dims = [d for a in assets for d in (a["width"], a["height"])]
    lo, hi = min(dims), max(dims)
    return f"{lo}px" if lo == hi else f"{lo}px–{hi}px"


def build_badges(assets: list[dict]) -> str:
    count = len(assets)
    emblem_word = "emblem" if count == 1 else "emblems"
    fmts = format_list(assets)
    fmt_badge = "_%7C_".join(fmts) if fmts else "none"
    return "\n".join(
        [
            f'<img src="https://img.shields.io/badge/assets-{count}_{emblem_word}-A855F7?style=flat-square" alt="Assets" />',
            f'<img src="https://img.shields.io/badge/formats-{fmt_badge}-2b2d34?style=flat-square" alt="Formats" />',
            '<img src="https://img.shields.io/badge/aspect_ratio-1%3A1-2b2d34?style=flat-square" alt="Aspect Ratio" />',
            '<img src="https://img.shields.io/github/last-commit/projectGloria/Signa?style=flat-square&color=A855F7" alt="Last commit" />',
        ]
    )


def build_gallery(assets: list[dict]) -> str:
    lines = ['<table align="center">']
    for i in range(0, len(assets), GALLERY_COLUMNS):
        row = assets[i : i + GALLERY_COLUMNS]
        lines.append("  <tr>")
        for asset in row:
            lines.append(
                f'    <td align="center" width="180">'
                f'<img src="{asset["url"]}" width="140" alt="{asset["stem"]}" />'
                f'<br /><code>{asset["name"]}</code></td>'
            )
        for _ in range(GALLERY_COLUMNS - len(row)):
            lines.append('    <td align="center" width="180"></td>')
        lines.append("  </tr>")
    lines.append("</table>")
    return "\n".join(lines)


def build_catalog(assets: list[dict]) -> str:
    lines = [
        "| File | Format | Resolution | Size | Background Hex |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for asset in assets:
        lines.append(
            f'| [`{asset["name"]}`]({asset["url"]}) '
            f'| {asset["fmt"]} '
            f'| `{asset["width"]}x{asset["height"]}` '
            f'| {asset["size_mb"]} '
            f'| `{asset["bg_hex"]}` |'
        )
    return "\n".join(lines)


def replace_block(content: str, marker: str, replacement: str) -> str:
    pattern = re.compile(
        rf"(<!-- AUTO:{marker}_START -->\r?\n).*?(\r?\n<!-- AUTO:{marker}_END -->)",
        re.DOTALL,
    )
    updated, count = pattern.subn(rf"\g<1>{replacement}\g<2>", content, count=1)
    if count != 1:
        raise ValueError(f"Marker block AUTO:{marker} not found in {README_PATH}")
    return updated


def build_banner(assets: list[dict]) -> str:
    count = len(assets)
    emblem_word = "Square Emblem" if count == 1 else "Square Emblems"
    fmts = format_list(assets)
    fmt_label = " &amp; ".join(fmts) if fmts else "No Assets"
    pills = [
        f"{count} {emblem_word}",
        fmt_label,
        resolution_label(assets),
        "Raw GitHub URLs",
    ]

    pill_elements = []
    x = 64
    gap = 14
    for label in pills:
        visible_len = len(label.replace("&amp;", "&"))
        width = max(130, visible_len * 9 + 54)
        pill_elements.append(
            f'      <rect x="{x}" y="220" width="{width}" height="44" rx="10" fill="#181A20" stroke="#2C2F3A" stroke-width="1" />\n'
            f'      <circle cx="{x + 22}" cy="242" r="5" fill="#A855F7" />\n'
            f'      <text x="{x + 38}" y="247">{label}</text>'
        )
        x += width + gap

    pills_svg = "\n\n".join(pill_elements)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 320" width="1200" height="320" role="img" aria-label="Signa banner">
  <defs>
    <radialGradient id="ambientGlow" cx="0%" cy="50%" r="48%" fx="0%" fy="50%">
      <stop offset="0%" stop-color="#A855F7" stop-opacity="0.28" />
      <stop offset="100%" stop-color="#A855F7" stop-opacity="0" />
    </radialGradient>
    <clipPath id="cardClip">
      <rect x="0.5" y="0.5" width="1199" height="319" rx="18" />
    </clipPath>
  </defs>

  <g clip-path="url(#cardClip)">
    <!-- Background -->
    <rect x="0.5" y="0.5" width="1199" height="319" rx="18" fill="#111216" stroke="#262830" stroke-width="1" />

    <!-- Ambient left glow -->
    <rect x="0" y="0" width="640" height="320" fill="url(#ambientGlow)" />

    <!-- Right geometric diagonal lines -->
    <line x1="940" y1="-20" x2="1120" y2="340" stroke="#A855F7" stroke-opacity="0.22" stroke-width="1.5" />
    <line x1="1010" y1="-20" x2="1190" y2="340" stroke="#A855F7" stroke-opacity="0.22" stroke-width="1.5" />
    <line x1="1080" y1="-20" x2="1260" y2="340" stroke="#A855F7" stroke-opacity="0.22" stroke-width="1.5" />

    <!-- Left accent bar -->
    <rect x="4" y="40" width="8" height="240" rx="4" fill="#A855F7" />

    <!-- Title & Subtitle -->
    <text x="64" y="128" font-family="system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif" font-size="52" font-weight="800" fill="#A855F7">Signa</text>
    <text x="64" y="172" font-family="system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif" font-size="22" font-weight="400" fill="#D4D4D8">Centralized emblem and artwork archive for projectGloria repositories</text>

    <!-- Feature Pills -->
    <g font-family="system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif" font-size="16" fill="#E4E4E7">
{pills_svg}
    </g>
  </g>
</svg>
"""


def main() -> None:
    assets = collect_assets()

    readme = README_PATH.read_text(encoding="utf-8")
    readme = replace_block(readme, "BADGES", build_badges(assets))
    readme = replace_block(readme, "GALLERY", build_gallery(assets))
    readme = replace_block(readme, "CATALOG", build_catalog(assets))
    README_PATH.write_text(readme, encoding="utf-8", newline="\n")

    BANNER_PATH.parent.mkdir(parents=True, exist_ok=True)
    BANNER_PATH.write_text(build_banner(assets), encoding="utf-8", newline="\n")

    print(f"Updated README.md and banner.svg for {len(assets)} assets.")


if __name__ == "__main__":
    main()
