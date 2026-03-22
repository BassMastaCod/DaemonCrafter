from pathlib import Path
from typing import Any


class Executable:
    def __init__(self, parent: Path, target: Any):
        self.parent = parent
        self.target = target

    def __repr__(self) -> str:
        return str(self.target)


def ASGIApp(
        parent: Path,
        server: str = 'uvicorn',
        file: str = 'main',
        app: str = 'app',
        public: bool = False
) -> Executable:
    target = f'{server} {file}:{app}'
    if public:
        target += ' --host 0.0.0.0'
    return Executable(parent, f'-m {target}')
