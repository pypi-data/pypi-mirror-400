
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareCheckBig(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-check-big'], 'items': [{'path': {'d': 'M21 10.656V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h12.344'}}, {'path': {'d': 'm9 11 3 3L22 4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
