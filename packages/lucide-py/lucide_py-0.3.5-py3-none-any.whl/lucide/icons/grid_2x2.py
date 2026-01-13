
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Grid2x2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-grid-2x2'], 'items': [{'path': {'d': 'M12 3v18'}}, {'path': {'d': 'M3 12h18'}}, {'rect': {'x': '3', 'y': '3', 'width': '18', 'height': '18', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
