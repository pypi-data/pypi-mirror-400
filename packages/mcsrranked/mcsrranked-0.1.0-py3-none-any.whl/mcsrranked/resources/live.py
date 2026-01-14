from __future__ import annotations

from typing import TYPE_CHECKING

from mcsrranked.types.live import LiveData

if TYPE_CHECKING:
    from mcsrranked._base_client import AsyncAPIClient, SyncAPIClient

__all__ = ["Live", "AsyncLive"]


class Live:
    """Synchronous live resource."""

    def __init__(self, client: SyncAPIClient) -> None:
        self._client = client

    def get(self) -> LiveData:
        """Get online players count and live stream matches.

        Returns:
            Live data including player count and active streams.
        """
        data = self._client.get("/live")
        return LiveData.model_validate(data["data"])


class AsyncLive:
    """Asynchronous live resource."""

    def __init__(self, client: AsyncAPIClient) -> None:
        self._client = client

    async def get(self) -> LiveData:
        """Get online players count and live stream matches.

        Returns:
            Live data including player count and active streams.
        """
        data = await self._client.get("/live")
        return LiveData.model_validate(data["data"])
