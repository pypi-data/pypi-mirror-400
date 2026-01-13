
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CheckLine(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-check-line'], 'items': [{'path': {'d': 'M20 4L9 15'}}, {'path': {'d': 'M21 19L3 19'}}, {'path': {'d': 'M9 15L4 10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
