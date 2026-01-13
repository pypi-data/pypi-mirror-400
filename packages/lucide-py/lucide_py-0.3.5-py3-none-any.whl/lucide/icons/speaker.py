
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Speaker(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-speaker'], 'items': [{'rect': {'width': '16', 'height': '20', 'x': '4', 'y': '2', 'rx': '2'}}, {'path': {'d': 'M12 6h.01'}}, {'circle': {'cx': '12', 'cy': '14', 'r': '4'}}, {'path': {'d': 'M12 14h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
