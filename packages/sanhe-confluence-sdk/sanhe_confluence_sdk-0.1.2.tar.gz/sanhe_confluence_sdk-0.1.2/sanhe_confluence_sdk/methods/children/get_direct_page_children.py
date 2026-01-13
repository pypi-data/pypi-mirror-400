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
class GetDirectPageChildrenRequestPathParams(PathParams):
    id: int = api_field(REQ)


@dataclasses.dataclass(frozen=True)
class GetDirectPageChildrenRequestQueryParams(QueryParams):
    cursor: str = api_field(OPT)
    limit: int = api_field(OPT)
    sort: str = api_field(OPT)


@dataclasses.dataclass(frozen=True)
class GetDirectPageChildrenRequest(BaseRequest):
    """
    See: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-children/#api-pages-id-direct-children-get
    """

    path_params: GetDirectPageChildrenRequestPathParams = dataclasses.field(
        default_factory=GetDirectPageChildrenRequestPathParams
    )
    query_params: GetDirectPageChildrenRequestQueryParams = dataclasses.field(
        default_factory=GetDirectPageChildrenRequestQueryParams
    )

    @property
    def _path(self) -> str:
        return f"/pages/{self.path_params.id}/direct-children"

    def sync(self, client: Confluence) -> "GetDirectPageChildrenResponse":
        return self._sync_get(GetDirectPageChildrenResponse, client)


# ------------------------------------------------------------------------------
# Output
# ------------------------------------------------------------------------------
# --- Deepest nested objects first ---
@dataclasses.dataclass(frozen=True)
class GetDirectPageChildrenResponseResult(BaseResponse):
    """ChildrenResponse schema - represents a single direct child in the results array."""

    @cached_property
    def id(self) -> str:
        """ID of the child content."""
        return self._get("id")

    @cached_property
    def status(self) -> str:
        """ContentStatus enum: current, archived."""
        return self._get("status")

    @cached_property
    def title(self) -> str:
        """Title of the child content."""
        return self._get("title")

    @cached_property
    def type(self) -> str:
        """Content type: database, embed, folder, page, or whiteboard."""
        return self._get("type")

    @cached_property
    def spaceId(self) -> str:
        """ID of the space the content is in."""
        return self._get("spaceId")

    @cached_property
    def childPosition(self) -> int:
        """Ordinal position among siblings in content hierarchy."""
        return self._get("childPosition")


# --- Top level response objects ---
@dataclasses.dataclass(frozen=True)
class GetDirectPageChildrenResponse(BaseResponse):
    """MultiEntityResult<ChildrenResponse> schema - top level response."""

    @cached_property
    def results(self) -> list[GetDirectPageChildrenResponseResult]:
        return self._new_many(GetDirectPageChildrenResponseResult, "results")

    @cached_property
    def links(self) -> Links:
        return self._new(Links, "_links")
