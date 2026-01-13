
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChartNoAxesColumnDecreasing(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chart-no-axes-column-decreasing'], 'items': [{'path': {'d': 'M5 21V3'}}, {'path': {'d': 'M12 21V9'}}, {'path': {'d': 'M19 21v-6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
