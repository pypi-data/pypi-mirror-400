
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def LockKeyholeOpen(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-lock-keyhole-open'], 'items': [{'circle': {'cx': '12', 'cy': '16', 'r': '1'}}, {'rect': {'width': '18', 'height': '12', 'x': '3', 'y': '10', 'rx': '2'}}, {'path': {'d': 'M7 10V7a5 5 0 0 1 9.33-2.5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
