import typing

from parfive import Downloader


class SpaceDataResultDownloadMixin:
    URL_KEY: str | typing.Callable[[object], str] | None = None

    async def download(
        self,
        folder_path: str,
        filename_fn: typing.Callable[[object], str] | None = None,
    ) -> Downloader:
        downloader = Downloader()

        if filename_fn is None:
            raise ValueError("Filename function is required for download")

        async for item in self:
            filename = filename_fn(item)
            if filename is None:
                continue

            if self.URL_KEY is None:
                raise ValueError("Download is not supported for this result type")

            if isinstance(self.URL_KEY, str):
                url = getattr(item, self.URL_KEY, None)
            else:
                url = self.URL_KEY(item)

            if url is None:
                continue

            downloader.enqueue_file(url=url, folder_path=folder_path, filename=filename)

        return downloader
