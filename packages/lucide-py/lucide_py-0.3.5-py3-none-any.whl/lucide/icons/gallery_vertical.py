
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def GalleryVertical(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-gallery-vertical'], 'items': [{'path': {'d': 'M3 2h18'}}, {'rect': {'width': '18', 'height': '12', 'x': '3', 'y': '6', 'rx': '2'}}, {'path': {'d': 'M3 22h18'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
