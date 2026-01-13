
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def AudioLines(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-audio-lines'], 'items': [{'path': {'d': 'M2 10v3'}}, {'path': {'d': 'M6 6v11'}}, {'path': {'d': 'M10 3v18'}}, {'path': {'d': 'M14 8v7'}}, {'path': {'d': 'M18 5v13'}}, {'path': {'d': 'M22 10v3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
