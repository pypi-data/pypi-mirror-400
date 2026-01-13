
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Presentation(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-presentation'], 'items': [{'path': {'d': 'M2 3h20'}}, {'path': {'d': 'M21 3v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V3'}}, {'path': {'d': 'm7 21 5-5 5 5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
