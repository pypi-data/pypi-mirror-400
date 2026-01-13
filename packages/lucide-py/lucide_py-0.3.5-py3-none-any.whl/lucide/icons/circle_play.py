
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CirclePlay(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-play'], 'items': [{'path': {'d': 'M9 9.003a1 1 0 0 1 1.517-.859l4.997 2.997a1 1 0 0 1 0 1.718l-4.997 2.997A1 1 0 0 1 9 14.996z'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
