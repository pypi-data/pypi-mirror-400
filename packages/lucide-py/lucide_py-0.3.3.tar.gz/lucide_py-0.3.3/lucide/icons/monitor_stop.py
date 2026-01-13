
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MonitorStop(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-monitor-stop'], 'items': [{'path': {'d': 'M12 17v4'}}, {'path': {'d': 'M8 21h8'}}, {'rect': {'x': '2', 'y': '3', 'width': '20', 'height': '14', 'rx': '2'}}, {'rect': {'x': '9', 'y': '7', 'width': '6', 'height': '6', 'rx': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
