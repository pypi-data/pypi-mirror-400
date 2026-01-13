
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleDivide(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-divide'], 'items': [{'line': {'x1': '8', 'x2': '16', 'y1': '12', 'y2': '12'}}, {'line': {'x1': '12', 'x2': '12', 'y1': '16', 'y2': '16'}}, {'line': {'x1': '12', 'x2': '12', 'y1': '8', 'y2': '8'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
