
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Cylinder(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-cylinder'], 'items': [{'ellipse': {'cx': '12', 'cy': '5', 'rx': '9', 'ry': '3'}}, {'path': {'d': 'M3 5v14a9 3 0 0 0 18 0V5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
