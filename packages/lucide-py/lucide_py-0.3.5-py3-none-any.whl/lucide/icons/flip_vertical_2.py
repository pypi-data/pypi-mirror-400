
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def FlipVertical2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-flip-vertical-2'], 'items': [{'path': {'d': 'm17 3-5 5-5-5h10'}}, {'path': {'d': 'm17 21-5-5-5 5h10'}}, {'path': {'d': 'M4 12H2'}}, {'path': {'d': 'M10 12H8'}}, {'path': {'d': 'M16 12h-2'}}, {'path': {'d': 'M22 12h-2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
