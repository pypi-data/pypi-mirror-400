
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowBigRightDash(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-big-right-dash'], 'items': [{'path': {'d': 'M11 9a1 1 0 0 0 1-1V5.061a1 1 0 0 1 1.811-.75l6.836 6.836a1.207 1.207 0 0 1 0 1.707l-6.836 6.835a1 1 0 0 1-1.811-.75V16a1 1 0 0 0-1-1H9a1 1 0 0 1-1-1v-4a1 1 0 0 1 1-1z'}}, {'path': {'d': 'M4 9v6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
