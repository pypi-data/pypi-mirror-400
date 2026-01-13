
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChartNoAxesColumn(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chart-no-axes-column'], 'items': [{'path': {'d': 'M5 21v-6'}}, {'path': {'d': 'M12 21V3'}}, {'path': {'d': 'M19 21V9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
