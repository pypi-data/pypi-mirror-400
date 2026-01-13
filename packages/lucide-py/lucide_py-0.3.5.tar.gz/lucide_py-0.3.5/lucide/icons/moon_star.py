
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MoonStar(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-moon-star'], 'items': [{'path': {'d': 'M18 5h4'}}, {'path': {'d': 'M20 3v4'}}, {'path': {'d': 'M20.985 12.486a9 9 0 1 1-9.473-9.472c.405-.022.617.46.402.803a6 6 0 0 0 8.268 8.268c.344-.215.825-.004.803.401'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
