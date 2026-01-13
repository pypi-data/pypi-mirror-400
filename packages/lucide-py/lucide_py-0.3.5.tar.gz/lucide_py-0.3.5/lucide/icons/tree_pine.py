
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TreePine(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-tree-pine'], 'items': [{'path': {'d': 'm17 14 3 3.3a1 1 0 0 1-.7 1.7H4.7a1 1 0 0 1-.7-1.7L7 14h-.3a1 1 0 0 1-.7-1.7L9 9h-.2A1 1 0 0 1 8 7.3L12 3l4 4.3a1 1 0 0 1-.8 1.7H15l3 3.3a1 1 0 0 1-.7 1.7H17Z'}}, {'path': {'d': 'M12 22v-3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
