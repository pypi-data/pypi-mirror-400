
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def RussianRuble(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-russian-ruble'], 'items': [{'path': {'d': 'M6 11h8a4 4 0 0 0 0-8H9v18'}}, {'path': {'d': 'M6 15h8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
