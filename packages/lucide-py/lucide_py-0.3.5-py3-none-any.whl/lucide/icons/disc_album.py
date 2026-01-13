
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def DiscAlbum(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-disc-album'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '5'}}, {'path': {'d': 'M12 12h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
