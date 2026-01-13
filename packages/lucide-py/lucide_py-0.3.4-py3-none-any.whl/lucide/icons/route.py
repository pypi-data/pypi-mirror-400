
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Route(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-route'], 'items': [{'circle': {'cx': '6', 'cy': '19', 'r': '3'}}, {'path': {'d': 'M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15'}}, {'circle': {'cx': '18', 'cy': '5', 'r': '3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
