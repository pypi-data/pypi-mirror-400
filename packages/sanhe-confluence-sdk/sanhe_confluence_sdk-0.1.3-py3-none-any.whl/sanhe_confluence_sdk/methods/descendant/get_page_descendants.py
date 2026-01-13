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
class GetPageDescendantsRequestPathParams(PathParams):
    id: int = api_field(REQ)


@dataclasses.dataclass(frozen=True)
class GetPageDescendantsRequestQueryParams(QueryParams):
    depth: int = api_field(OPT)
    limit: int = api_field(OPT)
    cursor: str = api_field(OPT)


@dataclasses.dataclass(frozen=True)
class GetPageDescendantsRequest(BaseRequest):
    """
    See: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-descendants/#api-pages-id-descendants-get
    """

    path_params: GetPageDescendantsRequestPathParams = dataclasses.field(
        default_factory=GetPageDescendantsRequestPathParams
    )
    query_params: GetPageDescendantsRequestQueryParams = dataclasses.field(
        default_factory=GetPageDescendantsRequestQueryParams
    )

    @property
    def _path(self) -> str:
        return f"/pages/{self.path_params.id}/descendants"

    def sync(self, client: Confluence) -> "GetPageDescendantsResponse":
        return self._sync_get(GetPageDescendantsResponse, client)


# ------------------------------------------------------------------------------
# Output
# ------------------------------------------------------------------------------
# --- Deepest nested objects first ---
@dataclasses.dataclass(frozen=True)
class GetPageDescendantsResponseResult(BaseResponse):
    """Descendant schema - represents a single descendant in the results array."""

    @cached_property
    def id(self) -> str:
        """ID of the descendant."""
        return self._get("id")

    @cached_property
    def status(self) -> str:
        """ContentStatus enum: current, archived."""
        return self._get("status")

    @cached_property
    def title(self) -> str:
        """Title of the descendant."""
        return self._get("title")

    @cached_property
    def type(self) -> str:
        """Content type: database, embed, folder, page, or whiteboard."""
        return self._get("type")

    @cached_property
    def parentId(self) -> str:
        """ID of the parent content."""
        return self._get("parentId")

    @cached_property
    def depth(self) -> int:
        """Nesting level relative to the requested page."""
        return self._get("depth")

    @cached_property
    def childPosition(self) -> int:
        """Ordinal position among siblings in content hierarchy."""
        return self._get("childPosition")


# --- Top level response objects ---
@dataclasses.dataclass(frozen=True)
class GetPageDescendantsResponse(BaseResponse):
    """DescendantsResponse schema - top level response."""

    @cached_property
    def results(self) -> list[GetPageDescendantsResponseResult]:
        return self._new_many(GetPageDescendantsResponseResult, "results")

    @cached_property
    def links(self) -> Links:
        return self._new(Links, "_links")
