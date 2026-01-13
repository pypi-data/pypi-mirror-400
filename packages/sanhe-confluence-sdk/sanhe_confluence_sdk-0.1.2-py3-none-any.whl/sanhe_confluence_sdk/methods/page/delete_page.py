# -*- coding: utf-8 -*-

import dataclasses

from httpx import Response
from func_args.api import REQ, OPT

from ...client import Confluence

from ..model import api_field, BaseRequest, PathParams, QueryParams, BaseResponse


# ------------------------------------------------------------------------------
# Input
# ------------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class DeletePageRequestPathParams(PathParams):
    id: int = api_field(REQ)


@dataclasses.dataclass(frozen=True)
class DeletePageRequestQueryParams(QueryParams):
    purge: bool = api_field(OPT)
    draft: bool = api_field(OPT)


@dataclasses.dataclass(frozen=True)
class DeletePageRequest(BaseRequest):
    """
    See: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-delete
    """

    path_params: DeletePageRequestPathParams = dataclasses.field(
        default_factory=DeletePageRequestPathParams
    )
    query_params: DeletePageRequestQueryParams = dataclasses.field(
        default_factory=DeletePageRequestQueryParams
    )

    @property
    def _path(self) -> str:
        return f"/pages/{self.path_params.id}"

    def sync(self, client: Confluence) -> Response:
        """
        Execute the DELETE request.

        Returns the httpx.Response object. A successful deletion returns
        status code 204 (No Content).
        """
        return self._sync_delete(DeletePageResponse, client)


# ------------------------------------------------------------------------------
# Output
# ------------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class DeletePageResponse(BaseResponse):
    """response for deleting a page."""
