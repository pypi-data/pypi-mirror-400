
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def GalleryVerticalEnd(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-gallery-vertical-end'], 'items': [{'path': {'d': 'M7 2h10'}}, {'path': {'d': 'M5 6h14'}}, {'rect': {'width': '18', 'height': '12', 'x': '3', 'y': '10', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
