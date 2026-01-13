
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def DecimalsArrowLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-decimals-arrow-left'], 'items': [{'path': {'d': 'm13 21-3-3 3-3'}}, {'path': {'d': 'M20 18H10'}}, {'path': {'d': 'M3 11h.01'}}, {'rect': {'x': '6', 'y': '3', 'width': '5', 'height': '8', 'rx': '2.5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
