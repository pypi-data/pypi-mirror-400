
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Heading6(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-heading-6'], 'items': [{'path': {'d': 'M4 12h8'}}, {'path': {'d': 'M4 18V6'}}, {'path': {'d': 'M12 18V6'}}, {'circle': {'cx': '19', 'cy': '16', 'r': '2'}}, {'path': {'d': 'M20 10c-2 2-3 3.5-3 6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
