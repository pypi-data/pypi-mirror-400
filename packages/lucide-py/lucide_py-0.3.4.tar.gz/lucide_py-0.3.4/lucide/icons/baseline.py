
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Baseline(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-baseline'], 'items': [{'path': {'d': 'M4 20h16'}}, {'path': {'d': 'm6 16 6-12 6 12'}}, {'path': {'d': 'M8 12h8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
