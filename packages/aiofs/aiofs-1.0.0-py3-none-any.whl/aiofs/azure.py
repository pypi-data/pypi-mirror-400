"""Implementation of FileLike with azure blobs"""

import fnmatch
from dataclasses import dataclass
from typing import Self

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import BlobServiceClient as SyncBlobServiceClient
from azure.storage.blob.aio import BlobClient, BlobServiceClient

from . import FileLike, FileLikeSystem


@dataclass
class AzureContainerConfig:
    account_name: str
    account_key: str
    container_name: str
    protocol: str = "https"
    host: str = "core.windows.net"
    port: int = 443

    @property
    def connection_string(self) -> str:
        """Dynamically generates the Azure Storage Connection String"""
        if self.host == "core.windows.net":
            return (
                f"DefaultEndpointsProtocol={self.protocol};"
                f"AccountName={self.account_name};"
                f"AccountKey={self.account_key};"
                f"EndpointSuffix={self.host}"
            )

        return (
            "AccountName=devstoreaccount1;"
            "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/"
            "K1SZFPTOtr/KBHBeksoGMGw==;"
            "DefaultEndpointsProtocol=http;"
            f"BlobEndpoint=http://{self.host}:{self.port}/devstoreaccount1;"
        )


class AzFileLike(FileLike):
    """Implementation of FileLike in azure blobs"""

    def __init__(self, blob: BlobClient, mode: str = "r"):
        self._blob = blob
        self._lease = None
        self._content = b""
        self._mode = mode
        self._lease = None
        self._context = None

    async def __aenter__(self) -> Self:
        self._context = self._blob = await self._blob.__aenter__()
        if "w" in self._mode or "r+" in self._mode:
            try:
                self._lease = await self._blob.acquire_lease(15)
            except ResourceNotFoundError:
                ...
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._blob.__aexit__(exc_type, exc, tb)

        try:
            if self._content:
                await self._blob.upload_blob(
                    self._content, overwrite=True, lease=self._lease
                )
        except ResourceExistsError:
            raise BlockingIOError(f"")
        finally:
            if self._lease:
                await self._lease.release()

    async def read(self, size: int = -1) -> bytes:
        if not self._context:
            raise RuntimeError('Call to "read" out of context')
        if size >= 0:
            raise NotImplementedError("Not designed to donwload partially")

        try:
            stream = await self._blob.download_blob()
        except ResourceNotFoundError:
            raise FileNotFoundError(f"Not found {self._blob.blob_name}")
        return await stream.readall()

    async def write(self, b: bytes):
        if not self._context:
            raise RuntimeError('Call to "write" out of context')
        self._content += b


class AzFileSystem(FileLikeSystem):
    """Create and manage AzFileLike"""

    def __init__(
        self,
        config: AzureContainerConfig,
        file_pattern: str = "*",
    ):
        self._config = config
        self._service = BlobServiceClient.from_connection_string(
            config.connection_string
        )
        self._container = None

        self._pattern = file_pattern

    def _load_container(self):
        with SyncBlobServiceClient.from_connection_string(
            self._config.connection_string
        ) as service:
            if not service.get_container_client(self._config.container_name).exists():
                service.create_container(self._config.container_name)
        return self._service.get_container_client(self._config.container_name)

    def open(self, filename: str, mode="r") -> AzFileLike:
        if not self._container:
            self._container = self._load_container()

        blob_name = self._pattern.replace("*", filename)
        blob = self._container.get_blob_client(blob_name)

        return AzFileLike(blob, mode)

    async def rm(self, pattern: str):
        if not self._container:
            self._container = self._load_container()

        filenames = await self.ls(pattern)
        for fn in filenames:
            blob_name = self._pattern.replace("*", fn)
            blob = self._container.get_blob_client(blob_name)
            try:
                await blob.delete_blob()
            except ResourceNotFoundError:
                pass

    async def close(self):
        if self._container:
            await self._container.close()
        await self._service.close()

    async def ls(self, pattern: str = "*"):
        """List all filenames of the system"""
        if not self._container:
            self._container = self._load_container()

        prefix, _, sufix = self._pattern.partition("*")
        names = []
        prefix = prefix if prefix else None
        pre = 0 if prefix is None else len(prefix)
        suf = -len(sufix) if sufix else None
        async for blob in self._container.list_blobs(prefix):
            if blob.name.endswith(sufix):
                names.append(blob.name[pre:suf])
        return fnmatch.filter(names, pattern)
