# -*- coding: utf-8 -*-

"""
Confluence Page Data Model

Provides the Page class for representing Confluence pages with hierarchy
metadata and serialization to XML/Markdown for AI knowledge base export.
"""

import typing as T
import json
import dataclasses
from functools import cached_property

import atlas_doc_parser.api as atlas_doc_parser
from sanhe_confluence_sdk.api import Confluence
from sanhe_confluence_sdk.methods.page.get_pages import (
    GetPagesResponseResult,
)
from .constants import TAB, ConfluencePageFieldEnum, DescendantTypeEnum
from .crawler import Entity, crawl_descendants, filter_entities


@dataclasses.dataclass
class Page:
    """
    Confluence page with hierarchy metadata and serialization capabilities.

    Combines crawled entity data (hierarchy info) with fetched page content
    (from Confluence API) to provide a complete page representation for export.

    :param site_url: Base URL of the Confluence site (e.g., "https://example.atlassian.net")
    :param entity: Crawled entity containing hierarchy metadata (breadcrumb paths, etc.)
    :param result: Page content from Confluence get_pages API response

    The page body is expected in
    `Atlas Doc Format <https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/>`_
    which is converted to Markdown for export.
    """

    site_url: str = dataclasses.field()
    entity: Entity = dataclasses.field()
    result: GetPagesResponseResult = dataclasses.field()

    @cached_property
    def _formatted_site_url(self) -> str:
        """Site URL without trailing slash."""
        if self.site_url.endswith("/"):
            return self.site_url[:-1]
        else:
            return self.site_url

    @cached_property
    def atlas_doc(self) -> dict[str, T.Any]:
        """Parsed Atlas Doc Format content as dictionary."""
        return json.loads(self.result.body.atlas_doc_format.value)

    @cached_property
    def webui_url(self) -> str:
        """Full URL to view this page in Confluence web UI."""
        return f"{self._formatted_site_url}/wiki{self.result.links.webui}"

    def to_markdown(self, ignore_error: bool = True) -> str:
        """
        Convert page content to Markdown format.

        :param ignore_error: Skip unsupported content types instead of raising errors

        :returns: Markdown string with page title as H1 header
        """
        node_doc = atlas_doc_parser.NodeDoc.from_dict(
            dct=self.atlas_doc,
        )
        md = node_doc.to_markdown(ignore_error=ignore_error)
        lines = [
            f"# {self.result.title}",
            "",
        ]
        lines.extend(md.splitlines())
        md = "\n".join(lines)
        return md.rstrip()

    def to_xml(
        self,
        wanted_fields: T.Optional[T.Set[ConfluencePageFieldEnum]] = None,
        to_markdown_ignore_error: bool = True,
    ) -> str:
        """
        Serialize page to XML format for AI knowledge base ingestion.

        :param wanted_fields: Fields to include; None means all fields
        :param to_markdown_ignore_error: Skip errors during markdown conversion

        :returns: XML string with document structure
        """
        if wanted_fields is None:
            wanted_fields = {field.value for field in ConfluencePageFieldEnum}
        else:
            wanted_fields = {field.value for field in wanted_fields}
        lines = list()
        lines.append("<document>")

        field = ConfluencePageFieldEnum.source_type.value
        if field in wanted_fields:
            lines.append(f"{TAB}<{field}>Confluence Page</{field}>")

        field = ConfluencePageFieldEnum.confluence_url.value
        if field in wanted_fields:
            lines.append(f"{TAB}<{field}>{self.webui_url}</{field}>")

        field = ConfluencePageFieldEnum.title.value
        if field in wanted_fields:
            lines.append(f"{TAB}<{field}>{self.result.title}</{field}>")

        field = ConfluencePageFieldEnum.markdown_content.value
        if field in wanted_fields:
            lines.append(f"{TAB}<{field}>")
            lines.append(self.to_markdown(ignore_error=to_markdown_ignore_error))
            lines.append(f"{TAB}</{field}>")

        lines.append("</document>")

        return "\n".join(lines)

    def to_json(
        self,
        wanted_fields: T.Optional[T.Set[ConfluencePageFieldEnum]] = None,
        to_markdown_ignore_error: bool = True,
    ) -> str:
        """Serialize page to JSON format. Not yet implemented."""
        raise NotImplementedError

    def to_yaml(
        self,
        wanted_fields: T.Optional[T.Set[ConfluencePageFieldEnum]] = None,
        to_markdown_ignore_error: bool = True,
    ) -> str:
        """Serialize page to YAML format. Not yet implemented."""
        raise NotImplementedError
