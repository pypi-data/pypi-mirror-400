
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareDot(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-dot'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
