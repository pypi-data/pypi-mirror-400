
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def InspectionPanel(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-inspection-panel'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M7 7h.01'}}, {'path': {'d': 'M17 7h.01'}}, {'path': {'d': 'M7 17h.01'}}, {'path': {'d': 'M17 17h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
