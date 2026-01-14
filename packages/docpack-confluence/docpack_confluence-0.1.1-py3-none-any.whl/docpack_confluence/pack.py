# -*- coding: utf-8 -*-

"""
Confluence DocPack Core Module

High-level API for exporting Confluence pages from multiple spaces
to XML format for AI knowledge base ingestion.
"""

import dataclasses
import shutil
from pathlib import Path

from sanhe_confluence_sdk.api import Confluence

from .constants import ConfluencePageFieldEnum
from .constants import DescendantTypeEnum
from .constants import BreadCrumbTypeEnum
from .shortcuts import get_space_by_id
from .shortcuts import get_space_by_key
from .shortcuts import get_pages_by_ids
from .crawler import select_entities
from .page import Page
from .exporter import export_pages_to_xml_files, merge_files


@dataclasses.dataclass(frozen=True)
class SpaceExportConfig:
    """
    Configuration for exporting pages from a single Confluence space.

    :param client: Confluence API client
    :param space_id: Space ID (mutually exclusive with space_key)
    :param space_key: Space key (mutually exclusive with space_id)
    :param include: Glob patterns for pages to include
    :param exclude: Glob patterns for pages to exclude
    :param breadcrumb_type: Filename format - use page IDs or titles
    :param wanted_fields: Fields to include in XML output
    :param ignore_to_markdown_error: Skip errors during markdown conversion
    """

    # fmt: off
    client: Confluence = dataclasses.field()
    space_id: int | None = dataclasses.field(default=None)
    space_key: str | None = dataclasses.field(default=None)
    include: list[str] | None = dataclasses.field(default=None)
    exclude: list[str] | None = dataclasses.field(default=None)
    breadcrumb_type: BreadCrumbTypeEnum = dataclasses.field(default=BreadCrumbTypeEnum.title)
    wanted_fields: set[ConfluencePageFieldEnum] | None = dataclasses.field(default=None)
    ignore_to_markdown_error: bool = dataclasses.field(default=True)
    # fmt: on

    @property
    def space_identifier(self) -> str:
        """Unique identifier string for output directory naming."""
        if self.space_id is not None:
            return f"space_id_{self.space_id}"
        elif self.space_key is not None:
            return f"space_key_{self.space_key}"
        else:
            raise ValueError("Either space_id or space_key must be provided")

    def export(self, dir_out: Path, encoding: str = "utf-8") -> None:
        """
        Export filtered pages from this space to XML files.

        :param dir_out: Output directory for XML files
        :param encoding: Output file encoding
        """
        # Get homepage ID to start crawling
        if self.space_id is not None:
            homepage_id = get_space_by_id(
                client=self.client, space_id=self.space_id
            ).homepageId
        elif self.space_key is not None:
            homepage_id = get_space_by_key(
                client=self.client, space_key=self.space_key
            ).homepageId
        else:
            raise ValueError("Either space_id or space_key must be provided")

        entities = select_entities(
            client=self.client,
            root_id=int(homepage_id),
            root_type=DescendantTypeEnum.page,
            include=self.include,
            exclude=self.exclude,
            verbose=False,
        )

        # Fetch full page content
        results = get_pages_by_ids(
            client=self.client,
            ids=[int(entity.node.id) for entity in entities],
        )
        if len(entities) != len(results):
            raise ValueError("Mismatch between filtered_entities and fetched_pages")
        result_by_id = {str(result.id): result for result in results}

        # Build Page objects
        pages = [
            Page(
                site_url=self.client.url,
                entity=entity,
                result=result_by_id[str(entity.node.id)],
            )
            for entity in entities
        ]

        # Export to XML files
        export_pages_to_xml_files(
            pages=pages,
            dir_out=dir_out,
            breadcrumb_type=self.breadcrumb_type,
            wanted_fields=self.wanted_fields,
            ignore_to_markdown_error=self.ignore_to_markdown_error,
            encoding=encoding,
            clean_output_dir=False,
        )


@dataclasses.dataclass(frozen=True)
class ExportSpec:
    """
    Specification for exporting pages from multiple Confluence spaces.

    :param space_configs: List of space export configurations
    :param dir_out: Root output directory
    :param encoding: File encoding for all output files
    """

    space_configs: list[SpaceExportConfig] = dataclasses.field()
    dir_out: Path = dataclasses.field()
    encoding: str = dataclasses.field(default="utf-8")

    @property
    def path_merged_output(self) -> Path:
        """Path to merged knowledge base file."""
        return self.dir_out / "all_in_one_knowledge_base.txt"

    def export(self) -> None:
        """
        Execute the export: crawl, filter, and export pages from all spaces,
        then merge into a single knowledge base file.
        """
        # Clean output directory
        shutil.rmtree(self.dir_out, ignore_errors=True)

        # Export each space to its own subdirectory
        dir_out_list: list[Path] = []
        for space_config in self.space_configs:
            dir_out_space = self.dir_out / space_config.space_identifier
            dir_out_list.append(dir_out_space)
            space_config.export(dir_out=dir_out_space, encoding=self.encoding)

        # Merge all exported files into one
        merge_files(
            dir_in_list=dir_out_list,
            path_out=self.path_merged_output,
            ext=".xml",
            input_encoding=self.encoding,
            output_encoding=self.encoding,
        )
