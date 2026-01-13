
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareLibrary(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-library'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M7 7v10'}}, {'path': {'d': 'M11 7v10'}}, {'path': {'d': 'm15 7 2 10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
