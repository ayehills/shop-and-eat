#!/usr/bin/env python3
"""Background removal for the graduate photo using U^2-Net (onnxruntime) + alpha matting.
Produces a clean transparent PNG WITHOUT altering the subject pixels themselves."""
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageFilter
from pymatting import estimate_alpha_cf, estimate_foreground_ml

SRC = "/root/.claude/uploads/e3ac4ded-a387-57b0-a101-d63c5b6d11cb/922d1aff-f6fe366550f540769c50db6febe7703c.jpeg"
OUT = "/home/user/shop-and-eat/flyer/build/graduate_cutout.png"
MODEL = "/root/.u2net/u2netp.onnx"

def u2net_mask(img_rgb):
    sess = ort.InferenceSession(MODEL, providers=["CPUExecutionProvider"])
    inp = sess.get_inputs()[0].name
    im = img_rgb.resize((320, 320), Image.LANCZOS)
    a = np.array(im).astype(np.float32) / 255.0
    a = a / a.max()
    mean = np.array([0.485, 0.456, 0.406], np.float32)
    std = np.array([0.229, 0.224, 0.225], np.float32)
    a = (a - mean) / std
    a = a.transpose(2, 0, 1)[None].astype(np.float32)
    out = sess.run(None, {inp: a})[0][0, 0]
    out = (out - out.min()) / (out.max() - out.min() + 1e-8)
    m = Image.fromarray((out * 255).astype(np.uint8)).resize(img_rgb.size, Image.LANCZOS)
    return np.array(m).astype(np.float32) / 255.0

def make_trimap(mask, lo=0.30, hi=0.70, band=7):
    fg = (mask > hi).astype(np.uint8) * 255
    bg = (mask < lo).astype(np.uint8) * 255
    fg_er = np.array(Image.fromarray(fg).filter(ImageFilter.MinFilter(band)))
    bg_er = np.array(Image.fromarray(bg).filter(ImageFilter.MinFilter(band)))
    tri = np.full(mask.shape, 128, np.uint8)
    tri[fg_er == 255] = 255
    tri[bg_er == 255] = 0
    return tri

def main():
    img = Image.open(SRC).convert("RGB")
    if max(img.size) > 2200:
        r = 2200/max(img.size); img = img.resize((round(img.size[0]*r), round(img.size[1]*r)), Image.LANCZOS)
    print("image:", img.size)
    mask = u2net_mask(img)
    print("coarse mask done")
    tri = make_trimap(mask)
    image_n = np.array(img).astype(np.float64) / 255.0
    trimap_n = tri.astype(np.float64) / 255.0
    print("running alpha matting (closed-form)...")
    alpha = estimate_alpha_cf(image_n, trimap_n)
    fg = estimate_foreground_ml(image_n, alpha)
    rgba = np.zeros((*alpha.shape, 4), np.uint8)
    rgba[..., :3] = np.clip(fg * 255, 0, 255).astype(np.uint8)
    rgba[..., 3] = np.clip(alpha * 255, 0, 255).astype(np.uint8)
    out = Image.fromarray(rgba, "RGBA")
    bbox = out.getbbox()
    if bbox:
        out = out.crop(bbox)
    out.save(OUT)
    print("saved", OUT, out.size)

if __name__ == "__main__":
    main()
