
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MapPinPlus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-map-pin-plus'], 'items': [{'path': {'d': 'M19.914 11.105A7.298 7.298 0 0 0 20 10a8 8 0 0 0-16 0c0 4.993 5.539 10.193 7.399 11.799a1 1 0 0 0 1.202 0 32 32 0 0 0 .824-.738'}}, {'circle': {'cx': '12', 'cy': '10', 'r': '3'}}, {'path': {'d': 'M16 18h6'}}, {'path': {'d': 'M19 15v6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
