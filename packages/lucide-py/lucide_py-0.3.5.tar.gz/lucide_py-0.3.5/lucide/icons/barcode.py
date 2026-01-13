
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Barcode(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-barcode'], 'items': [{'path': {'d': 'M3 5v14'}}, {'path': {'d': 'M8 5v14'}}, {'path': {'d': 'M12 5v14'}}, {'path': {'d': 'M17 5v14'}}, {'path': {'d': 'M21 5v14'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
