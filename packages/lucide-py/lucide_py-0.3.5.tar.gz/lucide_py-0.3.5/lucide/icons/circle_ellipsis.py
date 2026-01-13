
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleEllipsis(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-ellipsis'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'M17 12h.01'}}, {'path': {'d': 'M12 12h.01'}}, {'path': {'d': 'M7 12h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
