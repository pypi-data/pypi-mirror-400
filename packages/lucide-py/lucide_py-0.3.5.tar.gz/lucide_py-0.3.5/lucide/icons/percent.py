
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Percent(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-percent'], 'items': [{'line': {'x1': '19', 'x2': '5', 'y1': '5', 'y2': '19'}}, {'circle': {'cx': '6.5', 'cy': '6.5', 'r': '2.5'}}, {'circle': {'cx': '17.5', 'cy': '17.5', 'r': '2.5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
