
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def LaptopMinimalCheck(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-laptop-minimal-check'], 'items': [{'path': {'d': 'M2 20h20'}}, {'path': {'d': 'm9 10 2 2 4-4'}}, {'rect': {'x': '3', 'y': '4', 'width': '18', 'height': '12', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
