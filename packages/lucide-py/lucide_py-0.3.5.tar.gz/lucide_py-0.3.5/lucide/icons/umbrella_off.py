
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def UmbrellaOff(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-umbrella-off'], 'items': [{'path': {'d': 'M12 13v7a2 2 0 0 0 4 0'}}, {'path': {'d': 'M12 2v2'}}, {'path': {'d': 'M18.656 13h2.336a1 1 0 0 0 .97-1.274 10.284 10.284 0 0 0-12.07-7.51'}}, {'path': {'d': 'm2 2 20 20'}}, {'path': {'d': 'M5.961 5.957a10.28 10.28 0 0 0-3.922 5.769A1 1 0 0 0 3 13h10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
