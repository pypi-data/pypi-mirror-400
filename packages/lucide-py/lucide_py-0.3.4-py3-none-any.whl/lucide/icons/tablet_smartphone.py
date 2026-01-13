
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TabletSmartphone(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-tablet-smartphone'], 'items': [{'rect': {'width': '10', 'height': '14', 'x': '3', 'y': '8', 'rx': '2'}}, {'path': {'d': 'M5 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2h-2.4'}}, {'path': {'d': 'M8 18h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
