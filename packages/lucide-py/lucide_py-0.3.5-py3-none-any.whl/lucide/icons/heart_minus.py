
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def HeartMinus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-heart-minus'], 'items': [{'path': {'d': 'm14.876 18.99-1.368 1.323a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5a5.2 5.2 0 0 1-.244 1.572'}}, {'path': {'d': 'M15 15h6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
