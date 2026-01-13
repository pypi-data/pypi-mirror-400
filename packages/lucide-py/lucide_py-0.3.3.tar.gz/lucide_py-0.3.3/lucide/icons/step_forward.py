
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def StepForward(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-step-forward'], 'items': [{'path': {'d': 'M10.029 4.285A2 2 0 0 0 7 6v12a2 2 0 0 0 3.029 1.715l9.997-5.998a2 2 0 0 0 .003-3.432z'}}, {'path': {'d': 'M3 4v16'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
