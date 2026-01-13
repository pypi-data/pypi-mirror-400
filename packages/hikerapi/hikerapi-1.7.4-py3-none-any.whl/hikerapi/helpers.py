import httpx
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict, List, Optional, Union


class HelperMixin:

    def media_likers(
        self,
        media_id: str,
        page_id: Optional[str] = None,
        count: Optional[int] = None,
        container: Optional[List[Dict]] = None,
        max_requests: Optional[int] = None,
    ) -> List[Dict]:
        """Get likers on media"""
        params = {"media_id": media_id, "end_cursor": page_id}
        return self._paging_request(
            "/gql/media/likers/chunk",
            params=params,
            count=count,
            container=container,
            page_key="end_cursor",
            max_requests=max_requests,
        )

    def user_followers(
        self,
        user_id: Optional[str] = None,
        page_id: Optional[str] = None,
        count: Optional[int] = None,
        container: Optional[List[Dict]] = None,
        max_requests: Optional[int] = None,
    ) -> List[Dict]:
        """Get a user followers (one request required). Get part (one page) of followers users with cursor"""
        params = {"user_id": user_id, "page_id": page_id}
        return self._paging_request(
            "/v2/user/followers",
            params=params,
            count=count,
            container=container,
            max_requests=max_requests,
        )

    def save_media(self, url: str, folder: Optional[str] = None) -> Union[Path | str]:
        response = httpx.get(url)
        response.raise_for_status()
        if folder:
            fname = urlparse(url).path.rsplit("/", 1)[1]
            path = Path(folder) / fname
            with open(path, "wb") as f:
                f.write(response.content)
            return path.resolve()
        return response.content

    def save_photo_by_id(
        self, media_id: str, folder: Optional[str] = None
    ) -> Union[Path | str]:
        url = self.media_by_id_v1(id=media_id)["thumbnail_url"]
        return self.save_media(url, folder=folder)

    def save_video_by_id(
        self, media_id: str, folder: Optional[str] = None
    ) -> Union[Path | str]:
        url = self.media_by_id_v1(id=media_id)["video_url"]
        return self.save_media(url, folder=folder)

    def save_photo_by_url(
        self, media_url: str, folder: Optional[str] = None
    ) -> Union[Path | str]:
        url = self.media_by_url_v1(url=media_url)["thumbnail_url"]
        return self.save_media(url, folder=folder)

    def save_video_by_url(
        self, media_url: str, folder: Optional[str] = None
    ) -> Union[Path | str]:
        url = self.media_by_url_v1(url=media_url)["video_url"]
        return self.save_media(url, folder=folder)


class AsyncHelperMixin:

    async def media_likers(
        self,
        media_id: str,
        page_id: Optional[str] = None,
        count: Optional[int] = None,
        container: Optional[List[Dict]] = None,
        max_requests: Optional[int] = None,
    ) -> List[Dict]:
        """Get likers on media"""
        params = {"media_id": media_id, "end_cursor": page_id}
        return await self._paging_request(
            "/gql/media/likers/chunk",
            params=params,
            count=count,
            container=container,
            page_key="end_cursor",
            max_requests=max_requests,
        )

    async def user_followers(
        self,
        user_id: Optional[str] = None,
        page_id: Optional[str] = None,
        count: Optional[int] = None,
        container: Optional[List[Dict]] = None,
        max_requests: Optional[int] = None,
    ) -> List[Dict]:
        """Get a user followers (one request required). Get part (one page) of followers users with cursor"""
        params = {"user_id": user_id, "page_id": page_id}
        return await self._paging_request(
            "/v2/user/followers",
            params=params,
            count=count,
            container=container,
            max_requests=max_requests,
        )

    async def save_media(url: str, folder: Optional[str] = None) -> Union[Path | str]:
        async with httpx.AsyncClient() as client:
            response = client.get(url)
            response.raise_for_status()
            if folder:
                fname = urlparse(url).path.rsplit("/", 1)[1]
                path = Path(folder) / fname
                with open(path, "wb") as f:
                    f.write(response.content)
                return path.resolve()
            return response.content

    async def save_photo_by_id(
        self, media_id: str, folder: Optional[str] = None
    ) -> Union[Path | str]:
        url = await self.media_by_id_v1(id=media_id)["thumbnail_url"]
        return await self.save_media(url, folder=folder)

    async def save_video_by_id(
        self, media_id: str, folder: Optional[str] = None
    ) -> Union[Path | str]:
        url = await self.media_by_id_v1(id=media_id)["video_url"]
        return await self.save_media(url, folder=folder)

    async def save_photo_by_url(
        self, media_url: str, folder: Optional[str] = None
    ) -> Union[Path | str]:
        url = await self.media_by_url_v1(url=media_url)["thumbnail_url"]
        return await self.save_media(url, folder=folder)

    async def save_video_by_url(
        self, media_url: str, folder: Optional[str] = None
    ) -> Union[Path | str]:
        url = await self.media_by_url_v1(url=media_url)["video_url"]
        return await self.save_media(url, folder=folder)
