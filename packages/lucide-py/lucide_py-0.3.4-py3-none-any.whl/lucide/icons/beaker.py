
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Beaker(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-beaker'], 'items': [{'path': {'d': 'M4.5 3h15'}}, {'path': {'d': 'M6 3v16a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V3'}}, {'path': {'d': 'M6 14h12'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
