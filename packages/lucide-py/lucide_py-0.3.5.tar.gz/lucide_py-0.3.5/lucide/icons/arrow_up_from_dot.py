
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowUpFromDot(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-up-from-dot'], 'items': [{'path': {'d': 'm5 9 7-7 7 7'}}, {'path': {'d': 'M12 16V2'}}, {'circle': {'cx': '12', 'cy': '21', 'r': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
