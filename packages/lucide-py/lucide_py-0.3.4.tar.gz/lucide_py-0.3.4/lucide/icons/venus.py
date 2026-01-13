
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Venus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-venus'], 'items': [{'path': {'d': 'M12 15v7'}}, {'path': {'d': 'M9 19h6'}}, {'circle': {'cx': '12', 'cy': '9', 'r': '6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
