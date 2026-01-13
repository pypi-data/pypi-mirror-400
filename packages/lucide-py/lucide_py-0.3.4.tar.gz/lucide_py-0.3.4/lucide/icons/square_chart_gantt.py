
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareChartGantt(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-chart-gantt'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M9 8h7'}}, {'path': {'d': 'M8 12h6'}}, {'path': {'d': 'M11 16h5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
