
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Torus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-torus'], 'items': [{'ellipse': {'cx': '12', 'cy': '11', 'rx': '3', 'ry': '2'}}, {'ellipse': {'cx': '12', 'cy': '12.5', 'rx': '10', 'ry': '8.5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
