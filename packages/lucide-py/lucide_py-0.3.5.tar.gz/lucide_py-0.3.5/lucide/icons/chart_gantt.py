
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChartGantt(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chart-gantt'], 'items': [{'path': {'d': 'M10 6h8'}}, {'path': {'d': 'M12 16h6'}}, {'path': {'d': 'M3 3v16a2 2 0 0 0 2 2h16'}}, {'path': {'d': 'M8 11h7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
