#!/usr/bin/env python3
"""Reproducibly extract every logical asset from the original Scratch archive."""
from __future__ import annotations

import json, re, shutil, struct, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "TheMultidirectionalDilemma.sb3"
OUT = ROOT / "assets" / "generated"

def safe(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "_", value.strip()).strip("_")
    return value or "unnamed"

def png_size(data: bytes):
    return list(struct.unpack(">II", data[16:24])) if data[:8] == b"\x89PNG\r\n\x1a\n" else None

def svg_size(data: bytes):
    text = data[:2048].decode("utf8", "ignore")
    def n(key):
        m = re.search(fr'\b{key}=["\']([0-9.]+)', text)
        return float(m.group(1)) if m else None
    w, h = n("width"), n("height")
    return [w, h] if w and h else None

def main() -> None:
    if OUT.exists(): shutil.rmtree(OUT)
    (OUT / "images").mkdir(parents=True)
    (OUT / "audio").mkdir()
    entries = []
    with zipfile.ZipFile(SOURCE) as z:
        project = json.loads(z.read("project.json"))
        (OUT / "project.json").write_text(json.dumps(project, indent=2), encoding="utf8")
        for ti, target in enumerate(project["targets"]):
            defaults = {k: target.get(k) for k in ("size", "direction", "rotationStyle", "visible", "layerOrder", "x", "y")}
            for kind, collection, folder in (("costume", "costumes", "images"), ("sound", "sounds", "audio")):
                for i, item in enumerate(target.get(collection, [])):
                    ext = item["dataFormat"].lower()
                    filename = f"{ti:02d}_{safe(target['name'])}__{i:03d}_{safe(item['name'])}.{ext}"
                    raw = z.read(item["md5ext"])
                    (OUT / folder / filename).write_bytes(raw)
                    entry = {"target": target["name"], "kind": kind, "name": item["name"],
                             "index": i, "md5ext": item["md5ext"], "data_format": ext,
                             "path": f"assets/generated/{folder}/{filename}", **defaults}
                    if kind == "costume":
                        entry.update(bitmap_resolution=item.get("bitmapResolution", 1),
                                     rotation_center_x=item.get("rotationCenterX", 0),
                                     rotation_center_y=item.get("rotationCenterY", 0),
                                     source_dimensions=png_size(raw) or svg_size(raw))
                    else:
                        entry.update(rate=item.get("rate"), sample_count=item.get("sampleCount"))
                    entries.append(entry)
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "asset_manifest.json").write_text(json.dumps({"source": str(SOURCE.relative_to(ROOT)), "assets": entries}, indent=2), encoding="utf8")
    print(f"Extracted {len(entries)} logical references to {OUT}")

if __name__ == "__main__": main()
