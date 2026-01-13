
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChartNoAxesGantt(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chart-no-axes-gantt'], 'items': [{'path': {'d': 'M6 5h12'}}, {'path': {'d': 'M4 12h10'}}, {'path': {'d': 'M12 19h8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
