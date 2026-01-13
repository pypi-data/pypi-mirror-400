
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareDashedBottom(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-dashed-bottom'], 'items': [{'path': {'d': 'M5 21a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2'}}, {'path': {'d': 'M9 21h1'}}, {'path': {'d': 'M14 21h1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
