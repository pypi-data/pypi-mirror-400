from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from zmp_notion_exporter.node import Node


class NotionBlockType(str, Enum):
    BOOKMARK = "bookmark"
    BREADCRUMB = "breadcrumb"
    BULLETED_LIST_ITEM = "bulleted_list_item"
    CALLOUT = "callout"
    CHILD_DATABASE = "child_database"
    CHILD_PAGE = "child_page"
    COLUMN = "column"
    COLUMN_LIST = "column_list"
    DIVIDER = "divider"
    EMBED = "embed"
    CODE = "code"
    EQUATION = "equation"
    FILE = "file"
    HEADING_1 = "heading_1"
    HEADING_2 = "heading_2"
    HEADING_3 = "heading_3"
    IMAGE = "image"
    LINK_PREVIEW = "link_preview"
    LINK_TO_PAGE = "link_to_page"
    NUMBERED_LIST_ITEM = "numbered_list_item"
    PARAGRAPH = "paragraph"
    PDF = "pdf"
    QUOTE = "quote"
    SYNCED_BLOCK = "synced_block"
    TABLE = "table"
    TABLE_OF_CONTENTS = "table_of_contents"
    TABLE_ROW = "table_row"
    TEMPLATE = "template"
    TO_DO = "to_do"
    TOGGLE = "toggle"
    VIDEO = "video"
    UNSUPPORTED = "unsupported"


class NotionColorType(str, Enum):
    DEFAULT = "default"
    BLUE = "blue"
    BLUE_BACKGROUND = "blue_background"
    BROWN = "brown"
    BROWN_BACKGROUND = "brown_background"
    GRAY = "gray"
    GRAY_BACKGROUND = "gray_background"
    GREEN = "green"
    GREEN_BACKGROUND = "green_background"
    ORANGE = "orange"
    ORANGE_BACKGROUND = "orange_background"
    PINK = "pink"
    PINK_BACKGROUND = "pink_background"
    PURPLE = "purple"
    PURPLE_BACKGROUND = "purple_background"
    RED = "red"
    RED_BACKGROUND = "red_background"
    YELLOW = "yellow"
    YELLOW_BACKGROUND = "yellow_background"

    def get_admonition_type(self) -> MDXAdmonitionType:
        if self == NotionColorType.GREEN_BACKGROUND:
            return MDXAdmonitionType.TIP
        elif self == NotionColorType.BLUE_BACKGROUND:
            return MDXAdmonitionType.INFO
        elif self == NotionColorType.YELLOW_BACKGROUND:
            return MDXAdmonitionType.WARNING
        elif self == NotionColorType.RED_BACKGROUND:
            return MDXAdmonitionType.DANGER
        else:
            return MDXAdmonitionType.NOTE


class MDXAdmonitionType(str, Enum):
    NOTE = "note"
    TIP = "tip"
    INFO = "info"
    WARNING = "warning"
    DANGER = "danger"


class MDXCodeLanguage(str, Enum):
    JSX = "jsx"
    MDX_CODE_BLOCK = "mdx-code-block"
    JULIA = "julia"
    MATLAB = "matlab"

    @classmethod
    def translate_to_language(cls, language: str) -> str:
        if language == cls.JULIA.value:
            return cls.JSX.value
        elif language == cls.MATLAB.value:
            return cls.MDX_CODE_BLOCK.value
        else:
            return language


class RichTextType(str, Enum):
    TEXT = "text"
    MENTION = "mention"
    EQUATION = "equation"


class MentionType(str, Enum):
    USER = "user"
    DATE = "date"
    DATABASE = "database"
    PAGE = "page"
    LINK_PREVIEW = "link_preview"
    CUSTOM_EMOJI = "custom_emoji"


class UserType(str, Enum):
    PERSON = "person"
    BOT = "bot"


class ParentType(str, Enum):
    DATABASE = "database_id"
    PAGE = "page_id"
    WORKSPACE = "workspace"
    BLOCK = "block_id"


class FileType(str, Enum):
    FILE = "file"
    EXTERNAL = "external"
    CUSTOM_EMOJI = "custom_emoji"


class RenderingMode(str, Enum):
    MARKDOWN = "markdown"
    MARKDOWNX = "markdownx"
    HTML = "html"


class BaseBlock(BaseModel):
    id: str = Field(..., description="Block ID. UUIDv4")

    indent: int = Field(
        0, description="Indentation level for markdown formatting", ge=0, le=10
    )

    static_file_output_dir: Optional[Path] = Field(
        default=None, description="Output directory for static files"
    )

    static_file_context_path: Optional[str] = Field(
        default=None, description="Context path to the static file"
    )

    docs_root_node: Optional[Node] = Field(
        default=None, description="The root node of the this page(document)"
    )

    has_end_tag: bool = Field(
        default=False, description="Whether the block has an end tag"
    )

    @property
    def indent_space(self) -> str:
        """
        Returns a string of spaces(4 spaces per level) for the given indentation level.
        """
        return "    " * self.indent

    @abstractmethod
    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        pass

    @abstractmethod
    def generate_html_start_tag(self) -> str:
        pass

    @abstractmethod
    def generate_html_end_tag(self) -> str:
        pass

    def generate_end_tag(self) -> str:
        # will be overridden in the subclass if needed
        ...

    def get_file_name_from_url(self, url: str) -> str:
        """get file name from url.

        Args:
            url (str): url of image or file

        Returns:
            str: file name
        """
        filename = url.split("/")[-1]
        if "?" in filename:
            filename = filename.split("?")[0]
        return filename
