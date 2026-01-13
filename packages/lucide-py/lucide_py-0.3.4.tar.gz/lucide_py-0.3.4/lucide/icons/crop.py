
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Crop(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-crop'], 'items': [{'path': {'d': 'M6 2v14a2 2 0 0 0 2 2h14'}}, {'path': {'d': 'M18 22V8a2 2 0 0 0-2-2H2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
