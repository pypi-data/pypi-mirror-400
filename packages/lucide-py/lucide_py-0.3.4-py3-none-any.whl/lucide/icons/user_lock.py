
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def UserLock(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-user-lock'], 'items': [{'circle': {'cx': '10', 'cy': '7', 'r': '4'}}, {'path': {'d': 'M10.3 15H7a4 4 0 0 0-4 4v2'}}, {'path': {'d': 'M15 15.5V14a2 2 0 0 1 4 0v1.5'}}, {'rect': {'width': '8', 'height': '5', 'x': '13', 'y': '16', 'rx': '.899'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
