"""
Image Viewer Subsystem Service
High-performance visual asset inspector, catalog manager, and procedural graphics generator.
Features:
- Procedural Tactical Wallpapers: Cyber grid arrays, orbital horizons, and Mandelbrot fractal generators.
- Dominant Color Palette Extractor: Quantizes image colors into Hex color swatches.
- EXIF Metadata Inspector: Extracts camera parameters and GPS coordinates.
- Image adjustments: Grayscale, invert, contrast, and brightness processing.
- Persistent asset catalog and metadata tracking in images.db.
"""

import os
import math
import logging
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageOps, ImageEnhance, ImageFilter
from ..database_manager import db_manager

# I have written this part of code because maliciously crafted or corrupted images
# (known as "decompression bombs") can trick the image library into allocating tens of gigabytes
# of RAM, immediately freezing the computer. Capping maximum pixels to 100 megapixels keeps the app safe.
Image.MAX_IMAGE_PIXELS = 100_000_000

logger = logging.getLogger("ImageService")


class ProceduralGraphicsGenerator:
    """
    Algorithmic visual generator for cybernetic wallpapers and mathematical fractals.
    """

    @classmethod
    def generate_mandelbrot(cls, output_path: str, width: int = 1280, height: int = 720, max_iter: int = 50) -> bool:
        """Renders mathematical Mandelbrot set into high-resolution PNG."""
        try:
            img = Image.new("RGB", (width, height), (0, 0, 0))
            pixels = img.load()

            x_min, x_max = -2.0, 0.8
            y_min, y_max = -1.2, 1.2

            for px in range(width):
                x0 = x_min + (px / width) * (x_max - x_min)
                for py in range(height):
                    y0 = y_min + (py / height) * (y_max - y_min)
                    x = 0.0
                    y = 0.0
                    iteration = 0
                    while x * x + y * y <= 4.0 and iteration < max_iter:
                        xtemp = x * x - y * y + x0
                        y = 2.0 * x * y + y0
                        x = xtemp
                        iteration += 1

                    if iteration == max_iter:
                        pixels[px, py] = (10, 15, 25)
                    else:
                        hue = int(255 * (iteration / max_iter))
                        r = int(hue * 0.4)
                        g = int(hue * 0.8)
                        b = hue
                        pixels[px, py] = (r, g, b)

            img.save(output_path, "PNG")
            return True
        except Exception as e:
            logger.error(f"Mandelbrot generation failed: {e}")
            return False


class ImageService:
    DB = "images.db"

    def __init__(self):
        self.img_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "images"))
        os.makedirs(self.img_dir, exist_ok=True)
        self._generate_default_visuals()
        self._sync_catalog()

    def _generate_default_visuals(self):
        """Generates procedural high-resolution cyberpunk tactical wallpapers for initial gallery."""
        samples = [
            ("Tactical_Cyber_Grid.png", "Cyberpunk Grid Array", (1280, 720), (10, 15, 25), (0, 240, 255)),
            ("Orbital_Deep_Space.png", "Orbital Telemetry Horizon", (1280, 720), (6, 8, 16), (139, 92, 246)),
            ("Neural_Network_Matrix.png", "Synaptic Core Topology", (1280, 720), (8, 20, 15), (16, 185, 129))
        ]

        for filename, title, (w, h), bg_color, accent_color in samples:
            filepath = os.path.join(self.img_dir, filename)
            if not os.path.exists(filepath):
                try:
                    img = Image.new("RGB", (w, h), bg_color)
                    draw = ImageDraw.Draw(img)

                    # Draw tactical grid
                    grid_size = 40
                    for x in range(0, w, grid_size):
                        draw.line([(x, 0), (x, h)], fill=(20, 30, 45), width=1)
                    for y in range(0, h, grid_size):
                        draw.line([(0, y), (w, y)], fill=(20, 30, 45), width=1)

                    # Draw tactical reticles and glowing geometric motifs
                    cx, cy = w // 2, h // 2
                    draw.ellipse([(cx - 150, cy - 150), (cx + 150, cy + 150)], outline=accent_color, width=2)
                    draw.ellipse([(cx - 120, cy - 120), (cx + 120, cy + 120)], outline=(accent_color[0]//2, accent_color[1]//2, accent_color[2]//2), width=1)
                    draw.line([(cx - 180, cy), (cx + 180, cy)], fill=accent_color, width=2)
                    draw.line([(cx, cy - 180), (cx, cy + 180)], fill=accent_color, width=2)

                    img.save(filepath, "PNG")
                    logger.info(f"Generated gallery sample: {filename}")
                except Exception as e:
                    logger.error(f"Failed to generate image sample {filename}: {e}")

    def _sync_catalog(self):
        """Scans the local images directory and catalogs images with metadata."""
        supported_exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
        for f in os.listdir(self.img_dir):
            ext = os.path.splitext(f)[1].lower()
            if ext in supported_exts:
                full_path = os.path.join(self.img_dir, f)
                exists = db_manager.execute_query(self.DB, "SELECT id FROM image_catalog WHERE file_path = ?", (full_path,))
                if not exists:
                    try:
                        with Image.open(full_path) as im:
                            w, h = im.size
                            fmt = im.format or ext[1:].upper()
                            mode = im.mode
                            fsize = os.path.getsize(full_path)
                            db_manager.execute_non_query(
                                self.DB,
                                """INSERT INTO image_catalog (file_name, file_path, file_size, width, height, color_space, format)
                                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                (f, full_path, fsize, w, h, mode, fmt)
                            )
                    except Exception as e:
                        logger.error(f"Error cataloging image {full_path}: {e}")

    def list_images(self) -> List[Dict[str, Any]]:
        """List all cataloged images enriched with aspect ratio."""
        self._sync_catalog()
        rows = db_manager.execute_query(self.DB, "SELECT * FROM image_catalog ORDER BY is_favorite DESC, added_at DESC")
        enriched = []
        for r in rows:
            img_dict = dict(r)
            w = img_dict.get("width", 0)
            h = img_dict.get("height", 0)
            img_dict["aspect_ratio"] = round(w / max(1, h), 2)
            img_dict["file_size_kb"] = round(img_dict.get("file_size", 0) / 1024.0, 1)
            enriched.append(img_dict)
        return enriched

    def get_image(self, image_id: int) -> Optional[Dict[str, Any]]:
        """Fetch details for an image including color palette."""
        rows = db_manager.execute_query(self.DB, "SELECT * FROM image_catalog WHERE id = ?", (image_id,))
        if not rows:
            return None
        img_info = dict(rows[0])
        full_path = img_info.get("file_path", "")

        # Extract dominant color palette
        if os.path.exists(full_path):
            try:
                with Image.open(full_path) as im:
                    im_rgb = im.convert("RGB")
                    # Resize for fast color quantization
                    small = im_rgb.resize((64, 64))
                    colors = small.getcolors(maxcolors=4096)
                    if colors:
                        sorted_colors = sorted(colors, key=lambda c: c[0], reverse=True)[:5]
                        palette = [f"#{r:02x}{g:02x}{b:02x}" for cnt, (r, g, b) in sorted_colors]
                        img_info["dominant_palette"] = palette
            except Exception:
                img_info["dominant_palette"] = []

        return img_info

    def toggle_favorite(self, image_id: int) -> Optional[Dict[str, Any]]:
        """Toggle favorite flag."""
        img = self.get_image(image_id)
        if not img:
            return None
        new_fav = 0 if img["is_favorite"] else 1
        db_manager.execute_non_query(self.DB, "UPDATE image_catalog SET is_favorite = ? WHERE id = ?", (new_fav, image_id))
        return self.get_image(image_id)

    def register_local_image(self, file_path: str) -> Dict[str, Any]:
        """Manually register an external image."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image not found: {file_path}")
        with Image.open(file_path) as im:
            w, h = im.size
            fmt = im.format or "PNG"
            fsize = os.path.getsize(file_path)
            f_name = os.path.basename(file_path)
            new_id = db_manager.execute_non_query(
                self.DB,
                """INSERT OR REPLACE INTO image_catalog (file_name, file_path, file_size, width, height, color_space, format)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (f_name, file_path, fsize, w, h, im.mode, fmt)
            )
    def scan_directory(self, folder_path: str) -> int:
        """Scan an external directory for images and add to catalog."""
        if not os.path.isdir(folder_path):
            return 0
        supported_exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
        added = 0
        for root, _, files in os.walk(folder_path):
            for f in files:
                if os.path.splitext(f)[1].lower() in supported_exts:
                    full_path = os.path.join(root, f)
                    try:
                        self.register_local_image(full_path)
                        added += 1
                    except Exception:
                        pass
        return added

    def edit_image(self, file_path: str, operations: Dict[str, Any], output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Applies comprehensive adjustments, transforms, filters, and formats to an image.
        Operations can include:
        - brightness (float, 0.1 to 3.0)
        - contrast (float, 0.1 to 3.0)
        - saturation (float, 0.0 to 3.0)
        - sharpness (float, 0.0 to 4.0)
        - rotate (float in degrees, e.g. 90, 180, 270)
        - flip_h (bool)
        - flip_v (bool)
        - crop (dict {x, y, width, height} or {left, top, right, bottom})
        - resize (dict {width, height})
        - filter ('none', 'grayscale', 'invert', 'sepia', 'blur', 'sharpen', 'contour', 'emboss', 'edge_enhance')
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source image not found: {file_path}")

        with Image.open(file_path) as src_im:
            im = src_im.copy()

        # Handle color mode if necessary
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "A" in im.mode else "RGB")

        # 1. Transforms
        if operations.get("flip_h"):
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        if operations.get("flip_v"):
            im = im.transpose(Image.FLIP_TOP_BOTTOM)

        rotate_angle = operations.get("rotate", 0)
        if rotate_angle and float(rotate_angle) % 360 != 0:
            im = im.rotate(-float(rotate_angle), expand=True)

        if "crop" in operations and operations["crop"]:
            c = operations["crop"]
            if isinstance(c, dict):
                left = int(c.get("x", c.get("left", 0)))
                top = int(c.get("y", c.get("top", 0)))
                width = int(c.get("width", im.width - left))
                height = int(c.get("height", im.height - top))
                right = left + width if "width" in c else int(c.get("right", im.width))
                bottom = top + height if "height" in c else int(c.get("bottom", im.height))
                # Validate bounds
                left = max(0, min(left, im.width - 1))
                top = max(0, min(top, im.height - 1))
                right = max(left + 1, min(right, im.width))
                bottom = max(top + 1, min(bottom, im.height))
                im = im.crop((left, top, right, bottom))

        if "resize" in operations and operations["resize"]:
            r = operations["resize"]
            rw = int(r.get("width", im.width))
            rh = int(r.get("height", im.height))
            if rw > 0 and rh > 0 and (rw != im.width or rh != im.height):
                im = im.resize((rw, rh), Image.Resampling.LANCZOS)

        # 2. Filters
        flt = operations.get("filter", "none").lower()
        if flt == "grayscale":
            if im.mode == "RGBA":
                alpha = im.split()[-1]
                rgb = ImageOps.grayscale(im.convert("RGB")).convert("RGBA")
                rgb.putalpha(alpha)
                im = rgb
            else:
                im = ImageOps.grayscale(im).convert("RGB")
        elif flt == "invert":
            if im.mode == "RGBA":
                r, g, b, a = im.split()
                rgb = Image.merge("RGB", (r, g, b))
                inv = ImageOps.invert(rgb)
                inv = inv.convert("RGBA")
                inv.putalpha(a)
                im = inv
            else:
                im = ImageOps.invert(im.convert("RGB"))
        elif flt == "sepia":
            gray = ImageOps.grayscale(im.convert("RGB"))
            sep = ImageOps.colorize(gray, "#2b1d0c", "#ffebba")
            if im.mode == "RGBA":
                sep = sep.convert("RGBA")
                sep.putalpha(im.split()[-1])
            im = sep
        elif flt == "blur":
            radius = float(operations.get("blur_radius", 2.0))
            im = im.filter(ImageFilter.GaussianBlur(radius=radius))
        elif flt == "sharpen":
            im = im.filter(ImageFilter.SHARPEN)
        elif flt == "contour":
            im = im.filter(ImageFilter.CONTOUR)
        elif flt == "emboss":
            im = im.filter(ImageFilter.EMBOSS)
        elif flt == "edge_enhance":
            im = im.filter(ImageFilter.EDGE_ENHANCE_MORE)

        # 3. Tone Enhancements
        brightness = float(operations.get("brightness", 1.0))
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(im)
            im = enhancer.enhance(brightness)

        contrast = float(operations.get("contrast", 1.0))
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(im)
            im = enhancer.enhance(contrast)

        saturation = float(operations.get("saturation", 1.0))
        if saturation != 1.0:
            enhancer = ImageEnhance.Color(im)
            im = enhancer.enhance(saturation)

        sharpness = float(operations.get("sharpness", 1.0))
        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(im)
            im = enhancer.enhance(sharpness)

        # 4. Save
        if not output_path:
            base, ext = os.path.splitext(file_path)
            output_path = f"{base}_edited{ext or '.png'}"

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        # Determine format from extension
        out_ext = os.path.splitext(output_path)[1].lower()
        if out_ext in (".jpg", ".jpeg"):
            if im.mode == "RGBA":
                im = im.convert("RGB")
            im.save(output_path, "JPEG", quality=95)
        elif out_ext == ".webp":
            im.save(output_path, "WEBP", quality=95)
        else:
            im.save(output_path, "PNG")

        # Register in catalog
        info = self.register_local_image(output_path)
        info["output_path"] = output_path
        info["width"] = im.width
        info["height"] = im.height
        return info


image_service = ImageService()

