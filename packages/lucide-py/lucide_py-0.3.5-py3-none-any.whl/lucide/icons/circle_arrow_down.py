
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleArrowDown(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-arrow-down'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'M12 8v8'}}, {'path': {'d': 'm8 12 4 4 4-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
