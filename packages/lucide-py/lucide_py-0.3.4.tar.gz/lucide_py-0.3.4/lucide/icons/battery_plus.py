
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BatteryPlus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-battery-plus'], 'items': [{'path': {'d': 'M10 9v6'}}, {'path': {'d': 'M12.543 6H16a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-3.605'}}, {'path': {'d': 'M22 14v-4'}}, {'path': {'d': 'M7 12h6'}}, {'path': {'d': 'M7.606 18H4a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h3.606'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
