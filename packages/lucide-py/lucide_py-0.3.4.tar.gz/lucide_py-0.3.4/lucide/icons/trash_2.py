
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Trash2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-trash-2'], 'items': [{'path': {'d': 'M10 11v6'}}, {'path': {'d': 'M14 11v6'}}, {'path': {'d': 'M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6'}}, {'path': {'d': 'M3 6h18'}}, {'path': {'d': 'M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
