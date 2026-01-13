# -*- coding: utf-8 -*-

import dataclasses
from functools import cached_property

from func_args.api import REQ, OPT

from ...client import Confluence

from ..model import api_field, BaseRequest, BodyParams, BaseResponse


# ------------------------------------------------------------------------------
# Input
# ------------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class CreateFolderRequestBodyParams(BodyParams):
    space_id: str = api_field(REQ, "spaceId")
    title: str = api_field(OPT)
    parent_id: str = api_field(OPT, "parentId")


@dataclasses.dataclass(frozen=True)
class CreateFolderRequest(BaseRequest):
    """
    See: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-folder/#api-folders-post
    """

    body_params: CreateFolderRequestBodyParams = dataclasses.field(
        default_factory=CreateFolderRequestBodyParams
    )

    @property
    def _path(self) -> str:
        return "/folders"

    def sync(self, client: Confluence) -> "CreateFolderResponse":
        return self._sync_post(CreateFolderResponse, client)


# ------------------------------------------------------------------------------
# Output
# ------------------------------------------------------------------------------
# --- Deepest nested objects first ---
@dataclasses.dataclass(frozen=True)
class CreateFolderResponseVersion(BaseResponse):
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
class CreateFolderResponseLinks(BaseResponse):
    """FolderLinks schema."""

    @cached_property
    def webui(self) -> str:
        """Web UI link of the content."""
        return self._get("webui")


# --- Main response object ---
@dataclasses.dataclass(frozen=True)
class CreateFolderResponse(BaseResponse):
    """FolderSingle schema - response for creating a folder."""

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
        """ContentStatus enum: current, draft, archived, historical, trashed, deleted."""
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
        """Position of the folder within the parent tree."""
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
    def version(self) -> CreateFolderResponseVersion:
        return self._new(CreateFolderResponseVersion, "version")

    @cached_property
    def links(self) -> CreateFolderResponseLinks:
        return self._new(CreateFolderResponseLinks, "_links")
