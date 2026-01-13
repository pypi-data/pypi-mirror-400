
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def RadioReceiver(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-radio-receiver'], 'items': [{'path': {'d': 'M5 16v2'}}, {'path': {'d': 'M19 16v2'}}, {'rect': {'width': '20', 'height': '8', 'x': '2', 'y': '8', 'rx': '2'}}, {'path': {'d': 'M18 12h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
