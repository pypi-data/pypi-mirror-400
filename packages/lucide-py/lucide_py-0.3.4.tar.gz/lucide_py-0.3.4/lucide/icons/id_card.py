
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def IdCard(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-id-card'], 'items': [{'path': {'d': 'M16 10h2'}}, {'path': {'d': 'M16 14h2'}}, {'path': {'d': 'M6.17 15a3 3 0 0 1 5.66 0'}}, {'circle': {'cx': '9', 'cy': '11', 'r': '2'}}, {'rect': {'x': '2', 'y': '5', 'width': '20', 'height': '14', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
