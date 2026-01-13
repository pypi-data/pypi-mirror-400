
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def UndoDot(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-undo-dot'], 'items': [{'path': {'d': 'M21 17a9 9 0 0 0-15-6.7L3 13'}}, {'path': {'d': 'M3 7v6h6'}}, {'circle': {'cx': '12', 'cy': '17', 'r': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
