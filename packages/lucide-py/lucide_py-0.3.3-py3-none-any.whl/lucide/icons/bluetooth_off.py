
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BluetoothOff(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-bluetooth-off'], 'items': [{'path': {'d': 'm17 17-5 5V12l-5 5'}}, {'path': {'d': 'm2 2 20 20'}}, {'path': {'d': 'M14.5 9.5 17 7l-5-5v4.5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
