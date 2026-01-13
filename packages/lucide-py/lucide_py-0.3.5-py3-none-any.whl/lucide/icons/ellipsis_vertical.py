
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def EllipsisVertical(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-ellipsis-vertical'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '1'}}, {'circle': {'cx': '12', 'cy': '5', 'r': '1'}}, {'circle': {'cx': '12', 'cy': '19', 'r': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
