
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def GalleryHorizontal(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-gallery-horizontal'], 'items': [{'path': {'d': 'M2 3v18'}}, {'rect': {'width': '12', 'height': '18', 'x': '6', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M22 3v18'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
