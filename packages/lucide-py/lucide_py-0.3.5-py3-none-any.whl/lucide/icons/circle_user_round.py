
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleUserRound(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-user-round'], 'items': [{'path': {'d': 'M18 20a6 6 0 0 0-12 0'}}, {'circle': {'cx': '12', 'cy': '10', 'r': '4'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
