
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Birdhouse(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-birdhouse'], 'items': [{'path': {'d': 'M12 18v4'}}, {'path': {'d': 'm17 18 1.956-11.468'}}, {'path': {'d': 'm3 8 7.82-5.615a2 2 0 0 1 2.36 0L21 8'}}, {'path': {'d': 'M4 18h16'}}, {'path': {'d': 'M7 18 5.044 6.532'}}, {'circle': {'cx': '12', 'cy': '10', 'r': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
