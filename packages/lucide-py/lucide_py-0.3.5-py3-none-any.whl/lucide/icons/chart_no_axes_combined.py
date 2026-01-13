
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChartNoAxesCombined(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chart-no-axes-combined'], 'items': [{'path': {'d': 'M12 16v5'}}, {'path': {'d': 'M16 14v7'}}, {'path': {'d': 'M20 10v11'}}, {'path': {'d': 'm22 3-8.646 8.646a.5.5 0 0 1-.708 0L9.354 8.354a.5.5 0 0 0-.707 0L2 15'}}, {'path': {'d': 'M4 18v3'}}, {'path': {'d': 'M8 14v7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
