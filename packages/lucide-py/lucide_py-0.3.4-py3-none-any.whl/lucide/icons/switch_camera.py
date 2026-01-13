
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SwitchCamera(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-switch-camera'], 'items': [{'path': {'d': 'M11 19H4a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h5'}}, {'path': {'d': 'M13 5h7a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-5'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '3'}}, {'path': {'d': 'm18 22-3-3 3-3'}}, {'path': {'d': 'm6 2 3 3-3 3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
