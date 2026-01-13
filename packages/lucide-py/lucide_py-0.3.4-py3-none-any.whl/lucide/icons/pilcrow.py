
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Pilcrow(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-pilcrow'], 'items': [{'path': {'d': 'M13 4v16'}}, {'path': {'d': 'M17 4v16'}}, {'path': {'d': 'M19 4H9.5a4.5 4.5 0 0 0 0 9H13'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
