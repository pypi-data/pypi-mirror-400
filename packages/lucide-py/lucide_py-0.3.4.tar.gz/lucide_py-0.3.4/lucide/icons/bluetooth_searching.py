
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BluetoothSearching(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-bluetooth-searching'], 'items': [{'path': {'d': 'm7 7 10 10-5 5V2l5 5L7 17'}}, {'path': {'d': 'M20.83 14.83a4 4 0 0 0 0-5.66'}}, {'path': {'d': 'M18 12h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
