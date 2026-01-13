
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleArrowRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-arrow-right'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'm12 16 4-4-4-4'}}, {'path': {'d': 'M8 12h8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
