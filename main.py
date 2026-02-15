import json
import os
import sys
import tempfile

from pathlib import Path
from PIL import Image
from typing import Optional

MANIFEST_SIZES: tuple[int, ...] = (32, 48, 72, 128, 180, 192, 256, 384, 512)
MANIFEST_PREFIXES: tuple[str, ...] = ("icon", "maskable-icon")

CANVAS_SIZE: tuple[int, int] = (500, 500)
INNER_SIZE: tuple[int, int] = (320, 320)

RESAMPLE = Image.Resampling.LANCZOS

MANIFEST_ICON_BASE_PATH = "/assets/media/img/manifest"

def resolve_source_path(filename: str) -> Path:
    path = Path.cwd() / filename
    if not path.is_file():
        raise FileNotFoundError(
            f"'{filename}' not found in the current directory ({Path.cwd()})."
        )
    return path

def open_and_convert_img_to_rgb(path: Path) -> Image.Image:
    with Image.open(path) as img:
        return img.convert("RGBA")

def centre_on_canvas(
    img: Image.Image,
    canvas_size: tuple[int, int] = CANVAS_SIZE,
    inner_size: tuple[int, int] = INNER_SIZE,
) -> Image.Image:
    resized = img.resize(inner_size, RESAMPLE)
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    offset = (
        (canvas_size[0] - inner_size[0]) // 2,
        (canvas_size[1] - inner_size[1]) // 2,
    )
    canvas.paste(resized, offset, resized)
    return canvas

def save_png(img: Image.Image, path: Path) -> None:
    img.save(path, format="PNG", optimize=True)

def generate_manifest_icons(base: Image.Image, manifest_dir: Path) -> None:
    manifest_dir.mkdir(parents=True, exist_ok=True)

    for size in MANIFEST_SIZES:
        resized = base.resize((size, size), RESAMPLE)
        for prefix in MANIFEST_PREFIXES:
            save_png(resized, manifest_dir / f"{prefix}-{size}x{size}.png")

def generate_manifest_json(out_dir: Path, project_folder: str) -> None:
    icons = []
    for size in MANIFEST_SIZES:
        size_str = f"{size}x{size}"
        icons.append({
            "src": f"{MANIFEST_ICON_BASE_PATH}/icon-{size_str}.png",
            "sizes": size_str,
            "type": "image/png",
            "purpose": "any",
        })
        icons.append({
            "src": f"{MANIFEST_ICON_BASE_PATH}/maskable-icon-{size_str}.png",
            "sizes": size_str,
            "type": "image/png",
            "purpose": "maskable",
        })

    manifest = {
        "name": "Nom complet de l'application",
        "short_name": project_folder,
        "description": "Description de l'application.",
        "lang": "fr-FR",
        "dir": "ltr",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "orientation": "portrait-primary",
        "theme_color": "#ffffff",
        "background_color": "#ffffff",
        "icons": icons,
        "categories": [],
    }

    manifest_path = out_dir / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=4)

def generate_favicon(src: Image.Image, dest: Path) -> None:
    ico_sizes = [(32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    thumb = src.resize((32, 32), RESAMPLE)
    thumb.save(dest, format="ICO", sizes=ico_sizes)

def generate_logo(src: Image.Image, dest: Path, size: int = 192) -> None:
    save_png(src.resize((size, size), RESAMPLE), dest)

def generate_assets(
    source_path: Path,
    project_folder: str,
    center: bool = True,
) -> None:
    out = Path(project_folder)
    out.mkdir(parents=True, exist_ok=True)

    original = open_and_convert_img_to_rgb(source_path)

    if center:
        # Write the centred canvas to a temp file so it can be cleaned up automatically
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            base = centre_on_canvas(original)
            base.save(tmp_path, format="PNG")
            base = open_and_convert_img_to_rgb(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)
    else:
        base = original

    generate_manifest_icons(base, out / "manifest")
    generate_manifest_json(out, project_folder)
    generate_logo(original, out / "logo.png")
    generate_favicon(original, out / "favicon.ico")

    print(f"Icônes et manifest.json sauvegardés dans '{out}/'.")

def _parse_bool(value: str, flag: str) -> bool:
    #Parse a CLI string to ensure boolean value
    normalised = value.strip().lower()
    if normalised not in ("true", "false"):
        print(f"Error: '{flag}' must be 'true' or 'false', got '{value}'.")
        sys.exit(1)
    return normalised == "true"

def main(argv: Optional[list[str]] = None) -> None:
    args = (argv or sys.argv)[1:]

    if not (2 <= len(args) <= 3):
        print(
            "Utilisation: python main.py <nom_image> <nom_du_projet> [centrer sur le canvas]\n"
            "  - Si vous mettez 'false', l'image sera utilisée telle quelle, sans centrage ni redimensionnement."
        )
        sys.exit(1)

    filename, project_folder = args[0], args[1]
    center = _parse_bool(args[2], "center") if len(args) == 3 else True

    try:
        source_path = resolve_source_path(filename)
        generate_assets(source_path, project_folder, center=center)
    except FileNotFoundError as exc:
        print(f"File error: {exc}")
        sys.exit(1)
    except OSError as exc:
        print(f"I/O error: {exc}")
        sys.exit(1)

if __name__ == "__main__":
    main()
