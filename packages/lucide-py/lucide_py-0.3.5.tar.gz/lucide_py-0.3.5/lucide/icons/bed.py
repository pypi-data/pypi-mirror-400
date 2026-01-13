
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Bed(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-bed'], 'items': [{'path': {'d': 'M2 4v16'}}, {'path': {'d': 'M2 8h18a2 2 0 0 1 2 2v10'}}, {'path': {'d': 'M2 17h20'}}, {'path': {'d': 'M6 8v9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
