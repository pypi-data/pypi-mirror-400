
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChartNoAxesColumnIncreasing(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chart-no-axes-column-increasing'], 'items': [{'path': {'d': 'M5 21v-6'}}, {'path': {'d': 'M12 21V9'}}, {'path': {'d': 'M19 21V3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
