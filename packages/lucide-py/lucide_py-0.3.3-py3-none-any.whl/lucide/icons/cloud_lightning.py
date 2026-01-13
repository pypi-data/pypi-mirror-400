
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CloudLightning(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-cloud-lightning'], 'items': [{'path': {'d': 'M6 16.326A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 .5 8.973'}}, {'path': {'d': 'm13 12-3 5h4l-3 5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
