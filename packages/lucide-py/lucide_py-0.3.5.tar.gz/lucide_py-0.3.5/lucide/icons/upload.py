
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Upload(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-upload'], 'items': [{'path': {'d': 'M12 3v12'}}, {'path': {'d': 'm17 8-5-5-5 5'}}, {'path': {'d': 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
