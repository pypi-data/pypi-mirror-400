
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Terminal(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-terminal'], 'items': [{'path': {'d': 'M12 19h8'}}, {'path': {'d': 'm4 17 6-6-6-6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
