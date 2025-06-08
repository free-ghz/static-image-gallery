from jinja2 import Environment, FileSystemLoader
from gallery_lib import (
    find_latest_state_file, load_json_state, ImageLibrary, TEMPLATES_DIR
)
from typing import cast, Dict, Any

OUTPUT_HTML_FILE = "index.html"

def main() -> None:

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