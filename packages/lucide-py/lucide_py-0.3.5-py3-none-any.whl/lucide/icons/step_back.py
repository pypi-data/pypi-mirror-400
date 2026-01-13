
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def StepBack(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-step-back'], 'items': [{'path': {'d': 'M13.971 4.285A2 2 0 0 1 17 6v12a2 2 0 0 1-3.029 1.715l-9.997-5.998a2 2 0 0 1-.003-3.432z'}}, {'path': {'d': 'M21 20V4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
