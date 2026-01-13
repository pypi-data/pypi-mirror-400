
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def UsersRound(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-users-round'], 'items': [{'path': {'d': 'M18 21a8 8 0 0 0-16 0'}}, {'circle': {'cx': '10', 'cy': '8', 'r': '5'}}, {'path': {'d': 'M22 20c0-3.37-2-6.5-4-8a5 5 0 0 0-.45-8.3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
