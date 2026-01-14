# -*- coding: utf-8 -*-

"""
Confluence Page Exporter

Export Confluence pages to XML format for AI knowledge base ingestion.
The XML output contains structured metadata and markdown content optimized
for LLM context injection.
"""

import typing as T
import shutil
from pathlib import Path

from .constants import BreadCrumbTypeEnum, ConfluencePageFieldEnum
from .utils import safe_write
from .page import Page


def export_pages_to_xml_files(
    pages: T.List[Page],
    dir_out: Path,
    breadcrumb_type: BreadCrumbTypeEnum = BreadCrumbTypeEnum.title,
    wanted_fields: T.Optional[T.Set[ConfluencePageFieldEnum]] = None,
    ignore_to_markdown_error: bool = True,
    encoding: str = "utf-8",
    clean_output_dir: bool = False,
) -> None:
    """
    Export Confluence pages to individual XML files.

    Each page is serialized to XML with metadata and markdown content,
    named by its breadcrumb path to preserve hierarchy.

    :param pages: Pages to export (from crawler)
    :param dir_out: Output directory for XML files
    :param breadcrumb_type: Filename format - use page IDs or titles
    :param wanted_fields: Fields to include in XML; None means all fields
    :param ignore_to_markdown_error: Skip errors during markdown conversion
    :param encoding: Output file encoding
    :param clean_output_dir: Remove output directory before export
    """
    if clean_output_dir:
        shutil.rmtree(dir_out, ignore_errors=True)

    for page in pages:
        # Convert page to XML
        xml = page.to_xml(
            wanted_fields=wanted_fields,
            to_markdown_ignore_error=ignore_to_markdown_error,
        )

        # Determine filename from breadcrumb path
        if breadcrumb_type == BreadCrumbTypeEnum.id:
            basename = f"{page.entity.id_breadcrumb_path}.xml"
        elif breadcrumb_type == BreadCrumbTypeEnum.title:
            basename = f"{page.entity.title_breadcrumb_path}.xml"
        else:  # pragma: no cover
            raise TypeError(f"Unsupported breadcrumb_type: {breadcrumb_type}")

        path = dir_out / basename
        safe_write(path=path, content=xml, encoding=encoding)


def merge_files(
    dir_in_list: T.List[Path],
    path_out: Path,
    ext: str = ".xml",
    input_encoding: str = "utf-8",
    output_encoding: str = "utf-8",
    overwrite: bool = True,
) -> None:
    """
    Merge exported files into a single document.

    Collects all files with specified extension from input directories
    and concatenates them into one file for AI context ingestion.

    :param dir_in_list: Directories containing files to merge
    :param path_out: Output file path
    :param ext: File extension filter (e.g., ".xml")
    :param input_encoding: Input files encoding
    :param output_encoding: Output file encoding
    :param overwrite: If False, raise error when output exists

    :raises FileExistsError: If output exists and overwrite is False
    """
    if not overwrite and path_out.exists():
        raise FileExistsError(f"File already exists: {path_out}")

    # Collect files from all input directories
    paths: T.List[Path] = []
    for dir_in in dir_in_list:
        paths.extend(dir_in.glob(f"**/*{ext}"))
    paths.sort()

    # Read and concatenate
    contents = [p.read_text(encoding=input_encoding) for p in paths]
    safe_write(
        path=path_out,
        content="\n".join(contents),
        encoding=output_encoding,
    )
