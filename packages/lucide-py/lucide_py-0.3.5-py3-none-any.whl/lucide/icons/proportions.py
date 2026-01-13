
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Proportions(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-proportions'], 'items': [{'rect': {'width': '20', 'height': '16', 'x': '2', 'y': '4', 'rx': '2'}}, {'path': {'d': 'M12 9v11'}}, {'path': {'d': 'M2 9h13a2 2 0 0 1 2 2v9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
