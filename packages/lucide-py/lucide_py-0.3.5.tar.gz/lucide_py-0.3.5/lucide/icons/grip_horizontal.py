
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def GripHorizontal(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-grip-horizontal'], 'items': [{'circle': {'cx': '12', 'cy': '9', 'r': '1'}}, {'circle': {'cx': '19', 'cy': '9', 'r': '1'}}, {'circle': {'cx': '5', 'cy': '9', 'r': '1'}}, {'circle': {'cx': '12', 'cy': '15', 'r': '1'}}, {'circle': {'cx': '19', 'cy': '15', 'r': '1'}}, {'circle': {'cx': '5', 'cy': '15', 'r': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
