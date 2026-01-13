
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MonitorDot(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-monitor-dot'], 'items': [{'path': {'d': 'M12 17v4'}}, {'path': {'d': 'M22 12.307V15a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h8.693'}}, {'path': {'d': 'M8 21h8'}}, {'circle': {'cx': '19', 'cy': '6', 'r': '3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
