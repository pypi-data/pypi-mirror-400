# -*- coding: utf-8 -*-

import dataclasses
from functools import cached_property

from func_args.api import REQ, OPT

from ...client import Confluence

from ..model import api_field, BaseRequest, PathParams, QueryParams, BaseResponse


# ------------------------------------------------------------------------------
# Input
# ------------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class GetFolderRequestPathParams(PathParams):
    id: int = api_field(REQ)


@dataclasses.dataclass(frozen=True)
class GetFolderRequestQueryParams(QueryParams):
    include_collaborators: bool = api_field(OPT, "include-collaborators")
    include_direct_children: bool = api_field(OPT, "include-direct-children")
    include_operations: bool = api_field(OPT, "include-operations")
    include_properties: bool = api_field(OPT, "include-properties")


@dataclasses.dataclass(frozen=True)
class GetFolderRequest(BaseRequest):
    """
    See: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-folder/#api-folders-id-get
    """

    path_params: GetFolderRequestPathParams = dataclasses.field(
        default_factory=GetFolderRequestPathParams
    )
    query_params: GetFolderRequestQueryParams = dataclasses.field(
        default_factory=GetFolderRequestQueryParams
    )

    @property
    def _path(self) -> str:
        return f"/folders/{self.path_params.id}"

    def sync(self, client: Confluence) -> "GetFolderResponse":
        return self._sync_get(GetFolderResponse, client)


# ------------------------------------------------------------------------------
# Output
# ------------------------------------------------------------------------------
# --- Deepest nested objects first ---
@dataclasses.dataclass(frozen=True)
class GetFolderResponseVersion(BaseResponse):
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
class GetFolderResponseLinks(BaseResponse):
    """FolderLinks schema."""

    @cached_property
    def webui(self) -> str:
        """Web UI link of the content."""
        return self._get("webui")


# --- Optional nested objects for expanded fields ---
@dataclasses.dataclass(frozen=True)
class GetFolderResponseOperation(BaseResponse):
    """Operation schema."""

    @cached_property
    def operation(self) -> str:
        return self._get("operation")

    @cached_property
    def targetType(self) -> str:
        return self._get("targetType")


@dataclasses.dataclass(frozen=True)
class GetFolderResponseOperationsLinks(BaseResponse):
    """Links for operations pagination."""

    @cached_property
    def self_(self) -> str:
        return self._get("self")


@dataclasses.dataclass(frozen=True)
class GetFolderResponseOperationsMeta(BaseResponse):
    """Meta information for operations pagination."""

    @cached_property
    def hasMore(self) -> bool:
        return self._get("hasMore")

    @cached_property
    def cursor(self) -> str:
        return self._get("cursor")


@dataclasses.dataclass(frozen=True)
class GetFolderResponseOperations(BaseResponse):
    """Container for folder operations with pagination."""

    @cached_property
    def results(self) -> list[GetFolderResponseOperation]:
        return self._new_many(GetFolderResponseOperation, "results")

    @cached_property
    def meta(self) -> GetFolderResponseOperationsMeta:
        return self._new(GetFolderResponseOperationsMeta, "meta")

    @cached_property
    def links(self) -> GetFolderResponseOperationsLinks:
        return self._new(GetFolderResponseOperationsLinks, "_links")


@dataclasses.dataclass(frozen=True)
class GetFolderResponsePropertyVersion(BaseResponse):
    """Version schema for content property."""

    @cached_property
    def createdAt(self) -> str:
        return self._get("createdAt")

    @cached_property
    def message(self) -> str:
        return self._get("message")

    @cached_property
    def number(self) -> int:
        return self._get("number")

    @cached_property
    def minorEdit(self) -> bool:
        return self._get("minorEdit")

    @cached_property
    def authorId(self) -> str:
        return self._get("authorId")


@dataclasses.dataclass(frozen=True)
class GetFolderResponseProperty(BaseResponse):
    """ContentProperty schema."""

    @cached_property
    def id(self) -> str:
        return self._get("id")

    @cached_property
    def key(self) -> str:
        return self._get("key")

    @cached_property
    def value(self) -> str:
        """Value stored as JSON string."""
        return self._get("value")

    @cached_property
    def version(self) -> GetFolderResponsePropertyVersion:
        return self._new(GetFolderResponsePropertyVersion, "version")


@dataclasses.dataclass(frozen=True)
class GetFolderResponsePropertiesLinks(BaseResponse):
    """Links for properties pagination."""

    @cached_property
    def self_(self) -> str:
        return self._get("self")


@dataclasses.dataclass(frozen=True)
class GetFolderResponsePropertiesMeta(BaseResponse):
    """Meta information for properties pagination."""

    @cached_property
    def hasMore(self) -> bool:
        return self._get("hasMore")

    @cached_property
    def cursor(self) -> str:
        return self._get("cursor")


@dataclasses.dataclass(frozen=True)
class GetFolderResponseProperties(BaseResponse):
    """Container for folder properties with pagination."""

    @cached_property
    def results(self) -> list[GetFolderResponseProperty]:
        return self._new_many(GetFolderResponseProperty, "results")

    @cached_property
    def meta(self) -> GetFolderResponsePropertiesMeta:
        return self._new(GetFolderResponsePropertiesMeta, "meta")

    @cached_property
    def links(self) -> GetFolderResponsePropertiesLinks:
        return self._new(GetFolderResponsePropertiesLinks, "_links")


@dataclasses.dataclass(frozen=True)
class GetFolderResponseChild(BaseResponse):
    """ChildrenResponse schema."""

    @cached_property
    def id(self) -> str:
        return self._get("id")

    @cached_property
    def status(self) -> str:
        return self._get("status")

    @cached_property
    def title(self) -> str:
        return self._get("title")

    @cached_property
    def type(self) -> str:
        """Hierarchical content type (database/embed/folder/page/whiteboard)."""
        return self._get("type")

    @cached_property
    def spaceId(self) -> str:
        return self._get("spaceId")

    @cached_property
    def childPosition(self) -> int:
        """Position relative to siblings within the content tree."""
        return self._get("childPosition")


@dataclasses.dataclass(frozen=True)
class GetFolderResponseDirectChildrenLinks(BaseResponse):
    """Links for direct children pagination."""

    @cached_property
    def self_(self) -> str:
        return self._get("self")


@dataclasses.dataclass(frozen=True)
class GetFolderResponseDirectChildrenMeta(BaseResponse):
    """Meta information for direct children pagination."""

    @cached_property
    def hasMore(self) -> bool:
        return self._get("hasMore")

    @cached_property
    def cursor(self) -> str:
        return self._get("cursor")


@dataclasses.dataclass(frozen=True)
class GetFolderResponseDirectChildren(BaseResponse):
    """Container for folder direct children with pagination."""

    @cached_property
    def results(self) -> list[GetFolderResponseChild]:
        return self._new_many(GetFolderResponseChild, "results")

    @cached_property
    def meta(self) -> GetFolderResponseDirectChildrenMeta:
        return self._new(GetFolderResponseDirectChildrenMeta, "meta")

    @cached_property
    def links(self) -> GetFolderResponseDirectChildrenLinks:
        return self._new(GetFolderResponseDirectChildrenLinks, "_links")


# --- Main response object ---
@dataclasses.dataclass(frozen=True)
class GetFolderResponse(BaseResponse):
    """FolderSingle schema - response for getting a single folder by ID."""

    @cached_property
    def id(self) -> str:
        """ID of the folder."""
        return self._get("id")

    @cached_property
    def type(self) -> str:
        """The content type of the object."""
        return self._get("type")

    @cached_property
    def status(self) -> str:
        """ContentStatus enum: current, archived, deleted, trashed."""
        return self._get("status")

    @cached_property
    def title(self) -> str:
        """Title of the folder."""
        return self._get("title")

    @cached_property
    def parentId(self) -> str:
        """ID of the parent content, or null if there is no parent."""
        return self._get("parentId")

    @cached_property
    def parentType(self) -> str:
        """ParentContentType enum: page, whiteboard, database, embed, folder."""
        return self._get("parentType")

    @cached_property
    def position(self) -> int:
        """Position within parent tree."""
        return self._get("position")

    @cached_property
    def authorId(self) -> str:
        """The account ID of the user who created this folder."""
        return self._get("authorId")

    @cached_property
    def ownerId(self) -> str:
        """The account ID of the user who owns this folder."""
        return self._get("ownerId")

    @cached_property
    def createdAt(self) -> str:
        """Date and time when the folder was created. ISO 8601 format."""
        return self._get("createdAt")

    @cached_property
    def spaceId(self) -> str:
        """ID of the space the folder is in."""
        return self._get("spaceId")

    @cached_property
    def version(self) -> GetFolderResponseVersion:
        return self._new(GetFolderResponseVersion, "version")

    @cached_property
    def operations(self) -> GetFolderResponseOperations:
        """Available when include_operations=True."""
        return self._new(GetFolderResponseOperations, "operations")

    @cached_property
    def properties(self) -> GetFolderResponseProperties:
        """Available when include_properties=True."""
        return self._new(GetFolderResponseProperties, "properties")

    @cached_property
    def directChildren(self) -> GetFolderResponseDirectChildren:
        """Available when include_direct_children=True."""
        return self._new(GetFolderResponseDirectChildren, "directChildren")

    @cached_property
    def links(self) -> GetFolderResponseLinks:
        return self._new(GetFolderResponseLinks, "_links")
