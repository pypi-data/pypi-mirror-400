
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleSmall(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-small'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
