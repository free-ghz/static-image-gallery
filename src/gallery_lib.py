import os
import json
import hashlib
import datetime
import glob
from PIL import Image
from typing import Dict, Optional, Any, cast

from custom_types import (
    ImageMetadata, ImageSeries, ImageLibrary, ProcessingContext, OldMetadata
)
from schema import IMAGE_SCHEMA

WALLPAPERS_DIR = "wallpapers"
STATES_DIR = "states"
THUMBS_DIR = "thumbs"
TEMPLATES_DIR = "templates"
THUMB_SIZE = (400, 400)
SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png')
OUTPUT_DIR = "public"
OUTPUT_HTML_FILE = os.path.join(OUTPUT_DIR, "index.html")








def calculate_md5(filepath: str) -> Optional[str]:
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except IOError as e:
        print(f"error reading file {filepath}: {e}")
        return None

def ensure_dirs() -> None:
    for dir_path in [STATES_DIR, THUMBS_DIR, TEMPLATES_DIR, WALLPAPERS_DIR]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

def find_latest_state_file() -> Optional[str]:
    list_of_files = glob.glob(os.path.join(STATES_DIR, '*.json'))
    if not list_of_files:
        return None
    return max(list_of_files, key=os.path.getctime)

def load_json_state(filepath: Optional[str]) -> Dict[str, Any]:
    if not filepath or not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"error parsing file {filepath}: {e}")
        return {}

def save_state(state_data: ImageLibrary) -> Optional[str]:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}.json"
    filepath = os.path.join(STATES_DIR, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=2, ensure_ascii=False)
        return filepath
    except IOError as e:
        print(f"error writing state file {filepath}: {e}")
        return None








def discover_images() -> ImageLibrary:
    """
    scans the wallpapers directory and returns a fully structured (eh) ImageLibrary containing basic information about found images.
    """
    new_library: ImageLibrary = {"series": []}
    
    if not os.path.isdir(WALLPAPERS_DIR):
        print(f"warning: '{WALLPAPERS_DIR}' directory not found, which is weird. try again?")
        return new_library

    for series_name in os.listdir(WALLPAPERS_DIR):
        series_path = os.path.join(WALLPAPERS_DIR, series_name)
        if os.path.isdir(series_path):
            image_series: ImageSeries = {
                "name": series_name,
                "directory": series_path,
                "images": []
            }

            found_images = []
            for filename in os.listdir(series_path):
                if filename.lower().endswith(SUPPORTED_EXTENSIONS):
                    filepath = os.path.join(series_path, filename)
                    md5 = calculate_md5(filepath)
                    if md5:
                        found_images.append({"name": filename, "md5": md5})

            image_series['images'] = found_images # type: ignore
            new_library["series"].append(image_series)
            
    return new_library

def create_thumbnail(image_path: str, md5: str, force: bool = False) -> None:
    thumb_path = os.path.join(THUMBS_DIR, f"{md5}.jpg")
    if not force and os.path.exists(thumb_path):
        return

    try:
        with Image.open(image_path) as img:
            img.thumbnail(THUMB_SIZE)
            img = img.convert('RGB')
            img.save(thumb_path, "JPEG", quality=85)
    except Exception as e:
        print(f"error writing thumbnail file {image_path}: {e}")

def merge_states(current_scan: ImageLibrary, previous_state: Dict[str, Any]) -> ImageLibrary:
    """
    merges the discovered new state with the last know state from disk.

    the schema might have changed sice; we can't trust what's loaded to be entirely up to code.
    this is where functions from `schema.py` get applied.
    """
    previous_images_by_md5: Dict[str, Dict[str, Any]] = {}

    # .get() to avoid problems if the old state file is no longer fine
    for series in previous_state.get("series", []):
        if isinstance(series, dict):
            for img_data in series.get("images", []):
                if isinstance(img_data, dict) and "md5" in img_data:
                    previous_images_by_md5[img_data["md5"]] = img_data

    final_library: ImageLibrary = {"series": []}
    new_image_count = 0

    for current_series_scan in current_scan["series"]:
        final_series: ImageSeries = {
            "name": current_series_scan["name"],
            "directory": current_series_scan["directory"],
            "images": []
        }

        for scanned_image in current_series_scan["images"]:
            md5 = scanned_image["md5"]
            old_image_data: OldMetadata = previous_images_by_md5.get(md5)
            image_path = os.path.join(current_series_scan["directory"], scanned_image["name"])

            try:
                with Image.open(image_path) as img:
                    context = ProcessingContext(
                        name=scanned_image["name"],
                        md5=md5,
                        img=img
                    )

                    new_metadata_dict = {
                        field: generator_func(context, old_image_data)
                        for field, generator_func in IMAGE_SCHEMA.items()
                    }

                    final_image_metadata = cast(ImageMetadata, new_metadata_dict)
                    final_series["images"].append(final_image_metadata)

                    if not old_image_data:
                        new_image_count += 1
                        print(f"+ Found new image: {final_series['name']}/{context.name}")
                        create_thumbnail(image_path, md5)

            except Exception as e:
                print(f"error processing image {image_path}: {e}")

        final_library["series"].append(final_series)

    return final_library