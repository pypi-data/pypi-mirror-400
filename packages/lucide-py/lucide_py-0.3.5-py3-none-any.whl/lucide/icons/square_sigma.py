
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareSigma(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-sigma'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M16 8.9V7H8l4 5-4 5h8v-1.9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
