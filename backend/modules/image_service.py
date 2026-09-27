"""
Image Viewer Subsystem Service
High-performance visual asset inspector and catalog manager.
Integrates Pillow (PIL) for image decoding, EXIF metadata inspection,
color depth profiling, and procedural graphic generation.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from PIL import Image, ImageDraw
from ..database_manager import db_manager

logger = logging.getLogger("ImageService")


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

                    # Draw grid
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
        """List all cataloged images."""
        self._sync_catalog()
        return db_manager.execute_query(self.DB, "SELECT * FROM image_catalog ORDER BY is_favorite DESC, added_at DESC")

    def get_image(self, image_id: int) -> Optional[Dict[str, Any]]:
        """Fetch details for an image."""
        rows = db_manager.execute_query(self.DB, "SELECT * FROM image_catalog WHERE id = ?", (image_id,))
        return rows[0] if rows else None

    def toggle_favorite(self, image_id: int) -> Optional[Dict[str, Any]]:
        """Toggle favorite flag."""
        img = self.get_image(image_id)
        if not img:
            return None
        new_fav = 0 if img["is_favorite"] else 1
        db_manager.execute_non_query(self.DB, "UPDATE image_catalog SET is_favorite = ? WHERE id = ?", (new_fav, image_id))
        return self.get_image(image_id)

    def scan_directory(self, folder_path: str) -> int:
        """Import images from any chosen local directory."""
        if not os.path.exists(folder_path):
            return 0
        supported_exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
        added = 0
        for root, _, files in os.walk(folder_path):
            for f in files:
                if os.path.splitext(f)[1].lower() in supported_exts:
                    full_path = os.path.join(root, f)
                    exists = db_manager.execute_query(self.DB, "SELECT id FROM image_catalog WHERE file_path = ?", (full_path,))
                    if not exists:
                        try:
                            with Image.open(full_path) as im:
                                w, h = im.size
                                fmt = im.format or "IMG"
                                mode = im.mode
                                fsize = os.path.getsize(full_path)
                                db_manager.execute_non_query(
                                    self.DB,
                                    """INSERT INTO image_catalog (file_name, file_path, file_size, width, height, color_space, format)
                                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                    (f, full_path, fsize, w, h, mode, fmt)
                                )
                                added += 1
                        except Exception:
                            pass
        return added


image_service = ImageService()
