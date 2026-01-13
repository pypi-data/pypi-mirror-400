# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from functools import cached_property

from func_args.api import REQ, OPT

from ...client import Confluence

from ..model import api_field, BaseRequest, QueryParams, BodyParams, BaseResponse


# ------------------------------------------------------------------------------
# Input
# ------------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class CreatePageRequestQueryParams(QueryParams):
    embedded: bool = api_field(OPT)
    private: bool = api_field(OPT)
    root_level: bool = api_field(OPT, "root-level")


@dataclasses.dataclass(frozen=True)
class CreatePageRequestBodyParams(BodyParams):
    space_id: str = api_field(REQ, "spaceId")
    status: str = api_field(OPT)
    title: str = api_field(OPT)
    parent_id: str = api_field(OPT, "parentId")
    body: T.Dict[str, T.Any] = api_field(OPT)
    subtype: str = api_field(OPT)


@dataclasses.dataclass(frozen=True)
class CreatePageRequest(BaseRequest):
    """
    See: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-post
    """

    query_params: CreatePageRequestQueryParams = dataclasses.field(
        default_factory=CreatePageRequestQueryParams
    )
    body_params: CreatePageRequestBodyParams = dataclasses.field(
        default_factory=CreatePageRequestBodyParams
    )

    @property
    def _path(self) -> str:
        return "/pages"

    def sync(self, client: Confluence) -> "CreatePageResponse":
        return self._sync_post(CreatePageResponse, client)


# ------------------------------------------------------------------------------
# Output
# ------------------------------------------------------------------------------
# --- Deepest nested objects first ---
@dataclasses.dataclass(frozen=True)
class CreatePageResponseBodyStorage(BaseResponse):
    """BodyType schema for storage representation."""

    @cached_property
    def representation(self) -> str:
        return self._get("representation")

    @cached_property
    def value(self) -> str:
        return self._get("value")


@dataclasses.dataclass(frozen=True)
class CreatePageResponseBodyAtlasDocFormat(BaseResponse):
    """BodyType schema for atlas_doc_format representation."""

    @cached_property
    def representation(self) -> str:
        return self._get("representation")

    @cached_property
    def value(self) -> str:
        return self._get("value")


@dataclasses.dataclass(frozen=True)
class CreatePageResponseBodyView(BaseResponse):
    """BodyType schema for view representation."""

    @cached_property
    def representation(self) -> str:
        return self._get("representation")

    @cached_property
    def value(self) -> str:
        return self._get("value")


@dataclasses.dataclass(frozen=True)
class CreatePageResponseBody(BaseResponse):
    """BodySingle schema - contains fields for each representation type."""

    @cached_property
    def storage(self) -> CreatePageResponseBodyStorage:
        return self._new(CreatePageResponseBodyStorage, "storage")

    @cached_property
    def atlas_doc_format(self) -> CreatePageResponseBodyAtlasDocFormat:
        return self._new(CreatePageResponseBodyAtlasDocFormat, "atlas_doc_format")

    @cached_property
    def view(self) -> CreatePageResponseBodyView:
        return self._new(CreatePageResponseBodyView, "view")


@dataclasses.dataclass(frozen=True)
class CreatePageResponseVersion(BaseResponse):
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
class CreatePageResponseLinks(BaseResponse):
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


# --- Main response object ---
@dataclasses.dataclass(frozen=True)
class CreatePageResponse(BaseResponse):
    """PageSingle schema - response for creating a page."""

    @cached_property
    def id(self) -> str:
        """ID of the page."""
        return self._get("id")

    @cached_property
    def status(self) -> str:
        """ContentStatus enum: current, draft, archived, historical, trashed, deleted."""
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
    def version(self) -> CreatePageResponseVersion:
        return self._new(CreatePageResponseVersion, "version")

    @cached_property
    def body(self) -> CreatePageResponseBody:
        return self._new(CreatePageResponseBody, "body")

    @cached_property
    def links(self) -> CreatePageResponseLinks:
        return self._new(CreatePageResponseLinks, "_links")
