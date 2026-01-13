
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleArrowUp(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-arrow-up'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'm16 12-4-4-4 4'}}, {'path': {'d': 'M12 16V8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
