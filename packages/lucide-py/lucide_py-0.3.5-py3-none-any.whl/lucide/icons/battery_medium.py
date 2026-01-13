
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BatteryMedium(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-battery-medium'], 'items': [{'path': {'d': 'M10 14v-4'}}, {'path': {'d': 'M22 14v-4'}}, {'path': {'d': 'M6 14v-4'}}, {'rect': {'x': '2', 'y': '6', 'width': '16', 'height': '12', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
