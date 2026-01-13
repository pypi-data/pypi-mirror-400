
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleGauge(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-gauge'], 'items': [{'path': {'d': 'M15.6 2.7a10 10 0 1 0 5.7 5.7'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '2'}}, {'path': {'d': 'M13.4 10.6 19 5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
