
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CirclePercent(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-percent'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'm15 9-6 6'}}, {'path': {'d': 'M9 9h.01'}}, {'path': {'d': 'M15 15h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
