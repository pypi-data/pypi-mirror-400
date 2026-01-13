
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def HardHat(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-hard-hat'], 'items': [{'path': {'d': 'M10 10V5a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v5'}}, {'path': {'d': 'M14 6a6 6 0 0 1 6 6v3'}}, {'path': {'d': 'M4 15v-3a6 6 0 0 1 6-6'}}, {'rect': {'x': '2', 'y': '15', 'width': '20', 'height': '4', 'rx': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
