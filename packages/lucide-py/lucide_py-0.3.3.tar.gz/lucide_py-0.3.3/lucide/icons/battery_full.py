
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BatteryFull(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-battery-full'], 'items': [{'path': {'d': 'M10 10v4'}}, {'path': {'d': 'M14 10v4'}}, {'path': {'d': 'M22 14v-4'}}, {'path': {'d': 'M6 10v4'}}, {'rect': {'x': '2', 'y': '6', 'width': '16', 'height': '12', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
