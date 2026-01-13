
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Banknote(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-banknote'], 'items': [{'rect': {'width': '20', 'height': '12', 'x': '2', 'y': '6', 'rx': '2'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '2'}}, {'path': {'d': 'M6 12h.01M18 12h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
