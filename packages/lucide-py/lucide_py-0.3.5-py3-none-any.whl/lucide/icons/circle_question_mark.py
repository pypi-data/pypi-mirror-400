
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleQuestionMark(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-question-mark'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3'}}, {'path': {'d': 'M12 17h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
