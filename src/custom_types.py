from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from PIL import Image

from typing import TypedDict, List

class ImageMetadata(TypedDict):
    name: str
    md5: str
    comments: str
    tags: List[str]
    width: int
    height: int

class ImageSeries(TypedDict):
    name: str
    directory: str
    images: List[ImageMetadata]

class ImageLibrary(TypedDict):
    series: List[ImageSeries]

@dataclass
class ProcessingContext:
    name: str
    md5: str
    img: Image.Image

OldMetadata = Optional[Dict[str, Any]]
SchemaFieldGenerator = Callable[[ProcessingContext, OldMetadata], Any]
