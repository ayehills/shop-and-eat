# Flyer Studio — Purple Graduation Flyer Maker

A Photoshop-style flyer pipeline. It takes a portrait photo and a reference
template and produces a premium, print-ready flyer — background removed,
re-themed, and composited at high resolution.

**Live page:** open `index.html` (also deployable via GitHub Pages).

![Graduation flyer](flyer/graduation-flyer.jpg)

## What it does
- **Background removal** — U²-Net segmentation (ONNX / onnxruntime) followed by
  closed-form **alpha matting** for clean hair & beard edges. The subject's
  pixels are never altered; only the background is removed.
- **Re-theming** — rebuilds a reference template's composition in a new palette
  (here: purple & gold) with 3D metallic type, flying caps, diplomas and bokeh.
- **High-res render** — the layout is authored in self-contained HTML (fonts and
  images embedded as data URIs) and screenshotted at 2× → **2160×2160**.

## Project layout
```
index.html                     landing page + flyer download
flyer/
  cutout.py                    background removal (U²-Net + alpha matting)
  generate.py                  builds the flyer HTML from event info + cutout
  render.js                    renders HTML → 2160×2160 PNG (Playwright/Chromium)
  assets/fonts/                embedded typefaces
  graduation-flyer.png / .jpg  final deliverables
```

## Rebuild
```bash
pip install pillow numpy onnxruntime pymatting
python3 flyer/cutout.py        # -> flyer/build/graduate_cutout.png
python3 flyer/generate.py      # -> flyer/build/flyer.html
node    flyer/render.js        # -> flyer/build/flyer.png
```

To make a **different** flyer, drop a new photo path into `cutout.py` and edit
the event text (name, degree, date, venue) near the bottom of `generate.py`.
