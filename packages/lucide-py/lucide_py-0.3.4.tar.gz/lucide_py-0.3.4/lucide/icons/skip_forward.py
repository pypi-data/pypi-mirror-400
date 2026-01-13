
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SkipForward(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-skip-forward'], 'items': [{'path': {'d': 'M21 4v16'}}, {'path': {'d': 'M6.029 4.285A2 2 0 0 0 3 6v12a2 2 0 0 0 3.029 1.715l9.997-5.998a2 2 0 0 0 .003-3.432z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
