
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def NonBinary(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-non-binary'], 'items': [{'path': {'d': 'M12 2v10'}}, {'path': {'d': 'm8.5 4 7 4'}}, {'path': {'d': 'm8.5 8 7-4'}}, {'circle': {'cx': '12', 'cy': '17', 'r': '5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
