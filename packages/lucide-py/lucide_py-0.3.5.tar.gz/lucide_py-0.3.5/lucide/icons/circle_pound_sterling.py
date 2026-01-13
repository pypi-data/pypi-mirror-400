
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CirclePoundSterling(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-pound-sterling'], 'items': [{'path': {'d': 'M10 16V9.5a1 1 0 0 1 5 0'}}, {'path': {'d': 'M8 12h4'}}, {'path': {'d': 'M8 16h7'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
