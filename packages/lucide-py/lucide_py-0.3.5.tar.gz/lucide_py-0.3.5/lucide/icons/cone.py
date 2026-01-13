
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Cone(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-cone'], 'items': [{'path': {'d': 'm20.9 18.55-8-15.98a1 1 0 0 0-1.8 0l-8 15.98'}}, {'ellipse': {'cx': '12', 'cy': '19', 'rx': '9', 'ry': '3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
