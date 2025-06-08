import os
import shutil
from jinja2 import Environment, FileSystemLoader
from gallery_lib import (
    find_latest_state_file, load_json_state, ImageLibrary,
    TEMPLATES_DIR, WALLPAPERS_DIR, THUMBS_DIR, OUTPUT_DIR, OUTPUT_HTML_FILE
)
from typing import cast, Dict, Any 


def sync_directory(src_dir: str, dst_dir: str) -> None:
    os.makedirs(dst_dir, exist_ok=True)
    for src_root, _, files in os.walk(src_dir):
        dst_root = os.path.join(dst_dir, os.path.relpath(src_root, src_dir))
        os.makedirs(dst_root, exist_ok=True)

        for file in files:
            src_path = os.path.join(src_root, file)
            dst_path = os.path.join(dst_root, file)

            if os.path.exists(dst_path) and os.path.getmtime(src_path) <= os.path.getmtime(dst_path):
                continue

            shutil.copy2(src_path, dst_path)


def sync_template_assets() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for item in os.listdir(TEMPLATES_DIR):
        if item.endswith('.html'):
            continue

        src_path = os.path.join(TEMPLATES_DIR, item)
        dst_path = os.path.join(OUTPUT_DIR, item)

        if os.path.isfile(src_path):
            shutil.copy2(src_path, dst_path)
        elif os.path.isdir(src_path):
            sync_directory(src_path, dst_path)


def main() -> None:
    sync_directory(WALLPAPERS_DIR, os.path.join(OUTPUT_DIR, WALLPAPERS_DIR))
    sync_directory(THUMBS_DIR, os.path.join(OUTPUT_DIR, THUMBS_DIR))
    sync_template_assets()

    latest_state_path = find_latest_state_file()
    if not latest_state_path:
        print("no state files found. Run the update script first.")
        return
    untyped_state: Dict[str, Any] = load_json_state(latest_state_path)

    # TODO we are too confident the *latest* state file is valid. we should type check it and exit like above. before casting
    state_data = cast(ImageLibrary, untyped_state)

    gallery_data_for_template = state_data["series"]

    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)
    template = env.get_template("index.html")

    html_output = template.render(gallery_data=gallery_data_for_template)

    with open(OUTPUT_HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html_output)

    print(f"generated '{OUTPUT_HTML_FILE}'!")

if __name__ == "__main__":
    main()
