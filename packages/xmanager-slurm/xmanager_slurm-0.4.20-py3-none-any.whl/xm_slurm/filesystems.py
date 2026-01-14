import abc
import asyncio
import os
import typing as tp

import aiofile
import asyncssh
import typing_extensions as tpe
import wrapt


class AsyncFileIO(tp.Protocol):
    async def write(self, buffer: str | bytes, /) -> int: ...
    async def read(self, size: int = -1, /) -> bytes: ...
    async def seek(self, offset: int, /) -> int: ...
    async def tell(self) -> int: ...
    async def __aenter__(self) -> tpe.Self: ...
    async def __aexit__(self, *args: tp.Any, **kwargs: tp.Any) -> None: ...


class AsyncFileSystem(tp.Protocol):
    async def open(
        self,
        path: os.PathLike[str] | str,
        mode: tp.Literal["r", "w", "rb", "wb"],
        *,
        encoding: str = "utf-8",
    ) -> AsyncFileIO: ...

    async def read(
        self, path: os.PathLike[str] | str, *, size: int = -1, offset: int = 0
    ) -> bytes: ...
    async def write(
        self, path: os.PathLike[str] | str, data: str | bytes, *, offset: int = 0
    ) -> None: ...

    async def exists(self, path: os.PathLike[str] | str) -> bool: ...
    async def size(self, path: os.PathLike[str] | str) -> int | None: ...
    async def makedirs(
        self, path: os.PathLike[str] | str, mode: int = 511, exist_ok: bool = False
    ) -> None: ...


class AbstractAsyncFileSystem(AsyncFileSystem, abc.ABC):
    @abc.abstractmethod
    async def open(
        self,
        path: os.PathLike[str] | str,
        mode: tp.Literal["r", "w", "rb", "wb"],
        *,
        encoding: str = "utf-8",
    ) -> AsyncFileIO: ...

    async def read(self, path: os.PathLike[str] | str, *, size: int = -1, offset: int = 0) -> bytes:
        async with await self.open(path, "rb") as f:
            await f.seek(offset)
            return await f.read(size)

    async def write(
        self, path: os.PathLike[str] | str, data: str | bytes, *, offset: int = 0
    ) -> None:
        async with await self.open(path, "wb") as f:
            await f.seek(offset)
            await f.write(data)


class AsyncLocalFileIO(wrapt.ObjectProxy):
    async def seek(self, offset: int, /) -> int:
        await asyncio.to_thread(self.__wrapped__.seek, offset)
        return await asyncio.to_thread(self.__wrapped__.tell)

    async def tell(self) -> int:
        return await asyncio.to_thread(self.__wrapped__.tell)

    async def __aenter__(self) -> tpe.Self:  # ty:ignore[invalid-return-type]
        return AsyncLocalFileIO(
            await self.__wrapped__.__aenter__()
        )  # ty:ignore[invalid-return-type]

    async def __aexit__(self, *args: tp.Any, **kwargs: tp.Any) -> None:
        return await self.__wrapped__.__aexit__(*args, **kwargs)


class AsyncLocalFileSystem(AbstractAsyncFileSystem):
    def __init__(self): ...

    async def open(
        self,
        path: os.PathLike[str] | str,
        mode: tp.Literal["r", "w", "rb", "wb"],
        *,
        encoding: str = "utf-8",
    ) -> AsyncFileIO:
        return AsyncLocalFileIO(aiofile.async_open(os.fspath(path), mode=mode, encoding=encoding))  # type: ignore

    async def exists(self, path: os.PathLike[str] | str) -> bool:
        return await asyncio.to_thread(os.path.exists, os.fspath(path))

    async def size(self, path: os.PathLike[str] | str) -> int | None:
        return await asyncio.to_thread(os.path.getsize, os.fspath(path))

    async def makedirs(
        self, path: os.PathLike[str] | str, mode: int = 0o777, exist_ok: bool = False
    ) -> None:
        return await asyncio.to_thread(os.makedirs, os.fspath(path), mode=mode, exist_ok=exist_ok)


class AsyncSSHFileSystem(AbstractAsyncFileSystem):
    def __init__(self, client: asyncssh.SFTPClient):
        self._client = client

    async def open(
        self,
        path: os.PathLike[str] | str,
        mode: tp.Literal["r", "w", "rb", "wb"],
        *,
        encoding: str = "utf-8",
    ) -> AsyncFileIO:
        return await self._client.open(os.fspath(path), mode, encoding=encoding)  # type: ignore

    async def exists(self, path: os.PathLike[str] | str) -> bool:
        return await self._client.exists(os.fspath(path))

    async def size(self, path: os.PathLike[str] | str) -> int | None:
        return (await self._client.stat(os.fspath(path))).size

    async def makedirs(
        self, path: os.PathLike[str] | str, mode: int = 0o777, exist_ok: bool = False
    ) -> None:
        attrs = asyncssh.SFTPAttrs(permissions=mode)
        return await self._client.makedirs(os.fspath(path), attrs=attrs, exist_ok=exist_ok)
