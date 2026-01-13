# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from functools import cached_property

from func_args.api import REQ, OPT

from ...client import Confluence

from ..model import api_field, BaseRequest, PathParams, BodyParams, BaseResponse


# ------------------------------------------------------------------------------
# Input
# ------------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class UpdatePageRequestPathParams(PathParams):
    id: int = api_field(REQ)


@dataclasses.dataclass(frozen=True)
class UpdatePageRequestBodyParams(BodyParams):
    id: str = api_field(REQ)
    status: str = api_field(REQ)
    title: str = api_field(REQ)
    body: T.Dict[str, T.Any] = api_field(REQ)
    version: T.Dict[str, T.Any] = api_field(REQ)
    space_id: str = api_field(OPT, "spaceId")
    parent_id: str = api_field(OPT, "parentId")
    owner_id: str = api_field(OPT, "ownerId")


@dataclasses.dataclass(frozen=True)
class UpdatePageRequest(BaseRequest):
    """
    See: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-put
    """

    path_params: UpdatePageRequestPathParams = dataclasses.field(
        default_factory=UpdatePageRequestPathParams
    )
    body_params: UpdatePageRequestBodyParams = dataclasses.field(
        default_factory=UpdatePageRequestBodyParams
    )

    @property
    def _path(self) -> str:
        return f"/pages/{self.path_params.id}"

    def sync(self, client: Confluence) -> "UpdatePageResponse":
        return self._sync_put(UpdatePageResponse, client)


# ------------------------------------------------------------------------------
# Output
# ------------------------------------------------------------------------------
# --- Deepest nested objects first ---
@dataclasses.dataclass(frozen=True)
class UpdatePageResponseBodyStorage(BaseResponse):
    """BodyType schema for storage representation."""

    @cached_property
    def representation(self) -> str:
        return self._get("representation")

    @cached_property
    def value(self) -> str:
        return self._get("value")


@dataclasses.dataclass(frozen=True)
class UpdatePageResponseBodyAtlasDocFormat(BaseResponse):
    """BodyType schema for atlas_doc_format representation."""

    @cached_property
    def representation(self) -> str:
        return self._get("representation")

    @cached_property
    def value(self) -> str:
        return self._get("value")


@dataclasses.dataclass(frozen=True)
class UpdatePageResponseBodyView(BaseResponse):
    """BodyType schema for view representation."""

    @cached_property
    def representation(self) -> str:
        return self._get("representation")

    @cached_property
    def value(self) -> str:
        return self._get("value")


@dataclasses.dataclass(frozen=True)
class UpdatePageResponseBody(BaseResponse):
    """BodySingle schema - contains fields for each representation type."""

    @cached_property
    def storage(self) -> UpdatePageResponseBodyStorage:
        return self._new(UpdatePageResponseBodyStorage, "storage")

    @cached_property
    def atlas_doc_format(self) -> UpdatePageResponseBodyAtlasDocFormat:
        return self._new(UpdatePageResponseBodyAtlasDocFormat, "atlas_doc_format")

    @cached_property
    def view(self) -> UpdatePageResponseBodyView:
        return self._new(UpdatePageResponseBodyView, "view")


@dataclasses.dataclass(frozen=True)
class UpdatePageResponseVersion(BaseResponse):
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
class UpdatePageResponseLinks(BaseResponse):
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
class UpdatePageResponse(BaseResponse):
    """PageSingle schema - response for updating a page."""

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
    def version(self) -> UpdatePageResponseVersion:
        return self._new(UpdatePageResponseVersion, "version")

    @cached_property
    def body(self) -> UpdatePageResponseBody:
        return self._new(UpdatePageResponseBody, "body")

    @cached_property
    def links(self) -> UpdatePageResponseLinks:
        return self._new(UpdatePageResponseLinks, "_links")
