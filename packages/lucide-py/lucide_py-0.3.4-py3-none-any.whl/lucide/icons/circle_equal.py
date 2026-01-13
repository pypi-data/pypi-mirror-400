
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleEqual(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-equal'], 'items': [{'path': {'d': 'M7 10h10'}}, {'path': {'d': 'M7 14h10'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
