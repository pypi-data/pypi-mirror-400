
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Airplay(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-airplay'], 'items': [{'path': {'d': 'M5 17H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-1'}}, {'path': {'d': 'm12 15 5 6H7Z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
