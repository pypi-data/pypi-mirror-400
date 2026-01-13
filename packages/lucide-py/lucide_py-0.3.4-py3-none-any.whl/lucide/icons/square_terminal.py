
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareTerminal(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-terminal'], 'items': [{'path': {'d': 'm7 11 2-2-2-2'}}, {'path': {'d': 'M11 13h4'}}, {'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2', 'ry': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
