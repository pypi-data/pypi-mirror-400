
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleSlash2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-slash-2'], 'items': [{'path': {'d': 'M22 2 2 22'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
