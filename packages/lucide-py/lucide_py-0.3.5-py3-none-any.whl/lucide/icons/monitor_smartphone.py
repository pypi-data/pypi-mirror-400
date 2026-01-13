
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MonitorSmartphone(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-monitor-smartphone'], 'items': [{'path': {'d': 'M18 8V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h8'}}, {'path': {'d': 'M10 19v-3.96 3.15'}}, {'path': {'d': 'M7 19h5'}}, {'rect': {'width': '6', 'height': '10', 'x': '16', 'y': '12', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
