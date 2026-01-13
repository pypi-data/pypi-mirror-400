
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Blinds(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-blinds'], 'items': [{'path': {'d': 'M3 3h18'}}, {'path': {'d': 'M20 7H8'}}, {'path': {'d': 'M20 11H8'}}, {'path': {'d': 'M10 19h10'}}, {'path': {'d': 'M8 15h12'}}, {'path': {'d': 'M4 3v14'}}, {'circle': {'cx': '4', 'cy': '19', 'r': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
