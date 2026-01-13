
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TouchpadOff(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-touchpad-off'], 'items': [{'path': {'d': 'M12 20v-6'}}, {'path': {'d': 'M19.656 14H22'}}, {'path': {'d': 'M2 14h12'}}, {'path': {'d': 'm2 2 20 20'}}, {'path': {'d': 'M20 20H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2'}}, {'path': {'d': 'M9.656 4H20a2 2 0 0 1 2 2v10.344'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
