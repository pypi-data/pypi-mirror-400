
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ScreenShare(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-screen-share'], 'items': [{'path': {'d': 'M13 3H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-3'}}, {'path': {'d': 'M8 21h8'}}, {'path': {'d': 'M12 17v4'}}, {'path': {'d': 'm17 8 5-5'}}, {'path': {'d': 'M17 3h5v5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
