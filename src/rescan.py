from typing import Dict, Any
from gallery_lib import (
    ensure_dirs, discover_images, find_latest_state_file, load_json_state,
    merge_states, save_state, create_thumbnail, WALLPAPERS_DIR, ImageLibrary
)
import os

def main() -> None:
    ensure_dirs()

    current_scan: ImageLibrary = discover_images()

    for series in current_scan["series"]:
        series_name = series["name"]
        for image in series["images"]:
            image_path = os.path.join(WALLPAPERS_DIR, series_name, image["name"])
            create_thumbnail(image_path, image["md5"], force=True)

    latest_state_file = find_latest_state_file()
    previous_state: Dict[str, Any] = load_json_state(latest_state_file)

    merged_state: ImageLibrary = merge_states(current_scan, previous_state)
    save_state(merged_state)

if __name__ == "__main__":
    main()