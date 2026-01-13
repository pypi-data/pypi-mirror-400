
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def FolderGit2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-folder-git-2'], 'items': [{'path': {'d': 'M18 19a5 5 0 0 1-5-5v8'}}, {'path': {'d': 'M9 20H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h3.9a2 2 0 0 1 1.69.9l.81 1.2a2 2 0 0 0 1.67.9H20a2 2 0 0 1 2 2v5'}}, {'circle': {'cx': '13', 'cy': '12', 'r': '2'}}, {'circle': {'cx': '20', 'cy': '19', 'r': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
