
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MonitorUp(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-monitor-up'], 'items': [{'path': {'d': 'm9 10 3-3 3 3'}}, {'path': {'d': 'M12 13V7'}}, {'rect': {'width': '20', 'height': '14', 'x': '2', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M12 17v4'}}, {'path': {'d': 'M8 21h8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
