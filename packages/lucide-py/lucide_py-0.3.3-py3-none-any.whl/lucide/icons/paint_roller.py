
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PaintRoller(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-paint-roller'], 'items': [{'rect': {'width': '16', 'height': '6', 'x': '2', 'y': '2', 'rx': '2'}}, {'path': {'d': 'M10 16v-2a2 2 0 0 1 2-2h8a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2'}}, {'rect': {'width': '4', 'height': '6', 'x': '8', 'y': '16', 'rx': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
