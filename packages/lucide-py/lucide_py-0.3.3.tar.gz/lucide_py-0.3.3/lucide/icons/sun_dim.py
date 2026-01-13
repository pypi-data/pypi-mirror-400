
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SunDim(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-sun-dim'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '4'}}, {'path': {'d': 'M12 4h.01'}}, {'path': {'d': 'M20 12h.01'}}, {'path': {'d': 'M12 20h.01'}}, {'path': {'d': 'M4 12h.01'}}, {'path': {'d': 'M17.657 6.343h.01'}}, {'path': {'d': 'M17.657 17.657h.01'}}, {'path': {'d': 'M6.343 17.657h.01'}}, {'path': {'d': 'M6.343 6.343h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
