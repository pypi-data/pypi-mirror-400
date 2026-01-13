
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PcCase(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-pc-case'], 'items': [{'rect': {'width': '14', 'height': '20', 'x': '5', 'y': '2', 'rx': '2'}}, {'path': {'d': 'M15 14h.01'}}, {'path': {'d': 'M9 6h6'}}, {'path': {'d': 'M9 10h6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
