
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Database(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-database'], 'items': [{'ellipse': {'cx': '12', 'cy': '5', 'rx': '9', 'ry': '3'}}, {'path': {'d': 'M3 5V19A9 3 0 0 0 21 19V5'}}, {'path': {'d': 'M3 12A9 3 0 0 0 21 12'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
