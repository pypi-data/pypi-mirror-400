
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PoundSterling(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-pound-sterling'], 'items': [{'path': {'d': 'M18 7c0-5.333-8-5.333-8 0'}}, {'path': {'d': 'M10 7v14'}}, {'path': {'d': 'M6 21h12'}}, {'path': {'d': 'M6 13h10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
