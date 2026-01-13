
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TrainTrack(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-train-track'], 'items': [{'path': {'d': 'M2 17 17 2'}}, {'path': {'d': 'm2 14 8 8'}}, {'path': {'d': 'm5 11 8 8'}}, {'path': {'d': 'm8 8 8 8'}}, {'path': {'d': 'm11 5 8 8'}}, {'path': {'d': 'm14 2 8 8'}}, {'path': {'d': 'M7 22 22 7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
