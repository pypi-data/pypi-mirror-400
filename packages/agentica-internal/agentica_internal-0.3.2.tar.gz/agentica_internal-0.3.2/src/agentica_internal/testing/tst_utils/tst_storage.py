import re
from pathlib import Path
from typing import Callable, Self

from ...core.strs import pathsafe_str

__all__ = [
    'FileSection',
    'FileTemplate',
]

###############################################################################


class FileSection(Path):
    base: Path
    elem: str
    _key: str
    _pat: str
    _sin: Callable[[str], str]
    _mul: Callable[[str], str]

    def __init__(self, path: str | Path, elem: str) -> None:
        super().__init__(path)
        self.base = Path(path)
        self.elem = elem
        key = f'⟨{elem}⟩'
        pad = key.ljust(32)
        lhs = re.escape(key)
        self._key = key = f'⟨{elem}⟩'
        self._pat = f'{lhs}\\s*⟪{VAL}⟫\n'
        self._sin = f'{pad}⟪{{}}⟫\n'.format
        self._mul = f'{key}\n⟪{{}}⟫\n'.format

    def __str__(self) -> str:
        line = 0
        if self.__exists():
            if txt := self.__read():
                key = self._key
                if key in txt:
                    for i, l in enumerate(txt.splitlines()):
                        if l.startswith(key):
                            line = i + 1
                            break
        file = self.base.as_posix()
        if line:
            file = f'{file}:{line}'
        return f'{file}#{self.elem}'

    def __repr__(self) -> str:
        return f'SegmentedFile({str(self)!r})'

    def __fspath__(self) -> str:
        return self.base.as_posix()

    def absolute(self) -> Self:
        if self.base.is_absolute():
            return self
        return FileSection(self.base.absolute(), self.elem)

    def exists(self, **_) -> bool:
        return self.__exists() and self._key in self.__read()

    def unlink(self, **_):
        text = self.__read()
        if self._key not in text:
            return
        if text := re.sub(self._pat, '', text):
            self.__write(text)
        else:
            self.base.unlink()

    def write_text(self, text: str, **_) -> None:
        prev = self.__read()
        new = self._mul(text) if '\n' in text else self._sin(text)
        if self._key not in prev:
            self.__write(prev + new)
        else:
            self.__write(re.sub(self._pat, new, prev))

    @property
    def parent(self) -> Path:
        return self.base.parent

    def read_text(self, **_) -> str:
        text = self.__read()
        if self._key not in text:
            raise RuntimeError(f'segment {self.elem!r} not found in {self.__base}')
        pat = self._pat
        match = re.search(pat, text)
        if match is None:
            raise RuntimeError(f'RE did not match: {pat!r}')
        return match.group(1)

    def __exists(self) -> bool:
        base = self.base
        return base.exists() and base.is_file()

    def __write(self, s: str):
        self.base.write_text(s)

    def __read(self) -> str:
        base = self.base
        if not base.exists():
            return ''
        assert base.is_file(), f'{base!r} not a file'
        return base.read_text()


VAL = r'([^⟪⟫]*)'


class FileTemplate:
    parts: list[str | Path]
    section: str | None

    def __init__(self, *parts: str | Path, section: str = None) -> None:
        *path, file = list(parts)
        path = [p.removesuffix('.py') for p in path]
        self.parts = [*path, file]
        self.section = section

    # def absolute(self) -> Path:
    #     parts = self.parts.copy()
    #     parts[0] = parts[0].absolute()
    #     return replace(self, parts=parts)

    def __str__(self) -> str:
        return '~' + '/'.join(self.parts) + f'#{self.section}' if self.section else ''

    def __repr__(self) -> str:
        return f'FileTemplate(parts={self.parts!r}, section={self.section!r})'

    def format(self, **kwargs):
        parts = self.parts
        section = self.section
        safe = {k: pathsafe_str(v) for k, v in kwargs.items()}
        parts = [p.format(**safe) if type(p) is str else p for p in parts]
        path = Path(*parts)
        if not section:
            return path
        if path.exists() and path.is_dir():
            raise ValueError('base path {path!r} already exists and is a directory')
        section = section.format(**kwargs)
        return FileSection(path, section)
