<div align="center">

<img src="Gloria.png" width="110" alt="Signa icon" />

# Signa

Centralized archive of square emblem and project artwork assets for `projectGloria` repositories.

<!-- AUTO:BADGES_START -->
<img src="https://img.shields.io/badge/assets-20_emblems-A855F7?style=flat-square" alt="Assets" />
<img src="https://img.shields.io/badge/formats-PNG_%7C_JPEG-2b2d34?style=flat-square" alt="Formats" />
<img src="https://img.shields.io/badge/aspect_ratio-1%3A1-2b2d34?style=flat-square" alt="Aspect Ratio" />
<img src="https://img.shields.io/github/last-commit/projectGloria/Signa?style=flat-square&color=A855F7" alt="Last commit" />
<!-- AUTO:BADGES_END -->

<br /><br />

<img src="docs/assets/banner.svg" alt="Signa banner" width="100%" />

<br /><br />

[Features](#features) • [Gallery](#gallery) • [How it works](#how-it-works) • [Usage](#usage) • [Asset Catalog](#asset-catalog) • [Troubleshooting](#troubleshooting)

</div>

## About

**Signa** is a static image repository hosted at `projectGloria/Signa` that stores high-resolution square (`1:1`) emblems and artwork files in PNG and JPEG formats for `projectGloria` projects. Assets are stored directly at the repository root on the `main` branch and referenced via raw GitHub URLs or a local Git clone. A GitHub Action automatically updates the badges, banner, gallery, and asset catalog whenever root image files are pushed.

## Features

- **Square Project Emblems** — High-resolution `1:1` artwork for `projectGloria` repositories, including alternate variants such as `GloriaRed.png`.
- **Consistent Resolution Tiers** — Assets are stored at high square resolutions (`1212x1212` to `2048x2048`) for downscaling into icons, avatars, and README headers without upscaling artifacts.
- **Root-Level Flat Layout** — Every image resides in the repository root with its project name as the filename, keeping raw URLs short and predictable.
- **Automated README & Banner Sync** — Pushing, renaming, or removing root image files triggers `.github/workflows/update-readme.yml` to regenerate the gallery, catalog metadata, badges, and banner automatically.

## Gallery

<!-- AUTO:GALLERY_START -->
<table align="center">
  <tr>
    <td align="center" width="180"><img src="Ada.png" width="140" alt="Ada" /><br /><code>Ada.png</code></td>
    <td align="center" width="180"><img src="Babbage.png" width="140" alt="Babbage" /><br /><code>Babbage.png</code></td>
    <td align="center" width="180"><img src="BraveTweaker.png" width="140" alt="BraveTweaker" /><br /><code>BraveTweaker.png</code></td>
    <td align="center" width="180"><img src="Carmen.jpg" width="140" alt="Carmen" /><br /><code>Carmen.jpg</code></td>
  </tr>
  <tr>
    <td align="center" width="180"><img src="Emissa.jpg" width="140" alt="Emissa" /><br /><code>Emissa.jpg</code></td>
    <td align="center" width="180"><img src="FFMPEG-Toolkit.jpg" width="140" alt="FFMPEG-Toolkit" /><br /><code>FFMPEG-Toolkit.jpg</code></td>
    <td align="center" width="180"><img src="Gloria.png" width="140" alt="Gloria" /><br /><code>Gloria.png</code></td>
    <td align="center" width="180"><img src="GloriaRed.png" width="140" alt="GloriaRed" /><br /><code>GloriaRed.png</code></td>
  </tr>
  <tr>
    <td align="center" width="180"><img src="Inscriptio.jpg" width="140" alt="Inscriptio" /><br /><code>Inscriptio.jpg</code></td>
    <td align="center" width="180"><img src="Keystroker.jpg" width="140" alt="Keystroker" /><br /><code>Keystroker.jpg</code></td>
    <td align="center" width="180"><img src="Kintsugi.jpg" width="140" alt="Kintsugi" /><br /><code>Kintsugi.jpg</code></td>
    <td align="center" width="180"><img src="LLMSkillz.png" width="140" alt="LLMSkillz" /><br /><code>LLMSkillz.png</code></td>
  </tr>
  <tr>
    <td align="center" width="180"><img src="Lumina.jpeg" width="140" alt="Lumina" /><br /><code>Lumina.jpeg</code></td>
    <td align="center" width="180"><img src="Lyra.png" width="140" alt="Lyra" /><br /><code>Lyra.png</code></td>
    <td align="center" width="180"><img src="Mutatio.jpg" width="140" alt="Mutatio" /><br /><code>Mutatio.jpg</code></td>
    <td align="center" width="180"><img src="Quick%20Notes.jpeg" width="140" alt="Quick Notes" /><br /><code>Quick Notes.jpeg</code></td>
  </tr>
  <tr>
    <td align="center" width="180"><img src="Simulacrum.jpg" width="140" alt="Simulacrum" /><br /><code>Simulacrum.jpg</code></td>
    <td align="center" width="180"><img src="Tabula%20Rasa.png" width="140" alt="Tabula Rasa" /><br /><code>Tabula Rasa.png</code></td>
    <td align="center" width="180"><img src="Vulpes.png" width="140" alt="Vulpes" /><br /><code>Vulpes.png</code></td>
    <td align="center" width="180"><img src="Windows%20Tweaks.png" width="140" alt="Windows Tweaks" /><br /><code>Windows Tweaks.png</code></td>
  </tr>
</table>
<!-- AUTO:GALLERY_END -->

## How it works

```mermaid
flowchart LR
    A["Artwork File (PNG / JPEG)"] --> B["Committed to main Root"]
    B --> C{"Consumption Mode"}
    C -- "Remote Embed" --> D["raw.githubusercontent.com URL"]
    C -- "Local Build / Packaging" --> E["git clone projectGloria/Signa"]
    D --> F["READMEs & GitHub Profiles"]
    E --> G["App Icons & Local Assets"]
```

## Usage

### Embed via Raw GitHub URL

Reference any file directly from the `main` branch in Markdown or HTML:

```html
<img src="https://raw.githubusercontent.com/projectGloria/Signa/main/Gloria.png" width="128" alt="Gloria" />
```

For filenames containing spaces (`Quick Notes.jpeg`, `Tabula Rasa.png`, `Windows Tweaks.png`), percent-encode spaces as `%20`:

```html
<img src="https://raw.githubusercontent.com/projectGloria/Signa/main/Tabula%20Rasa.png" width="128" alt="Tabula Rasa" />
```

### Clone Locally

```bash
git clone https://github.com/projectGloria/Signa.git
```

## Asset Catalog

<!-- AUTO:CATALOG_START -->
| File | Format | Resolution | Size | Background Hex |
| :--- | :--- | :--- | :--- | :--- |
| [`Ada.png`](Ada.png) | PNG | `1254x1254` | 2.84 MB | `#910204` |
| [`Babbage.png`](Babbage.png) | PNG | `1254x1254` | 2.80 MB | `#A30201` |
| [`BraveTweaker.png`](BraveTweaker.png) | PNG | `1254x1254` | 2.84 MB | `#F72002` |
| [`Carmen.jpg`](Carmen.jpg) | JPG | `2048x2048` | 3.47 MB | `#43141A` |
| [`Emissa.jpg`](Emissa.jpg) | JPG | `2048x2048` | 2.29 MB | `#F40084` |
| [`FFMPEG-Toolkit.jpg`](FFMPEG-Toolkit.jpg) | JPG | `2048x2048` | 2.45 MB | `#AC08F2` |
| [`Gloria.png`](Gloria.png) | PNG | `1212x1212` | 2.15 MB | `#7907B9` |
| [`GloriaRed.png`](GloriaRed.png) | PNG | `1212x1212` | 2.24 MB | `#B90707` |
| [`Inscriptio.jpg`](Inscriptio.jpg) | JPG | `2048x2048` | 2.06 MB | `#0A8485` |
| [`Keystroker.jpg`](Keystroker.jpg) | JPG | `2048x2048` | 1.62 MB | `#9E0B28` |
| [`Kintsugi.jpg`](Kintsugi.jpg) | JPG | `2048x2048` | 2.13 MB | `#000000` |
| [`LLMSkillz.png`](LLMSkillz.png) | PNG | `1254x1254` | 2.54 MB | `#0058FD` |
| [`Lumina.jpeg`](Lumina.jpeg) | JPEG | `2048x2048` | 1.85 MB | `#0A4CBA` |
| [`Lyra.png`](Lyra.png) | PNG | `1254x1254` | 3.22 MB | `#ECA402` |
| [`Mutatio.jpg`](Mutatio.jpg) | JPG | `2048x2048` | 2.19 MB | `#137952` |
| [`Quick Notes.jpeg`](Quick%20Notes.jpeg) | JPEG | `2048x2048` | 1.73 MB | `#F37A11` |
| [`Simulacrum.jpg`](Simulacrum.jpg) | JPG | `2048x2048` | 1.78 MB | `#FFFFFF` |
| [`Tabula Rasa.png`](Tabula%20Rasa.png) | PNG | `1254x1254` | 2.71 MB | `#6F2587` |
| [`Vulpes.png`](Vulpes.png) | PNG | `1254x1254` | 2.93 MB | `#FC5002` |
| [`Windows Tweaks.png`](Windows%20Tweaks.png) | PNG | `1254x1254` | 2.34 MB | `#D20302` |
<!-- AUTO:CATALOG_END -->

## Troubleshooting

- **Broken image link for multi-word filenames** — Replace literal spaces with `%20` in Markdown image links and raw URLs (for example, `Quick%20Notes.jpeg`, `Tabula%20Rasa.png`, and `Windows%20Tweaks.png`).
- **404 after format conversion** — Check the exact extension in the [Asset Catalog](#asset-catalog); for example, `Lyra.jpg` was replaced by `Lyra.png`, and both `.jpg` and `.jpeg` extensions are used across the repository.
- **Case sensitivity on GitHub URLs** — Raw GitHub URLs are case-sensitive; match the exact casing shown in the catalog (e.g., `FFMPEG-Toolkit.jpg`, `BraveTweaker.png`).
