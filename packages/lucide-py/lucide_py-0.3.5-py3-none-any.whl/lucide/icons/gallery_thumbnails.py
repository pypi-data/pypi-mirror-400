
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def GalleryThumbnails(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-gallery-thumbnails'], 'items': [{'rect': {'width': '18', 'height': '14', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M4 21h1'}}, {'path': {'d': 'M9 21h1'}}, {'path': {'d': 'M14 21h1'}}, {'path': {'d': 'M19 21h1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
