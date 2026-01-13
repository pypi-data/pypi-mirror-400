
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def GlassWater(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-glass-water'], 'items': [{'path': {'d': 'M5.116 4.104A1 1 0 0 1 6.11 3h11.78a1 1 0 0 1 .994 1.105L17.19 20.21A2 2 0 0 1 15.2 22H8.8a2 2 0 0 1-2-1.79z'}}, {'path': {'d': 'M6 12a5 5 0 0 1 6 0 5 5 0 0 0 6 0'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
