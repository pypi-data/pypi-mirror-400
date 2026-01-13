
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def GalleryHorizontalEnd(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-gallery-horizontal-end'], 'items': [{'path': {'d': 'M2 7v10'}}, {'path': {'d': 'M6 5v14'}}, {'rect': {'width': '12', 'height': '18', 'x': '10', 'y': '3', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
