
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CirclePlus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-plus'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'M8 12h8'}}, {'path': {'d': 'M12 8v8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
