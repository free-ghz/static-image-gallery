from typing import Dict
from custom_types import (
    SchemaFieldGenerator
)

# here you can add generator lambdas for new metadata types.
#
# each key should be a function that takes (context, old_metadata) and returns some stuff of your choosing.
# remember to update the `ImageMetadata` type in custom_types.py
#
# context holds some properties gathered from the disk scan, such as the raw image. See the `ProcessingContext` type.
#
# old_metadata is the metadata entry from the previous state, or None if new. you can use this to set your own custom rules for overwriting with new values on a scan.
IMAGE_SCHEMA: Dict[str, SchemaFieldGenerator] = {
    "name": lambda context, old_metadata: context.name,
    "md5": lambda context, old_metadata: context.md5, # always take the fresh MD5 from the disk scan
    "comments": lambda context, old_metadata: old_metadata.get("comments", "") if old_metadata else "", # keep the old value if it exists, otherwise default to empty string
    "tags": lambda context, old_metadata: old_metadata.get("tags", []) if old_metadata else [],

    "width": lambda context, old_metadata: context.img.width,
    "height": lambda context, old_metadata: context.img.height,
    "filesize": lambda context, old_metadata: format_bytes(context.filesize),
}


def format_bytes(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"
