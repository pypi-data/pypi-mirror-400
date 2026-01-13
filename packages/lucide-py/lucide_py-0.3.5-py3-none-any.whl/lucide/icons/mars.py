
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Mars(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-mars'], 'items': [{'path': {'d': 'M16 3h5v5'}}, {'path': {'d': 'm21 3-6.75 6.75'}}, {'circle': {'cx': '10', 'cy': '14', 'r': '6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
