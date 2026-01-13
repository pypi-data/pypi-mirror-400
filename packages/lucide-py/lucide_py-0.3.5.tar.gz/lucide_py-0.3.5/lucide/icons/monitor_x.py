
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MonitorX(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-monitor-x'], 'items': [{'path': {'d': 'm14.5 12.5-5-5'}}, {'path': {'d': 'm9.5 12.5 5-5'}}, {'rect': {'width': '20', 'height': '14', 'x': '2', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M12 17v4'}}, {'path': {'d': 'M8 21h8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
