
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TextAlignJustify(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-text-align-justify'], 'items': [{'path': {'d': 'M3 5h18'}}, {'path': {'d': 'M3 12h18'}}, {'path': {'d': 'M3 19h18'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
