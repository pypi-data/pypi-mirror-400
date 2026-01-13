
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TextWrap(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-text-wrap'], 'items': [{'path': {'d': 'm16 16-3 3 3 3'}}, {'path': {'d': 'M3 12h14.5a1 1 0 0 1 0 7H13'}}, {'path': {'d': 'M3 19h6'}}, {'path': {'d': 'M3 5h18'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
