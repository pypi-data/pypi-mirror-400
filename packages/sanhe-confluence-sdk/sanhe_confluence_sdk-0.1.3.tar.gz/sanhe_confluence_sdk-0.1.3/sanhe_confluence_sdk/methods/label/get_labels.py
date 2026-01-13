# -*- coding: utf-8 -*-

import dataclasses
from functools import cached_property

from func_args.api import OPT

from ...client import Confluence

from ..model import api_field, BaseRequest, QueryParams, BaseResponse
from ..common.links import Links


# ------------------------------------------------------------------------------
# Input
# ------------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class GetLabelsRequestQueryParams(QueryParams):
    label_id: list[int] = api_field(OPT, "label-id")
    prefix: list[str] = api_field(OPT)
    cursor: str = api_field(OPT)
    sort: str = api_field(OPT)
    limit: int = api_field(OPT)


@dataclasses.dataclass(frozen=True)
class GetLabelsRequest(BaseRequest):
    """
    See: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-label/#api-labels-get
    """

    query_params: GetLabelsRequestQueryParams = dataclasses.field(
        default_factory=GetLabelsRequestQueryParams
    )

    @property
    def _path(self) -> str:
        return "/labels"

    def sync(self, client: Confluence) -> "GetLabelsResponse":
        return self._sync_get(GetLabelsResponse, client)


# ------------------------------------------------------------------------------
# Output
# ------------------------------------------------------------------------------
# --- Result item ---
@dataclasses.dataclass(frozen=True)
class GetLabelsResponseResult(BaseResponse):
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
class GetLabelsResponse(BaseResponse):
    """MultiEntityResult<Label> schema - top level response."""

    @cached_property
    def results(self) -> list[GetLabelsResponseResult]:
        return self._new_many(GetLabelsResponseResult, "results")

    @cached_property
    def links(self) -> Links:
        return self._new(Links, "_links")
