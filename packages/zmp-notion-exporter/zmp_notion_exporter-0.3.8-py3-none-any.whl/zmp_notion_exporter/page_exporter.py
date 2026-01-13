from __future__ import annotations

import logging
import logging.config
from enum import Enum
from pathlib import Path
from typing import Callable, Optional

from notion_client import Client
from pydantic import BaseModel

from zmp_notion_exporter.notion.base import NotionBlockType, RenderingMode
from zmp_notion_exporter.node import Node
from zmp_notion_exporter.notion.objects import (
    Block,
    MarkdownTableHeaderRow,
    Page,
    TableRow,
    User,
)
from zmp_notion_exporter.utility import (
    transform_block_id_to_uuidv4,
    validate_page_id,
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

ROOT_DIR_NAME = ".output"
DOCS_DIR_NAME = "docs"
STATIC_DIR_NAME = "static"
IMAGE_DIR_NAME = "img"


class Parent(BaseModel):
    object_id: Optional[str] = None
    name: Optional[str] = None


class SupportedFileType(str, Enum):
    PDF = "pdf"
    HTML = "html"
    MARKDOWN = "md"
    MARKDOWNX = "mdx"


class NotionPageExporter:
    def __init__(
        self,
        *,
        notion_token: str,
        root_page_id: str,
        root_output_dir: str,
    ):
        """Initialize the NotionPageExporter.

        Args:
            notion_token (str): Notion token
            root_page_id (str): Root page id
            root_output_dir (str): Root output directory
            log_level (Union[int, str] | None, optional): Log level. Defaults to logging.INFO.
        """
        self.client = Client(auth=notion_token)
        self.root_page_id = root_page_id
        self.root_output_dir = root_output_dir if root_output_dir else ROOT_DIR_NAME

        self.docs_node = None
        self.static_image_node = None
        self.initialized_node_tree = False

        self.total_pages = 0
        self.total_directories = 0
        self.exported_pages = 0

    def markdown(
        self, *, page_id: str | None = None, include_subpages: bool = False
    ) -> Path:
        """Export the page to a markdown file.

        Args:
            page_id (str): page id or None for all pages
            include_subpages (bool, optional): include subpages. Defaults to False.

        Returns:
            Path: markdown file path
        """
        return self._export(
            page_id=page_id,
            include_subpages=include_subpages,
            file_type=SupportedFileType.MARKDOWN,
        )

    def markdownx(
        self,
        page_id: Optional[str] = None,
        include_subpages: bool = False,
        progress_callback: Optional[Callable[[int, int, Optional[str]], None]] = None,
    ) -> Path:
        """Export the page to a markdownx file.

        Args:
            page_id (str): page id or None for all pages
            include_subpages (bool, optional): include subpages. Defaults to False.
            progress_callback: Optional callback function that takes (current_progress, total, message) as arguments

        Returns:
            Path: markdownx file path
        """
        try:
            # Initialize node tree if not already done
            if not self.initialized_node_tree:
                self._make_tree_node()

            # Reset counters
            self.exported_pages = 0
            self.total_pages = 0

            return self._export(
                page_id=page_id,
                include_subpages=include_subpages,
                file_type=SupportedFileType.MARKDOWNX,
                progress_callback=progress_callback,
            )

        except Exception as e:
            log.error(f"Failed to export MDX: {str(e)}")
            raise

    def html(self, *, page_id: str, include_subpages: bool = False) -> Path:
        """Export the page to a html file.

        Args:
            page_id (str): page id
            include_subpages (bool, optional): include subpages. Defaults to False.

        Returns:
            Path: html file path
        """
        return self._export(
            page_id=page_id,
            include_subpages=include_subpages,
            file_type=SupportedFileType.HTML,
        )

    def pdf(self, *, page_id: str, include_subpages: bool = False) -> Path:
        """Export the page to a pdf file.

        Args:
            page_id (str): page id
            include_subpages (bool, optional): include subpages. Defaults to False.

        Returns:
            Path: pdf file path
        """
        # Not implemented yet. Don't use this function
        raise NotImplementedError("PDF export is not implemented yet")

    def get_output_nodes(self) -> tuple[Node, Node]:
        """Get the output nodes.

        Returns:
            tuple[Node, Node]: docs node and static image node
        """
        if not self.initialized_node_tree:
            self._make_tree_node()

        return self.docs_node, self.static_image_node

    def html_string(self, *, page_id: str) -> tuple[Page, str]:
        """Export the page to a html tag string.

        Args:
            page_id (str): page id

        Returns:
            tuple[Page, str]: page object and html tag string
        """
        return self._rendering_page(page_id=page_id, rendering_mode=RenderingMode.HTML)

    def markdown_string(self, *, page_id: str) -> tuple[Page, str]:
        """Export the page to a markdown tag string.
        This function returns the markdown tag string only for the current page.

        Args:
            page_id (str): page id

        Returns:
            tuple[Page, str]: page object and markdown tag string
        """
        return self._rendering_page(
            page_id=page_id, rendering_mode=RenderingMode.MARKDOWN
        )

    def _rendering_page(
        self,
        *,
        page_id: str,
        rendering_mode: RenderingMode,
        need_generate_metadata: bool = True,
    ) -> tuple[Page, str]:
        """Generate the tag string for the page.

        Args:
            page_id (str): page id
            rendering_mode (RenderingMode): rendering mode

        Returns:
            tuple[Page, str]: page object and tag string
        """
        page = self._get_page(page_id)

        blocks = self._get_all_blocks(page.id)

        # @TODO: Why page_node from static_image_node? I think it should be from docs_node
        page_node = self.static_image_node.find_by_object_id(page_id)

        # image directory is the parent of the page node
        # Never page_node.parent is None because the page node is the child of the static image node
        static_file_output_dir = Path(
            self.static_image_node.find_path_by_object_id(page_node.parent.object_id)
        )

        blocks_tag = []
        if rendering_mode == RenderingMode.MARKDOWNX and need_generate_metadata:
            blocks_tag.append(
                page.get_markdownx_metadata(sidebar_position=page_node.index)
            )

        for block in blocks:
            # ignore child page
            if block.type != NotionBlockType.CHILD_PAGE:
                if block.type in [
                    NotionBlockType.IMAGE,
                    NotionBlockType.FILE,
                    NotionBlockType.PDF,
                ]:
                    block.static_file_output_dir = static_file_output_dir
                    # for docusaurus, we need to use the context path
                    # context path is '/img/.../filename'
                    block.static_file_context_path = str(
                        static_file_output_dir
                    ).replace(f"{self.root_output_dir}/{STATIC_DIR_NAME}", "")

                if block.type in [
                    NotionBlockType.PARAGRAPH,
                    NotionBlockType.LINK_TO_PAGE,
                ]:
                    # to get the absolute path of the linked notion page in the any block
                    block.docs_root_node = self.docs_node.find_by_object_id(
                        self.root_page_id
                    )

                log.debug(
                    f"block info for rendering - type: {block.type} value: {block}"
                )

                blocks_tag.append(
                    self._rendering_block(
                        block,
                        rendering_mode=rendering_mode,
                        static_file_output_dir_of_page=static_file_output_dir,
                    )
                )

        log.debug(
            f"page is rendered successfully - {page.properties.renamed_page_title}"
        )

        return (page, "".join(blocks_tag))

    def _rendering_block(
        self,
        block: Block,
        *,
        static_file_output_dir_of_page: Path | None = None,
        rendering_mode: RenderingMode = RenderingMode.MARKDOWN,
    ) -> str:
        """Generate the content tag string for the block.

        Args:
            block (Block): block object
            rendering_mode (RenderingMode, optional): rendering mode. Defaults to RenderingMode.MARKDOWN.

        Returns:
            str: content tag string
        """
        if (
            rendering_mode == RenderingMode.MARKDOWN
            and block.type == NotionBlockType.CALLOUT
        ):
            rendering_mode = RenderingMode.HTML

        content_tag = ""
        if rendering_mode == RenderingMode.HTML:
            content_tag += block.get_type_object().generate_html_start_tag()

        _type_object = block.get_type_object()
        log.debug(f"Block {block.type} :\n{_type_object}")

        content_tag += _type_object.generate_tag(rendering_mode=rendering_mode)

        if block.has_children:
            log.debug(f"Block {block.id} has children")

            if block.type == NotionBlockType.TABLE:
                # because the markdown does not support indent for table
                indent = block.indent + 1 if rendering_mode == RenderingMode.HTML else 0
                child_blocks = self._get_all_blocks(block.id, indent=indent)
                header_row = True
                # child_blocks is list of TableRow
                for child_block in child_blocks:
                    content_tag += self._rendering_block(
                        child_block, rendering_mode=rendering_mode
                    )
                    # for header row, add --- to the markdown
                    if header_row:
                        table_header: TableRow = child_block.get_type_object()
                        table_header_row: MarkdownTableHeaderRow = (
                            MarkdownTableHeaderRow(
                                id=table_header.id,  # dummy id
                                cells_count=len(table_header.cells),
                                indent=indent,
                            )
                        )
                        content_tag += table_header_row.generate_tag(
                            rendering_mode=rendering_mode
                        )
                        header_row = False
            else:
                child_blocks = self._get_all_blocks(block.id, indent=block.indent + 1)
                for child_block in child_blocks:
                    if child_block.type != NotionBlockType.CHILD_PAGE:
                        if child_block.type in [
                            NotionBlockType.IMAGE,
                            NotionBlockType.FILE,
                            NotionBlockType.PDF,
                        ]:
                            child_block.static_file_output_dir = (
                                static_file_output_dir_of_page
                            )
                            # for docusaurus, we need to use the context path
                            # context path is '/img/.../filename'
                            child_block.static_file_context_path = str(
                                static_file_output_dir_of_page
                            ).replace(f"{self.root_output_dir}/{STATIC_DIR_NAME}", "")

                        if child_block.type in [
                            NotionBlockType.PARAGRAPH,
                            NotionBlockType.LINK_TO_PAGE,
                        ]:
                            # to get the absolute path of the linked notion page in the any block
                            child_block.docs_root_node = (
                                self.docs_node.find_by_object_id(self.root_page_id)
                            )

                        content_tag += self._rendering_block(
                            child_block,
                            rendering_mode=rendering_mode,
                            static_file_output_dir_of_page=static_file_output_dir_of_page,
                        )

        if rendering_mode == RenderingMode.HTML:
            content_tag += block.get_type_object().generate_html_end_tag()

        # for the callout(admonition) block, we need to add the end tag for callout's children
        if _type_object.has_end_tag:
            content_tag += _type_object.generate_end_tag()

        log.debug(f"Block {block.id} has been generated successfully")

        return content_tag

    def _export(
        self,
        *,
        page_id: str | None = None,
        include_subpages: bool = False,
        file_type: SupportedFileType,
        progress_callback: Optional[Callable[[int, int, Optional[str]], None]] = None,
    ) -> Path:
        """Export the page to a supported file.

        Args:
            page_id (str): page id or None for all pages
            include_subpages (bool, optional): include subpages. Defaults to False.
            file_type (SupportedFileType): file type
                SupportedFileType.MARKDOWN: markdown file
                SupportedFileType.MARKDOWNX: markdownx file
                SupportedFileType.HTML: html file
                SupportedFileType.PDF: pdf file
            progress_callback: Optional callback function that takes (current_progress, total, message) as arguments

        Returns:
            Path: supported file path
        """
        # validate the page_id format is valid UUIDv4 or not
        if page_id is not None and not validate_page_id(page_id):
            log.warning(
                f"Invalid page ID format. Page ID must be a valid UUID: {page_id}"
            )
            page_id = transform_block_id_to_uuidv4(page_id)

        if not self.initialized_node_tree:
            self._make_tree_node()

        if page_id is None:
            if include_subpages:
                # 1. this is the case for the sub pages of the root directory
                self._set_total_pages_and_directories(self.docs_node)

                self._export_recursive(
                    self.docs_node,
                    file_type=file_type,
                    progress_callback=progress_callback,
                )
                return Path(self.root_output_dir)
            else:
                # 2. this is the case for the root page
                # So we don't need to export the markdown for the root page
                raise ValueError("Root page is not supported for markdown export")
        else:
            if include_subpages:
                # 3. this is the case for the sub pages of the target directory
                node = self.docs_node.find_by_object_id(page_id)

                if node is None:
                    raise ValueError(f"Could not find page with ID: {page_id}")

                log.info(f"Exporting sub pages of the target directory: {node.name}")

                self._set_total_pages_and_directories(node)

                self._export_recursive(
                    node, file_type=file_type, progress_callback=progress_callback
                )

                return Path(self.docs_node.find_path_by_object_id(page_id))
            else:
                # 4. this is the case for the target single page
                self._set_total_pages_and_directories(None)

                page, file_content = self._rendering_page(
                    page_id=page_id,
                    rendering_mode=(
                        RenderingMode.MARKDOWN
                        if file_type == SupportedFileType.MARKDOWN
                        else (
                            RenderingMode.MARKDOWNX
                            if file_type == SupportedFileType.MARKDOWNX
                            else RenderingMode.HTML
                        )
                    ),
                )

                full_path = f"{self.docs_node.find_path_by_object_id(page.id)}.{file_type.value}"
                file_path = Path(full_path)
                file_path.parent.mkdir(parents=True, exist_ok=True)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(file_content)

                self._increment_exported_pages()

                # Call progress callback if provided
                if progress_callback:
                    progress_callback(
                        1, 1, f"Exported page: {page.properties.renamed_page_title}"
                    )

                return Path(full_path)

    @property
    def initialized(self) -> bool:
        return self.initialized_node_tree

    @property
    def total_and_exported_pages(self) -> tuple[int, int]:
        if self.initialized_node_tree:
            return self.total_pages, self.exported_pages
        else:
            raise ValueError("Node tree is not initialized")

    @property
    def progress(self) -> int:
        if self.initialized_node_tree:
            return int((self.exported_pages / self.total_pages) * 100)
        else:
            raise ValueError("Node tree is not initialized")

    @property
    def progress_info(self) -> str:
        if self.initialized_node_tree:
            return f"Total: {self.total_pages} / Exported: {self.exported_pages}, Progress: {self.progress}%"
        else:
            raise ValueError("Node tree is not initialized")

    def _increment_exported_pages(self) -> None:
        self.exported_pages += 1

    def _set_total_pages_and_directories(self, node: Node) -> None:
        if node is None:
            self.total_pages = 1
            self.total_directories = 0
        else:
            self.total_pages = node.total_pages
            self.total_directories = node.total_directories

    def _export_recursive(
        self,
        node: Node,
        *,
        file_type: SupportedFileType,
        progress_callback: Optional[Callable[[int, int, Optional[str]], None]] = None,
    ) -> None:
        """Export pages recursively with progress tracking"""
        if not node.is_directory and node.object_id:
            # Render the page for leaf nodes
            page, file_content = self._rendering_page(
                page_id=node.object_id,
                rendering_mode=(
                    RenderingMode.MARKDOWN
                    if file_type == SupportedFileType.MARKDOWN
                    else (
                        RenderingMode.MARKDOWNX
                        if file_type == SupportedFileType.MARKDOWNX
                        else RenderingMode.HTML
                    )
                ),
            )

            # Create file path and ensure directory exists
            full_path = f"{self.docs_node.find_path_by_object_id(node.object_id)}.{file_type.value}"
            file_path = Path(full_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write markdown content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file_content)

            self._increment_exported_pages()

            # Call progress callback if provided
            if progress_callback:
                progress_callback(
                    self.exported_pages,
                    self.total_pages,
                    f"Exported page: {page.properties.renamed_page_title}",
                )

            log.info(f"Created {file_type} file: {file_path}")
        else:
            # Handle directory case
            if file_type == SupportedFileType.MARKDOWNX:
                if node.name not in [self.root_output_dir, DOCS_DIR_NAME]:
                    page = self._get_page(node.object_id)
                    category_tag = page.get_category_tag(position=node.index)

                    full_path = (
                        f"{self.docs_node.find_path_by_object_id(node.object_id)}"
                    )
                    file_path = Path(full_path) / "_category_.json"
                    file_path.parent.mkdir(parents=True, exist_ok=True)

                    # Write _category_.json content for docusaurus
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(category_tag)

                    log.info(f"Created _category_.json file: {file_path}")

        # Recursively process children
        if node.children:
            for child in node.children:
                self._export_recursive(
                    child, file_type=file_type, progress_callback=progress_callback
                )

    def _get_page(self, page_id: str) -> Page:
        """Get the page object from Notion API using page id.

        Args:
            page_id (str): page id

        Returns:
            Page: page object
        """
        try:
            _page = self.client.pages.retrieve(page_id)
        except Exception as e:
            log.error(f"Error getting page: {e}")
            raise ValueError(
                f"The page: {page_id} is not found. Please check the page id is correct."
            )

        log.debug(f"Page info by notion client: \n{_page}")

        return Page(**_page)

    def _get_all_blocks(self, block_id: str, *, indent: int | None = 0) -> list[Block]:
        """
        Get all blocks from Notion API using block id.

        Args:
            block_id (str): block id

        Returns:
            list: list of blocks
        """
        notion_blocks = []
        next_cursor = None

        while True:
            response = self.client.blocks.children.list(
                block_id=block_id, start_cursor=next_cursor
            )
            notion_blocks.extend(response.get("results", []))
            next_cursor = response.get("next_cursor")
            if not next_cursor:
                break

        blocks: list[Block] = []
        for notion_block in notion_blocks:
            block = Block(**notion_block)
            block.indent = indent
            blocks.append(block)

        log.debug(f"All blocks of block {block_id} have been retrieved successfully")

        return blocks

    def _has_child_pages(self, children: list[Block]) -> bool:
        """Check if the page is a directory.

        Args:
            page (Page): page object

        Returns:
            bool: True if the page is a directory, False otherwise
        """
        for block in children:
            if block.type == NotionBlockType.CHILD_PAGE:
                return True
        return False

    def get_tree_nodes(self, *, page_id: str | None = None) -> list[Node]:
        """Get the nodes of the page.

        Args:
            page_id (str): page id. If None, the root page id will be used.

        Returns:
            list[Node]: nodes
        """
        if page_id is None:
            page_id = self.root_page_id

        all_nodes = []
        root_node = self._make_node_from_page(page_id)
        all_nodes.append(root_node)

        if root_node.children:
            for child in root_node.children:
                all_nodes.append(child)
                self._extract_children_nodes(
                    node=child,
                    all_nodes=all_nodes,
                )

        # remove children from all nodes because recursive function is called

        for node in all_nodes:
            node.children = None
            node.parent = Parent(
                object_id=node.parent.object_id if node.parent else None,
                name=node.parent.name if node.parent else None,
            )

        return all_nodes

    def _extract_children_nodes(
        self,
        *,
        node: Node,
        all_nodes: list[Node],
    ) -> None:
        """Extract children nodes from the node.

        Args:
            node (Node): node
            all_nodes (list[Node]): all nodes
        """
        if node.children:
            for child in node.children:
                all_nodes.append(child)
                self._extract_children_nodes(node=child, all_nodes=all_nodes)

    def _make_tree_node(self, *, page_id: str | None = None) -> tuple[Node, Node]:
        """Make the tree node.

        Args:
            page_id (str): page id

        Returns:
            tuple[Node, Node]: docs node and static image node
        """
        if page_id is None:
            page_id = self.root_page_id

        children = self._make_node_from_page(page_id)

        self.docs_node = self._get_output_docs_node(children)
        self.docs_node.create_directory()

        self.static_image_node = self._get_output_static_image_node(children)
        self.static_image_node.create_directory()

        self.initialized_node_tree = True

        log.info("Nodes for the docs and static image have been created successfully")

        return self.docs_node, self.static_image_node

    def _get_output_docs_node(self, children: Node) -> Node:
        """Get the root node of the manual.
        ex)
        .output/
            docs/
                [solution]/
                    [pages]

        Args:
            children (Node): children node

        Returns:
            Node: root node
        """
        root_node = Node(
            object_id=f"__{self.root_output_dir}__",
            name=self.root_output_dir,
            is_directory=True,
        )

        docs_node = Node(
            object_id=f"__{DOCS_DIR_NAME}__",
            name=DOCS_DIR_NAME,
            is_directory=True,
        )

        # Add the children directly to the docs node
        docs_node.add_child(children)
        root_node.add_child(docs_node)

        log.info(f"Docs node: {docs_node.name}")

        return root_node

    def _get_output_static_image_node(self, children: Node) -> Node:
        """Get the static image node of the output.

        ex)
        .output/
            static/
                img/

        Args:
            children (Node): children node

        Returns:
            Node: static image node
        """
        root_node = Node(
            object_id=f"__{self.root_output_dir}__",
            name=self.root_output_dir,
            is_directory=True,
        )

        static_node = Node(
            object_id=f"__{STATIC_DIR_NAME}__",
            name=STATIC_DIR_NAME,
            is_directory=True,
        )

        image_node = Node(
            object_id=f"__{IMAGE_DIR_NAME}__",
            name=IMAGE_DIR_NAME,
            is_directory=True,
        )

        image_node.add_child(children)

        static_node.add_child(image_node)

        root_node.add_child(static_node)

        log.info(f"Static image node: {static_node.name}")

        return root_node

    def _make_node_from_page(self, page_id: str) -> Node:
        """Create a Node object from a Notion page.

        Args:
            page_id (str): ID of the Notion page

        Returns:
            Node: Node object representing the page
        """
        page = self._get_page(page_id)
        blocks = self._get_all_blocks(page_id)
        has_child_pages = self._has_child_pages(children=blocks)
        
        try:
            user_dict = self.client.users.retrieve(user_id=page.last_edited_by.id)
            user: User = User(**user_dict)
        except Exception as e:
            log.warning(f"Failed to retrieve user information for page {page_id}: {e}")
            user = None

        _node = Node(
            object_id=page.id,
            name=page.properties.renamed_page_title,
            is_directory=has_child_pages,
            last_edited_time=page.last_edited_time,
            last_edited_by=user.name if user else None,
            last_editor_avatar_url=user.avatar_url if user else None,
            notion_url=page.url,
        )

        if _node.is_directory:
            for block in blocks:
                if block.type == NotionBlockType.CHILD_PAGE:
                    child = self._make_node_from_page(block.id)
                    _node.add_child(child)
                else:
                    log.warning(
                        f"Page {page.properties.renamed_page_title}'s Block {block.id}-{block.type} is not a child page. It will be ignored."
                    )

        return _node
