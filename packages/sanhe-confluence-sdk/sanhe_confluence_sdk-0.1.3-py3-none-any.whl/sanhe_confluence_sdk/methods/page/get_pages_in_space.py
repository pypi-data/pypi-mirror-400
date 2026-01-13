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
class GetPagesInSpaceRequestPathParams(PathParams):
    id: int = api_field(REQ)


@dataclasses.dataclass(frozen=True)
class GetPagesInSpaceRequestQueryParams(QueryParams):
    depth: str = api_field(OPT)
    sort: str = api_field(OPT)
    status: list[str] = api_field(OPT)
    title: str = api_field(OPT)
    body_format: str = api_field(OPT, "body-format")
    cursor: str = api_field(OPT)
    limit: int = api_field(OPT)


@dataclasses.dataclass(frozen=True)
class GetPagesInSpaceRequest(BaseRequest):
    """
    See: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-spaces-id-pages-get
    """

    path_params: GetPagesInSpaceRequestPathParams = dataclasses.field(
        default_factory=GetPagesInSpaceRequestPathParams
    )
    query_params: GetPagesInSpaceRequestQueryParams = dataclasses.field(
        default_factory=GetPagesInSpaceRequestQueryParams
    )

    @property
    def _path(self) -> str:
        return f"/spaces/{self.path_params.id}/pages"

    def sync(self, client: Confluence) -> "GetPagesInSpaceResponse":
        return self._sync_get(GetPagesInSpaceResponse, client)


# ------------------------------------------------------------------------------
# Output
# ------------------------------------------------------------------------------
# --- Deepest nested objects first ---
@dataclasses.dataclass(frozen=True)
class GetPagesInSpaceResponseResultBodyStorage(BaseResponse):
    """BodyType schema for storage representation."""

    @cached_property
    def representation(self) -> str:
        return self._get("representation")

    @cached_property
    def value(self) -> str:
        return self._get("value")


@dataclasses.dataclass(frozen=True)
class GetPagesInSpaceResponseResultBodyAtlasDocFormat(BaseResponse):
    """BodyType schema for atlas_doc_format representation."""

    @cached_property
    def representation(self) -> str:
        return self._get("representation")

    @cached_property
    def value(self) -> str:
        return self._get("value")


@dataclasses.dataclass(frozen=True)
class GetPagesInSpaceResponseResultBody(BaseResponse):
    """BodyBulk schema - contains fields for each representation type requested."""

    @cached_property
    def storage(self) -> GetPagesInSpaceResponseResultBodyStorage:
        return self._new(GetPagesInSpaceResponseResultBodyStorage, "storage")

    @cached_property
    def atlas_doc_format(self) -> GetPagesInSpaceResponseResultBodyAtlasDocFormat:
        return self._new(GetPagesInSpaceResponseResultBodyAtlasDocFormat, "atlas_doc_format")


@dataclasses.dataclass(frozen=True)
class GetPagesInSpaceResponseResultVersion(BaseResponse):
    """Version schema."""

    @cached_property
    def createdAt(self) -> str:
        """Date and time when the version was created. ISO 8601 format."""
        return self._get("createdAt")

    @cached_property
    def message(self) -> str:
        """Message associated with the current version."""
        return self._get("message")

    @cached_property
    def number(self) -> int:
        """The version number."""
        return self._get("number")

    @cached_property
    def minorEdit(self) -> bool:
        """Describes if this version is a minor version."""
        return self._get("minorEdit")

    @cached_property
    def authorId(self) -> str:
        """The account ID of the user who created this version."""
        return self._get("authorId")


@dataclasses.dataclass(frozen=True)
class GetPagesInSpaceResponseResultLinks(BaseResponse):
    """AbstractPageLinks schema."""

    @cached_property
    def webui(self) -> str:
        """Web UI link of the content."""
        return self._get("webui")

    @cached_property
    def editui(self) -> str:
        """Edit UI link of the content."""
        return self._get("editui")

    @cached_property
    def tinyui(self) -> str:
        """Tiny UI link of the content."""
        return self._get("tinyui")


# --- Main result object ---
@dataclasses.dataclass(frozen=True)
class GetPagesInSpaceResponseResult(BaseResponse):
    """PageBulk schema - represents a single page in the results array."""

    @cached_property
    def id(self) -> str:
        """ID of the page."""
        return self._get("id")

    @cached_property
    def status(self) -> str:
        """ContentStatus enum: current, draft, archived, historical, trashed, deleted, any."""
        return self._get("status")

    @cached_property
    def title(self) -> str:
        """Title of the page."""
        return self._get("title")

    @cached_property
    def spaceId(self) -> str:
        """ID of the space the page is in."""
        return self._get("spaceId")

    @cached_property
    def parentId(self) -> str:
        """ID of the parent page, or null if there is no parent page."""
        return self._get("parentId")

    @cached_property
    def parentType(self) -> str:
        """ParentContentType enum: page, whiteboard, database, embed, folder."""
        return self._get("parentType")

    @cached_property
    def position(self) -> int:
        """Position of child page within the given parent page tree."""
        return self._get("position")

    @cached_property
    def authorId(self) -> str:
        """The account ID of the user who created this page originally."""
        return self._get("authorId")

    @cached_property
    def ownerId(self) -> str:
        """The account ID of the user who owns this page."""
        return self._get("ownerId")

    @cached_property
    def lastOwnerId(self) -> str:
        """The account ID of the user who owned this page previously, or null."""
        return self._get("lastOwnerId")

    @cached_property
    def subtype(self) -> str:
        """The subtype of the page."""
        return self._get("subtype")

    @cached_property
    def createdAt(self) -> str:
        """Date and time when the page was created. ISO 8601 format."""
        return self._get("createdAt")

    @cached_property
    def version(self) -> GetPagesInSpaceResponseResultVersion:
        return self._new(GetPagesInSpaceResponseResultVersion, "version")

    @cached_property
    def body(self) -> GetPagesInSpaceResponseResultBody:
        return self._new(GetPagesInSpaceResponseResultBody, "body")

    @cached_property
    def links(self) -> GetPagesInSpaceResponseResultLinks:
        return self._new(GetPagesInSpaceResponseResultLinks, "_links")


# --- Top level response objects ---
@dataclasses.dataclass(frozen=True)
class GetPagesInSpaceResponse(BaseResponse):
    """MultiEntityResult<PageBulk> schema - top level response."""

    @cached_property
    def results(self) -> list[GetPagesInSpaceResponseResult]:
        return self._new_many(GetPagesInSpaceResponseResult, "results")

    @cached_property
    def links(self) -> Links:
        return self._new(Links, "_links")
