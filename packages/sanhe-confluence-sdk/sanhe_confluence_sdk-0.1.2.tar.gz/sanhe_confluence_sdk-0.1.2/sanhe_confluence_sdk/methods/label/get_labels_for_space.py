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
class GetLabelsForSpaceRequestPathParams(PathParams):
    id: int = api_field(REQ)


@dataclasses.dataclass(frozen=True)
class GetLabelsForSpaceRequestQueryParams(QueryParams):
    prefix: str = api_field(OPT)
    sort: str = api_field(OPT)
    cursor: str = api_field(OPT)
    limit: int = api_field(OPT)


@dataclasses.dataclass(frozen=True)
class GetLabelsForSpaceRequest(BaseRequest):
    """
    See: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-label/#api-spaces-id-labels-get
    """

    path_params: GetLabelsForSpaceRequestPathParams = dataclasses.field(
        default_factory=GetLabelsForSpaceRequestPathParams
    )
    query_params: GetLabelsForSpaceRequestQueryParams = dataclasses.field(
        default_factory=GetLabelsForSpaceRequestQueryParams
    )

    @property
    def _path(self) -> str:
        return f"/spaces/{self.path_params.id}/labels"

    def sync(self, client: Confluence) -> "GetLabelsForSpaceResponse":
        return self._sync_get(GetLabelsForSpaceResponse, client)


# ------------------------------------------------------------------------------
# Output
# ------------------------------------------------------------------------------
# --- Nested objects first ---
@dataclasses.dataclass(frozen=True)
class GetLabelsForSpaceResponseResult(BaseResponse):
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


# --- Top level response object ---
@dataclasses.dataclass(frozen=True)
class GetLabelsForSpaceResponse(BaseResponse):
    """MultiEntityResult<Label> schema - top level response."""

    @cached_property
    def results(self) -> list[GetLabelsForSpaceResponseResult]:
        return self._new_many(GetLabelsForSpaceResponseResult, "results")

    @cached_property
    def links(self) -> Links:
        return self._new(Links, "_links")
