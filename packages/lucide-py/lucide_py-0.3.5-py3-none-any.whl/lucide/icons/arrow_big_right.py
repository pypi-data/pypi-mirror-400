
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowBigRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-big-right'], 'items': [{'path': {'d': 'M11 9a1 1 0 0 0 1-1V5.061a1 1 0 0 1 1.811-.75l6.836 6.836a1.207 1.207 0 0 1 0 1.707l-6.836 6.835a1 1 0 0 1-1.811-.75V16a1 1 0 0 0-1-1H5a1 1 0 0 1-1-1v-4a1 1 0 0 1 1-1z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
