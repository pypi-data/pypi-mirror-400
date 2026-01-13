
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SlidersHorizontal(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-sliders-horizontal'], 'items': [{'path': {'d': 'M10 5H3'}}, {'path': {'d': 'M12 19H3'}}, {'path': {'d': 'M14 3v4'}}, {'path': {'d': 'M16 17v4'}}, {'path': {'d': 'M21 12h-9'}}, {'path': {'d': 'M21 19h-5'}}, {'path': {'d': 'M21 5h-7'}}, {'path': {'d': 'M8 10v4'}}, {'path': {'d': 'M8 12H3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
