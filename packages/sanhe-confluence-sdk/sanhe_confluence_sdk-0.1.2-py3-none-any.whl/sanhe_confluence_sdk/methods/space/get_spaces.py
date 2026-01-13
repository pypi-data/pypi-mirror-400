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
class GetSpacesRequestQueryParams(QueryParams):
    ids: list[int] = api_field(OPT)
    keys: list[str] = api_field(OPT)
    type: str = api_field(OPT)
    status: str = api_field(OPT)
    labels: list[str] = api_field(OPT)
    favorited_by: str = api_field(OPT, "favorited-by")
    not_favorited_by: str = api_field(OPT, "not-favorited-by")
    sort: str = api_field(OPT)
    description_format: str = api_field(OPT, "description-format")
    include_icon: bool = api_field(OPT, "include-icon")
    cursor: str = api_field(OPT)
    limit: int = api_field(OPT)


@dataclasses.dataclass(frozen=True)
class GetSpacesRequest(BaseRequest):
    """
    See: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-space/#api-spaces-get
    """

    query_params: GetSpacesRequestQueryParams = dataclasses.field(
        default_factory=GetSpacesRequestQueryParams
    )

    @property
    def _path(self) -> str:
        return "/spaces"

    def sync(self, client: Confluence) -> "GetSpacesResponse":
        return self._sync_get(GetSpacesResponse, client)


# ------------------------------------------------------------------------------
# Output
# ------------------------------------------------------------------------------
# --- Deepest nested objects first ---
@dataclasses.dataclass(frozen=True)
class GetSpacesResponseResultDescriptionPlain(BaseResponse):
    """BodyType schema for plain text representation."""

    @cached_property
    def representation(self) -> str:
        return self._get("representation")

    @cached_property
    def value(self) -> str:
        return self._get("value")


@dataclasses.dataclass(frozen=True)
class GetSpacesResponseResultDescriptionView(BaseResponse):
    """BodyType schema for view (HTML) representation."""

    @cached_property
    def representation(self) -> str:
        return self._get("representation")

    @cached_property
    def value(self) -> str:
        return self._get("value")


@dataclasses.dataclass(frozen=True)
class GetSpacesResponseResultDescription(BaseResponse):
    """SpaceDescription schema."""

    @cached_property
    def plain(self) -> GetSpacesResponseResultDescriptionPlain:
        return self._new(GetSpacesResponseResultDescriptionPlain, "plain")

    @cached_property
    def view(self) -> GetSpacesResponseResultDescriptionView:
        return self._new(GetSpacesResponseResultDescriptionView, "view")


@dataclasses.dataclass(frozen=True)
class GetSpacesResponseResultIcon(BaseResponse):
    """SpaceIcon schema."""

    @cached_property
    def path(self) -> str:
        return self._get("path")

    @cached_property
    def apiDownloadLink(self) -> str:
        return self._get("apiDownloadLink")


@dataclasses.dataclass(frozen=True)
class GetSpacesResponseResultLinks(BaseResponse):
    """SpaceLinks schema."""

    @cached_property
    def webui(self) -> str:
        return self._get("webui")


# --- Main result object ---
@dataclasses.dataclass(frozen=True)
class GetSpacesResponseResult(BaseResponse):
    """SpaceBulk schema - represents a single space in the results array."""

    @cached_property
    def id(self) -> str:
        return self._get("id")

    @cached_property
    def key(self) -> str:
        return self._get("key")

    @cached_property
    def name(self) -> str:
        return self._get("name")

    @cached_property
    def type(self) -> str:
        """SpaceType enum: global, collaboration, knowledge_base, personal, etc."""
        return self._get("type")

    @cached_property
    def status(self) -> str:
        """SpaceStatus enum: current, archived."""
        return self._get("status")

    @cached_property
    def authorId(self) -> str:
        return self._get("authorId")

    @cached_property
    def currentActiveAlias(self) -> str:
        return self._get("currentActiveAlias")

    @cached_property
    def createdAt(self) -> str:
        """ISO 8601 date-time string."""
        return self._get("createdAt")

    @cached_property
    def homepageId(self) -> str:
        return self._get("homepageId")

    @cached_property
    def description(self) -> GetSpacesResponseResultDescription:
        return self._new(GetSpacesResponseResultDescription, "description")

    @cached_property
    def icon(self) -> GetSpacesResponseResultIcon:
        return self._new(GetSpacesResponseResultIcon, "icon")

    @cached_property
    def links(self) -> GetSpacesResponseResultLinks:
        return self._new(GetSpacesResponseResultLinks, "_links")


# --- Top level response objects ---
@dataclasses.dataclass(frozen=True)
class GetSpacesResponse(BaseResponse):
    """MultiEntityResult<SpaceBulk> schema - top level response."""

    @cached_property
    def results(self) -> list[GetSpacesResponseResult]:
        return self._new_many(GetSpacesResponseResult, "results")

    @cached_property
    def links(self) -> Links:
        return self._new(Links, "_links")
