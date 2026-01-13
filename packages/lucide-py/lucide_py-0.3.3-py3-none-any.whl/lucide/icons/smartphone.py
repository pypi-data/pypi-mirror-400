
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Smartphone(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-smartphone'], 'items': [{'rect': {'width': '14', 'height': '20', 'x': '5', 'y': '2', 'rx': '2', 'ry': '2'}}, {'path': {'d': 'M12 18h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
