"""Type stubs for VMLICENSE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .download import Download
    from .download_eval import DownloadEval
    from .upload import Upload


class Vmlicense:
    """Type stub for Vmlicense."""

    download: Download
    download_eval: DownloadEval
    upload: Upload

    def __init__(self, client: IHTTPClient) -> None: ...
