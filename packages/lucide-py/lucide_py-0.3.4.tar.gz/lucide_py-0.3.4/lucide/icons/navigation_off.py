
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def NavigationOff(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-navigation-off'], 'items': [{'path': {'d': 'M8.43 8.43 3 11l8 2 2 8 2.57-5.43'}}, {'path': {'d': 'M17.39 11.73 22 2l-9.73 4.61'}}, {'line': {'x1': '2', 'x2': '22', 'y1': '2', 'y2': '22'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
