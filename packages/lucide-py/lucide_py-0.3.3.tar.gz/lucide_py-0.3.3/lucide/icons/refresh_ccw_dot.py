
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def RefreshCcwDot(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-refresh-ccw-dot'], 'items': [{'path': {'d': 'M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8'}}, {'path': {'d': 'M3 3v5h5'}}, {'path': {'d': 'M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16'}}, {'path': {'d': 'M16 16h5v5'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
