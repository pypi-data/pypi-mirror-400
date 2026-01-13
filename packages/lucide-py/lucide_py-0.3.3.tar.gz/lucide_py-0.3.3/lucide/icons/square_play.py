
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquarePlay(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-play'], 'items': [{'rect': {'x': '3', 'y': '3', 'width': '18', 'height': '18', 'rx': '2'}}, {'path': {'d': 'M9 9.003a1 1 0 0 1 1.517-.859l4.997 2.997a1 1 0 0 1 0 1.718l-4.997 2.997A1 1 0 0 1 9 14.996z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
