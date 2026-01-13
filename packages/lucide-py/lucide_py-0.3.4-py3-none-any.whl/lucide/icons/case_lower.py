
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CaseLower(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-case-lower'], 'items': [{'path': {'d': 'M10 9v7'}}, {'path': {'d': 'M14 6v10'}}, {'circle': {'cx': '17.5', 'cy': '12.5', 'r': '3.5'}}, {'circle': {'cx': '6.5', 'cy': '12.5', 'r': '3.5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
