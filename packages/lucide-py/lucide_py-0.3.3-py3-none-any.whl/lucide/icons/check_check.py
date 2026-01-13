
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CheckCheck(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-check-check'], 'items': [{'path': {'d': 'M18 6 7 17l-5-5'}}, {'path': {'d': 'm22 10-7.5 7.5L13 16'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
