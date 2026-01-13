# -*- coding: utf-8 -*-

import dataclasses
from functools import cached_property

from func_args.api import REQ, OPT

from ...client import Confluence

from ..model import api_field, BaseRequest, PathParams, QueryParams, BaseResponse
from ..common.links import Links


# ------------------------------------------------------------------------------
# Input
# ------------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class GetFolderDirectChildrenRequestPathParams(PathParams):
    id: int = api_field(REQ)


@dataclasses.dataclass(frozen=True)
class GetFolderDirectChildrenRequestQueryParams(QueryParams):
    cursor: str = api_field(OPT)
    limit: int = api_field(OPT)
    sort: str = api_field(OPT)


@dataclasses.dataclass(frozen=True)
class GetFolderDirectChildrenRequest(BaseRequest):
    """
    See: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-children/#api-folders-id-direct-children-get
    """

    path_params: GetFolderDirectChildrenRequestPathParams = dataclasses.field(
        default_factory=GetFolderDirectChildrenRequestPathParams
    )
    query_params: GetFolderDirectChildrenRequestQueryParams = dataclasses.field(
        default_factory=GetFolderDirectChildrenRequestQueryParams
    )

    @property
    def _path(self) -> str:
        return f"/folders/{self.path_params.id}/direct-children"

    def sync(self, client: Confluence) -> "GetFolderDirectChildrenResponse":
        return self._sync_get(GetFolderDirectChildrenResponse, client)


# ------------------------------------------------------------------------------
# Output
# ------------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class GetFolderDirectChildrenResponseResult(BaseResponse):
    """ChildrenResponse schema - represents a single child in the results array."""

    @cached_property
    def id(self) -> str:
        """ID of the child content."""
        return self._get("id")

    @cached_property
    def status(self) -> str:
        """OnlyArchivedAndCurrentContentStatus enum: current, archived."""
        return self._get("status")

    @cached_property
    def title(self) -> str:
        """Title of the child content."""
        return self._get("title")

    @cached_property
    def type(self) -> str:
        """Hierarchical content type: database, embed, folder, page, whiteboard."""
        return self._get("type")

    @cached_property
    def spaceId(self) -> str:
        """ID of the space the content is in."""
        return self._get("spaceId")

    @cached_property
    def childPosition(self) -> int:
        """Numerical value indicating position relative to siblings."""
        return self._get("childPosition")


@dataclasses.dataclass(frozen=True)
class GetFolderDirectChildrenResponse(BaseResponse):
    """MultiEntityResult<ChildrenResponse> schema - top level response."""

    @cached_property
    def results(self) -> list[GetFolderDirectChildrenResponseResult]:
        return self._new_many(GetFolderDirectChildrenResponseResult, "results")

    @cached_property
    def links(self) -> Links:
        return self._new(Links, "_links")
