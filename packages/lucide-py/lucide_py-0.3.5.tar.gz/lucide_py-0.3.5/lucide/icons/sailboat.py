
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Sailboat(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-sailboat'], 'items': [{'path': {'d': 'M10 2v15'}}, {'path': {'d': 'M7 22a4 4 0 0 1-4-4 1 1 0 0 1 1-1h16a1 1 0 0 1 1 1 4 4 0 0 1-4 4z'}}, {'path': {'d': 'M9.159 2.46a1 1 0 0 1 1.521-.193l9.977 8.98A1 1 0 0 1 20 13H4a1 1 0 0 1-.824-1.567z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
