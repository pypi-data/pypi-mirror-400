
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChartLine(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chart-line'], 'items': [{'path': {'d': 'M3 3v16a2 2 0 0 0 2 2h16'}}, {'path': {'d': 'm19 9-5 5-4-4-3 3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
