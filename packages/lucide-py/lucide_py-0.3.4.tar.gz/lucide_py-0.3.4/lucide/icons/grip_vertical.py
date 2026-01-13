
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def GripVertical(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-grip-vertical'], 'items': [{'circle': {'cx': '9', 'cy': '12', 'r': '1'}}, {'circle': {'cx': '9', 'cy': '5', 'r': '1'}}, {'circle': {'cx': '9', 'cy': '19', 'r': '1'}}, {'circle': {'cx': '15', 'cy': '12', 'r': '1'}}, {'circle': {'cx': '15', 'cy': '5', 'r': '1'}}, {'circle': {'cx': '15', 'cy': '19', 'r': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
