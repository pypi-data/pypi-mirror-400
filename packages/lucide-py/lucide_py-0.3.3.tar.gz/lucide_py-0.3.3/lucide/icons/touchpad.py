
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Touchpad(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-touchpad'], 'items': [{'rect': {'width': '20', 'height': '16', 'x': '2', 'y': '4', 'rx': '2'}}, {'path': {'d': 'M2 14h20'}}, {'path': {'d': 'M12 20v-6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
