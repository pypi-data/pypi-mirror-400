
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CreditCard(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-credit-card'], 'items': [{'rect': {'width': '20', 'height': '14', 'x': '2', 'y': '5', 'rx': '2'}}, {'line': {'x1': '2', 'x2': '22', 'y1': '10', 'y2': '10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
