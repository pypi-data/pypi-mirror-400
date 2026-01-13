
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Parentheses(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-parentheses'], 'items': [{'path': {'d': 'M8 21s-4-3-4-9 4-9 4-9'}}, {'path': {'d': 'M16 3s4 3 4 9-4 9-4 9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
