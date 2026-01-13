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
class GetPageRequestPathParams(PathParams):
    id: int = api_field(REQ)


@dataclasses.dataclass(frozen=True)
class GetPageRequestQueryParams(QueryParams):
    body_format: str = api_field(OPT, "body-format")
    get_draft: bool = api_field(OPT, "get-draft")
    status: list[str] = api_field(OPT)
    version: int = api_field(OPT)
    include_labels: bool = api_field(OPT, "include-labels")
    include_properties: bool = api_field(OPT, "include-properties")
    include_operations: bool = api_field(OPT, "include-operations")
    include_likes: bool = api_field(OPT, "include-likes")
    include_versions: bool = api_field(OPT, "include-versions")
    include_version: bool = api_field(OPT, "include-version")
    include_favorited_by_current_user_status: bool = api_field(OPT, "include-favorited-by-current-user-status")
    include_webresources: bool = api_field(OPT, "include-webresources")
    include_collaborators: bool = api_field(OPT, "include-collaborators")
    include_direct_children: bool = api_field(OPT, "include-direct-children")


@dataclasses.dataclass(frozen=True)
class GetPageRequest(BaseRequest):
    """
    See: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-get
    """

    path_params: GetPageRequestPathParams = dataclasses.field(
        default_factory=GetPageRequestPathParams
    )
    query_params: GetPageRequestQueryParams = dataclasses.field(
        default_factory=GetPageRequestQueryParams
    )

    @property
    def _path(self) -> str:
        return f"/pages/{self.path_params.id}"

    def sync(self, client: Confluence) -> "GetPageResponse":
        return self._sync_get(GetPageResponse, client)


# ------------------------------------------------------------------------------
# Output
# ------------------------------------------------------------------------------
# --- Deepest nested objects first ---
@dataclasses.dataclass(frozen=True)
class GetPageResponseBodyStorage(BaseResponse):
    """BodyType schema for storage representation."""

    @cached_property
    def representation(self) -> str:
        return self._get("representation")

    @cached_property
    def value(self) -> str:
        return self._get("value")


@dataclasses.dataclass(frozen=True)
class GetPageResponseBodyAtlasDocFormat(BaseResponse):
    """BodyType schema for atlas_doc_format representation."""

    @cached_property
    def representation(self) -> str:
        return self._get("representation")

    @cached_property
    def value(self) -> str:
        return self._get("value")


@dataclasses.dataclass(frozen=True)
class GetPageResponseBodyView(BaseResponse):
    """BodyType schema for view representation."""

    @cached_property
    def representation(self) -> str:
        return self._get("representation")

    @cached_property
    def value(self) -> str:
        return self._get("value")


@dataclasses.dataclass(frozen=True)
class GetPageResponseBody(BaseResponse):
    """BodySingle schema - contains fields for each representation type."""

    @cached_property
    def storage(self) -> GetPageResponseBodyStorage:
        return self._new(GetPageResponseBodyStorage, "storage")

    @cached_property
    def atlas_doc_format(self) -> GetPageResponseBodyAtlasDocFormat:
        return self._new(GetPageResponseBodyAtlasDocFormat, "atlas_doc_format")

    @cached_property
    def view(self) -> GetPageResponseBodyView:
        return self._new(GetPageResponseBodyView, "view")


@dataclasses.dataclass(frozen=True)
class GetPageResponseVersion(BaseResponse):
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
class GetPageResponseLinks(BaseResponse):
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


@dataclasses.dataclass(frozen=True)
class GetPageResponseLabel(BaseResponse):
    """Label schema."""

    @cached_property
    def id(self) -> str:
        """ID of the label."""
        return self._get("id")

    @cached_property
    def name(self) -> str:
        """Name of the label."""
        return self._get("name")

    @cached_property
    def prefix(self) -> str:
        """Prefix of the label."""
        return self._get("prefix")


@dataclasses.dataclass(frozen=True)
class GetPageResponseLabels(BaseResponse):
    """Labels with metadata schema."""

    @cached_property
    def results(self) -> list[GetPageResponseLabel]:
        return self._new_many(GetPageResponseLabel, "results")


@dataclasses.dataclass(frozen=True)
class GetPageResponseProperty(BaseResponse):
    """ContentProperty schema."""

    @cached_property
    def id(self) -> str:
        """ID of the property."""
        return self._get("id")

    @cached_property
    def key(self) -> str:
        """Key of the property."""
        return self._get("key")

    @cached_property
    def value(self) -> str:
        """Value of the property."""
        return self._get("value")


@dataclasses.dataclass(frozen=True)
class GetPageResponseProperties(BaseResponse):
    """Properties with metadata schema."""

    @cached_property
    def results(self) -> list[GetPageResponseProperty]:
        return self._new_many(GetPageResponseProperty, "results")


@dataclasses.dataclass(frozen=True)
class GetPageResponseOperation(BaseResponse):
    """Operation schema."""

    @cached_property
    def operation(self) -> str:
        """Name of the operation."""
        return self._get("operation")

    @cached_property
    def targetType(self) -> str:
        """The type of entity the operation acts on."""
        return self._get("targetType")


@dataclasses.dataclass(frozen=True)
class GetPageResponseOperations(BaseResponse):
    """Operations with metadata schema."""

    @cached_property
    def results(self) -> list[GetPageResponseOperation]:
        return self._new_many(GetPageResponseOperation, "results")


@dataclasses.dataclass(frozen=True)
class GetPageResponseLike(BaseResponse):
    """Like schema."""

    @cached_property
    def accountId(self) -> str:
        """Account ID of the user who liked."""
        return self._get("accountId")


@dataclasses.dataclass(frozen=True)
class GetPageResponseLikes(BaseResponse):
    """Likes with metadata schema."""

    @cached_property
    def results(self) -> list[GetPageResponseLike]:
        return self._new_many(GetPageResponseLike, "results")

    @cached_property
    def count(self) -> int:
        """Count of likes."""
        return self._get("count")


@dataclasses.dataclass(frozen=True)
class GetPageResponseVersionsResult(BaseResponse):
    """Version schema for versions array."""

    @cached_property
    def createdAt(self) -> str:
        """Date and time when the version was created. ISO 8601 format."""
        return self._get("createdAt")

    @cached_property
    def message(self) -> str:
        """Message associated with this version."""
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
class GetPageResponseVersions(BaseResponse):
    """Versions with metadata schema."""

    @cached_property
    def results(self) -> list[GetPageResponseVersionsResult]:
        return self._new_many(GetPageResponseVersionsResult, "results")


# --- Main response object ---
@dataclasses.dataclass(frozen=True)
class GetPageResponse(BaseResponse):
    """PageSingle schema - response for getting a single page."""

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
    def isFavoritedByCurrentUser(self) -> bool:
        """Whether the current user has favorited this page."""
        return self._get("isFavoritedByCurrentUser")

    @cached_property
    def version(self) -> GetPageResponseVersion:
        return self._new(GetPageResponseVersion, "version")

    @cached_property
    def body(self) -> GetPageResponseBody:
        return self._new(GetPageResponseBody, "body")

    @cached_property
    def links(self) -> GetPageResponseLinks:
        return self._new(GetPageResponseLinks, "_links")

    @cached_property
    def labels(self) -> GetPageResponseLabels:
        """Labels associated with the page. Only available when include-labels=true."""
        return self._new(GetPageResponseLabels, "labels")

    @cached_property
    def properties(self) -> GetPageResponseProperties:
        """Properties associated with the page. Only available when include-properties=true."""
        return self._new(GetPageResponseProperties, "properties")

    @cached_property
    def operations(self) -> GetPageResponseOperations:
        """Permitted operations for the page. Only available when include-operations=true."""
        return self._new(GetPageResponseOperations, "operations")

    @cached_property
    def likes(self) -> GetPageResponseLikes:
        """Likes on the page. Only available when include-likes=true."""
        return self._new(GetPageResponseLikes, "likes")

    @cached_property
    def versions(self) -> GetPageResponseVersions:
        """Version history. Only available when include-versions=true."""
        return self._new(GetPageResponseVersions, "versions")
