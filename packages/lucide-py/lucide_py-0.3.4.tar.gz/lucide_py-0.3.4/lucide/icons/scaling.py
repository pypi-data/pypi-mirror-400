
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Scaling(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-scaling'], 'items': [{'path': {'d': 'M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7'}}, {'path': {'d': 'M14 15H9v-5'}}, {'path': {'d': 'M16 3h5v5'}}, {'path': {'d': 'M21 3 9 15'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
