
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Mic(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-mic'], 'items': [{'path': {'d': 'M12 19v3'}}, {'path': {'d': 'M19 10v2a7 7 0 0 1-14 0v-2'}}, {'rect': {'x': '9', 'y': '2', 'width': '6', 'height': '13', 'rx': '3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
