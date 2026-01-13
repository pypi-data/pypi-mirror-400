
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def VenusAndMars(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-venus-and-mars'], 'items': [{'path': {'d': 'M10 20h4'}}, {'path': {'d': 'M12 16v6'}}, {'path': {'d': 'M17 2h4v4'}}, {'path': {'d': 'm21 2-5.46 5.46'}}, {'circle': {'cx': '12', 'cy': '11', 'r': '5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
