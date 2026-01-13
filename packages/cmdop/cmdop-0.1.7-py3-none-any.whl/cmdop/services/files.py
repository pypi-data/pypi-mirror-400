"""
Files service for CMDOP SDK.

Provides file system operations: list, read, write, delete, copy, move.
Supports both sync and async patterns.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from cmdop.models.files import (
    FileEntry,
    FileInfo,
    FileType,
    ListDirectoryResponse,
)
from cmdop.services.base import BaseService

if TYPE_CHECKING:
    from cmdop.transport.base import BaseTransport


def _parse_file_type(pb_type: int) -> FileType:
    """Convert protobuf file type to enum."""
    # Map based on proto enum values
    type_map = {
        0: FileType.UNKNOWN,
        1: FileType.FILE,
        2: FileType.DIRECTORY,
        3: FileType.SYMLINK,
    }
    return type_map.get(pb_type, FileType.UNKNOWN)


def _parse_timestamp(ts: Any) -> datetime | None:
    """Convert protobuf timestamp to datetime."""
    if ts is None:
        return None
    try:
        if hasattr(ts, "seconds"):
            return datetime.fromtimestamp(ts.seconds, tz=timezone.utc)
        return None
    except (ValueError, OSError):
        return None


class FilesService(BaseService):
    """
    Synchronous files service.

    Provides file system operations.

    Example:
        >>> entries = client.files.list("/home/user")
        >>> content = client.files.read("/etc/hosts")
        >>> client.files.write("/tmp/test.txt", b"Hello")
    """

    def __init__(self, transport: BaseTransport) -> None:
        super().__init__(transport)
        self._stub: Any = None

    @property
    def _get_stub(self) -> Any:
        """Lazy-load gRPC stub."""
        if self._stub is None:
            from cmdop._generated.service_pb2_grpc import (
                TerminalStreamingServiceStub,
            )

            self._stub = TerminalStreamingServiceStub(self._channel)
        return self._stub

    def list(
        self,
        path: str,
        include_hidden: bool = False,
        page_size: int = 100,
        page_token: str | None = None,
    ) -> ListDirectoryResponse:
        """
        List directory contents.

        Args:
            path: Directory path to list
            include_hidden: Include hidden files
            page_size: Number of entries per page
            page_token: Pagination token

        Returns:
            Directory listing response
        """
        from cmdop._generated.file_rpc.directory_pb2 import (
            FileListDirectoryRpcRequest,
        )

        request = FileListDirectoryRpcRequest(
            path=path,
            page_size=page_size,
            include_hidden=include_hidden,
        )
        if page_token:
            request.page_token = page_token

        response = self._call_sync(self._get_stub.FileListDirectory, request)

        entries = []
        for entry in response.result.entries:
            entries.append(
                FileEntry(
                    name=entry.name,
                    path=entry.path,
                    type=_parse_file_type(entry.type),
                    size=entry.size,
                    modified_at=_parse_timestamp(entry.modified_at),
                    is_hidden=entry.name.startswith("."),
                )
            )

        return ListDirectoryResponse(
            path=response.result.current_path,
            entries=entries,
            next_page_token=response.result.next_page_token or None,
            total_count=response.result.total_count,
        )

    def read(
        self,
        path: str,
        offset: int = 0,
        limit: int = 0,
    ) -> bytes:
        """
        Read file contents.

        Args:
            path: File path to read
            offset: Byte offset to start reading
            limit: Maximum bytes to read (0 = entire file)

        Returns:
            File contents as bytes
        """
        from cmdop._generated.file_rpc.file_crud_pb2 import FileReadRpcRequest

        request = FileReadRpcRequest(
            path=path,
        )

        response = self._call_sync(self._get_stub.FileRead, request)
        return response.result.content

    def write(
        self,
        path: str,
        content: bytes | str,
        create_parents: bool = False,
        overwrite: bool = True,
    ) -> None:
        """
        Write file contents.

        Args:
            path: File path to write
            content: Content to write (bytes or string)
            create_parents: Create parent directories
            overwrite: Overwrite existing file
        """
        from cmdop._generated.file_rpc.file_crud_pb2 import FileWriteRpcRequest

        if isinstance(content, str):
            content = content.encode("utf-8")

        request = FileWriteRpcRequest(
            path=path,
            content=content,
            create_parents=create_parents,
        )

        self._call_sync(self._get_stub.FileWrite, request)

    def delete(self, path: str, recursive: bool = False) -> None:
        """
        Delete file or directory.

        Args:
            path: Path to delete
            recursive: Delete directory recursively
        """
        from cmdop._generated.file_rpc.file_crud_pb2 import FileDeleteRpcRequest

        request = FileDeleteRpcRequest(
            path=path,
            recursive=recursive,
        )

        self._call_sync(self._get_stub.FileDelete, request)

    def copy(self, source: str, destination: str) -> None:
        """
        Copy file or directory.

        Args:
            source: Source path
            destination: Destination path
        """
        from cmdop._generated.file_rpc.file_crud_pb2 import FileCopyRpcRequest

        request = FileCopyRpcRequest(
            source_path=source,
            destination_path=destination,
        )

        self._call_sync(self._get_stub.FileCopy, request)

    def move(self, source: str, destination: str) -> None:
        """
        Move/rename file or directory.

        Args:
            source: Source path
            destination: Destination path
        """
        from cmdop._generated.file_rpc.file_crud_pb2 import FileMoveRpcRequest

        request = FileMoveRpcRequest(
            source_path=source,
            destination_path=destination,
        )

        self._call_sync(self._get_stub.FileMove, request)

    def info(self, path: str) -> FileInfo:
        """
        Get file information.

        Args:
            path: File path

        Returns:
            Detailed file information
        """
        from cmdop._generated.file_rpc.file_crud_pb2 import FileGetInfoRpcRequest

        request = FileGetInfoRpcRequest(path=path)
        response = self._call_sync(self._get_stub.FileGetInfo, request)

        entry = response.result.entry
        return FileInfo(
            path=entry.path,
            type=_parse_file_type(entry.type),
            size=entry.size,
            modified_at=_parse_timestamp(entry.modified_at),
            permissions=entry.permissions if hasattr(entry, "permissions") else None,
        )

    def mkdir(self, path: str, create_parents: bool = True) -> None:
        """
        Create directory.

        Args:
            path: Directory path to create
            create_parents: Create parent directories
        """
        from cmdop._generated.file_rpc.file_crud_pb2 import (
            FileCreateDirectoryRpcRequest,
        )

        request = FileCreateDirectoryRpcRequest(
            path=path,
            create_parents=create_parents,
        )

        self._call_sync(self._get_stub.FileCreateDirectory, request)


class AsyncFilesService(BaseService):
    """
    Asynchronous files service.

    Provides async file system operations.
    """

    def __init__(self, transport: BaseTransport) -> None:
        super().__init__(transport)
        self._stub: Any = None

    @property
    def _get_stub(self) -> Any:
        """Lazy-load async gRPC stub."""
        if self._stub is None:
            from cmdop._generated.service_pb2_grpc import (
                TerminalStreamingServiceStub,
            )

            self._stub = TerminalStreamingServiceStub(self._async_channel)
        return self._stub

    async def list(
        self,
        path: str,
        include_hidden: bool = False,
        page_size: int = 100,
        page_token: str | None = None,
    ) -> ListDirectoryResponse:
        """List directory contents."""
        from cmdop._generated.file_rpc.directory_pb2 import (
            FileListDirectoryRpcRequest,
        )

        request = FileListDirectoryRpcRequest(
            path=path,
            page_size=page_size,
            include_hidden=include_hidden,
        )
        if page_token:
            request.page_token = page_token

        response = await self._call_async(self._get_stub.FileListDirectory, request)

        entries = []
        for entry in response.result.entries:
            entries.append(
                FileEntry(
                    name=entry.name,
                    path=entry.path,
                    type=_parse_file_type(entry.type),
                    size=entry.size,
                    modified_at=_parse_timestamp(entry.modified_at),
                    is_hidden=entry.name.startswith("."),
                )
            )

        return ListDirectoryResponse(
            path=response.result.current_path,
            entries=entries,
            next_page_token=response.result.next_page_token or None,
            total_count=response.result.total_count,
        )

    async def read(self, path: str, offset: int = 0, limit: int = 0) -> bytes:
        """Read file contents."""
        from cmdop._generated.file_rpc.file_crud_pb2 import FileReadRpcRequest

        request = FileReadRpcRequest(path=path)
        response = await self._call_async(self._get_stub.FileRead, request)
        return response.result.content

    async def write(
        self,
        path: str,
        content: bytes | str,
        create_parents: bool = False,
        overwrite: bool = True,
    ) -> None:
        """Write file contents."""
        from cmdop._generated.file_rpc.file_crud_pb2 import FileWriteRpcRequest

        if isinstance(content, str):
            content = content.encode("utf-8")

        request = FileWriteRpcRequest(
            path=path,
            content=content,
            create_parents=create_parents,
        )
        await self._call_async(self._get_stub.FileWrite, request)

    async def delete(self, path: str, recursive: bool = False) -> None:
        """Delete file or directory."""
        from cmdop._generated.file_rpc.file_crud_pb2 import FileDeleteRpcRequest

        request = FileDeleteRpcRequest(path=path, recursive=recursive)
        await self._call_async(self._get_stub.FileDelete, request)

    async def copy(self, source: str, destination: str) -> None:
        """Copy file or directory."""
        from cmdop._generated.file_rpc.file_crud_pb2 import FileCopyRpcRequest

        request = FileCopyRpcRequest(
            source_path=source,
            destination_path=destination,
        )
        await self._call_async(self._get_stub.FileCopy, request)

    async def move(self, source: str, destination: str) -> None:
        """Move/rename file or directory."""
        from cmdop._generated.file_rpc.file_crud_pb2 import FileMoveRpcRequest

        request = FileMoveRpcRequest(
            source_path=source,
            destination_path=destination,
        )
        await self._call_async(self._get_stub.FileMove, request)

    async def info(self, path: str) -> FileInfo:
        """Get file information."""
        from cmdop._generated.file_rpc.file_crud_pb2 import FileGetInfoRpcRequest

        request = FileGetInfoRpcRequest(path=path)
        response = await self._call_async(self._get_stub.FileGetInfo, request)

        entry = response.result.entry
        return FileInfo(
            path=entry.path,
            type=_parse_file_type(entry.type),
            size=entry.size,
            modified_at=_parse_timestamp(entry.modified_at),
        )

    async def mkdir(self, path: str, create_parents: bool = True) -> None:
        """Create directory."""
        from cmdop._generated.file_rpc.file_crud_pb2 import (
            FileCreateDirectoryRpcRequest,
        )

        request = FileCreateDirectoryRpcRequest(
            path=path,
            create_parents=create_parents,
        )
        await self._call_async(self._get_stub.FileCreateDirectory, request)
