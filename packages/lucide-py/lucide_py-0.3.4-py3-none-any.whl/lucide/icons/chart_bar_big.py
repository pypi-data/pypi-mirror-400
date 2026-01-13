
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChartBarBig(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chart-bar-big'], 'items': [{'path': {'d': 'M3 3v16a2 2 0 0 0 2 2h16'}}, {'rect': {'x': '7', 'y': '13', 'width': '9', 'height': '4', 'rx': '1'}}, {'rect': {'x': '7', 'y': '5', 'width': '12', 'height': '4', 'rx': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
