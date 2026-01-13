
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BatteryCharging(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-battery-charging'], 'items': [{'path': {'d': 'm11 7-3 5h4l-3 5'}}, {'path': {'d': 'M14.856 6H16a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.935'}}, {'path': {'d': 'M22 14v-4'}}, {'path': {'d': 'M5.14 18H4a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h2.936'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
