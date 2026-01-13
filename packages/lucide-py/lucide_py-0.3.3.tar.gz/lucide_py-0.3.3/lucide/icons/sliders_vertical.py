
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SlidersVertical(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-sliders-vertical'], 'items': [{'path': {'d': 'M10 8h4'}}, {'path': {'d': 'M12 21v-9'}}, {'path': {'d': 'M12 8V3'}}, {'path': {'d': 'M17 16h4'}}, {'path': {'d': 'M19 12V3'}}, {'path': {'d': 'M19 21v-5'}}, {'path': {'d': 'M3 14h4'}}, {'path': {'d': 'M5 10V3'}}, {'path': {'d': 'M5 21v-7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
