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
class GetLabelsForPageRequestPathParams(PathParams):
    id: int = api_field(REQ)


@dataclasses.dataclass(frozen=True)
class GetLabelsForPageRequestQueryParams(QueryParams):
    prefix: str = api_field(OPT)
    sort: str = api_field(OPT)
    cursor: str = api_field(OPT)
    limit: int = api_field(OPT)


@dataclasses.dataclass(frozen=True)
class GetLabelsForPageRequest(BaseRequest):
    """
    See: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-label/#api-pages-id-labels-get
    """

    path_params: GetLabelsForPageRequestPathParams = dataclasses.field(
        default_factory=GetLabelsForPageRequestPathParams
    )
    query_params: GetLabelsForPageRequestQueryParams = dataclasses.field(
        default_factory=GetLabelsForPageRequestQueryParams
    )

    @property
    def _path(self) -> str:
        return f"/pages/{self.path_params.id}/labels"

    def sync(self, client: Confluence) -> "GetLabelsForPageResponse":
        return self._sync_get(GetLabelsForPageResponse, client)


# ------------------------------------------------------------------------------
# Output
# ------------------------------------------------------------------------------
# --- Result item ---
@dataclasses.dataclass(frozen=True)
class GetLabelsForPageResponseResult(BaseResponse):
    """Label schema - represents a single label in the results array."""

    @cached_property
    def id(self) -> str:
        return self._get("id")

    @cached_property
    def name(self) -> str:
        return self._get("name")

    @cached_property
    def prefix(self) -> str:
        return self._get("prefix")


# --- Top level response ---
@dataclasses.dataclass(frozen=True)
class GetLabelsForPageResponse(BaseResponse):
    """MultiEntityResult<Label> schema - top level response."""

    @cached_property
    def results(self) -> list[GetLabelsForPageResponseResult]:
        return self._new_many(GetLabelsForPageResponseResult, "results")

    @cached_property
    def links(self) -> Links:
        return self._new(Links, "_links")
