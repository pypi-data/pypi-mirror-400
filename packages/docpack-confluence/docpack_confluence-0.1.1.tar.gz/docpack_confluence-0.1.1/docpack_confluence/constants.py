# -*- coding: utf-8 -*-

"""
Constants and Enums
"""

import enum

TAB = " " * 2


class ConfluencePageFieldEnum(str, enum.Enum):
    """
    Enum for Confluence page fields.
    """

    source_type = "source_type"
    confluence_url = "confluence_url"
    title = "title"
    markdown_content = "markdown_content"


GET_PAGE_DESCENDANTS_MAX_DEPTH = 5


class DescendantTypeEnum(str, enum.Enum):
    database = "database"
    embed = "embed"
    folder = "folder"
    page = "page"
    whiteboard = "whiteboard"


class BreadCrumbTypeEnum(str, enum.Enum):
    id = "id"
    title = "title"
