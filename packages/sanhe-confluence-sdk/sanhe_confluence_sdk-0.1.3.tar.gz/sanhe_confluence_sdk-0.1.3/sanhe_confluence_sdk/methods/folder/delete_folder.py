# -*- coding: utf-8 -*-

import dataclasses

from func_args.api import REQ

from ...client import Confluence

from ..model import api_field, BaseRequest, PathParams, BaseResponse


# ------------------------------------------------------------------------------
# Input
# ------------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class DeleteFolderRequestPathParams(PathParams):
    id: int = api_field(REQ)


@dataclasses.dataclass(frozen=True)
class DeleteFolderRequest(BaseRequest):
    """
    See: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-folder/#api-folders-id-delete
    """

    path_params: DeleteFolderRequestPathParams = dataclasses.field(
        default_factory=DeleteFolderRequestPathParams
    )

    @property
    def _path(self) -> str:
        return f"/folders/{self.path_params.id}"

    def sync(self, client: Confluence) -> "DeleteFolderResponse":
        return self._sync_delete(DeleteFolderResponse, client)


# ------------------------------------------------------------------------------
# Output
# ------------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class DeleteFolderResponse(BaseResponse):
    """Response for deleting a folder."""

    pass
