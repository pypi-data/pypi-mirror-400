
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Axis3d(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-axis-3d'], 'items': [{'path': {'d': 'M13.5 10.5 15 9'}}, {'path': {'d': 'M4 4v15a1 1 0 0 0 1 1h15'}}, {'path': {'d': 'M4.293 19.707 6 18'}}, {'path': {'d': 'm9 15 1.5-1.5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
