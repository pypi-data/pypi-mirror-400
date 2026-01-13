
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def DollarSign(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-dollar-sign'], 'items': [{'line': {'x1': '12', 'x2': '12', 'y1': '2', 'y2': '22'}}, {'path': {'d': 'M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
