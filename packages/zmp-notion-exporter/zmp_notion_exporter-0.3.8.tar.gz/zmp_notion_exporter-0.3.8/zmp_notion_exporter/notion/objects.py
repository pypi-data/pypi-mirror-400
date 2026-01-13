from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import httpx
import requests
from pydantic import BaseModel, ConfigDict, Field

from zmp_notion_exporter.node import Node
from zmp_notion_exporter.notion.base import (
    BaseBlock,
    FileType,
    MDXCodeLanguage,
    MentionType,
    NotionBlockType,
    NotionColorType,
    ParentType,
    RenderingMode,
    RichTextType,
    UserType,
)
from zmp_notion_exporter.notion.threadpool_executor import get_executor
from zmp_notion_exporter.utility import (
    transform_block_id_to_uuidv4,
    validate_page_id,
)

_executor = get_executor()


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# https://developers.notion.com/reference/block


class Emoji(BaseModel):
    type: str = Field(..., description="The type of the emoji. Always emoji")
    emoji: str = Field(..., description="The emoji")


class NotionHostedFile(BaseModel):
    url: str = Field(..., description="The notion hosted URL of the file")
    expiry_time: str = Field(..., description="The expiry time of the file. ISO 8601")


class NotionExternalFile(BaseModel):
    url: str = Field(..., description="The external URL of the file")


class File(BaseModel):
    type: FileType = Field(..., description="The type of the file. Always file")
    file: Optional[NotionHostedFile] = Field(
        default=None, description="The notion hosted file"
    )
    external: Optional[NotionExternalFile] = Field(
        default=None, description="The external file"
    )


class User(BaseModel):
    object: str = Field(..., description="The type of object. Always user")
    id: str = Field(..., description="The ID of the user. UUID")
    type: Optional[UserType] = Field(
        default=None, description="The type of the user. Person or Bot"
    )
    name: Optional[str] = Field(default=None, description="The name of the user")
    avatar_url: Optional[str] = Field(
        default=None, description="The avatar URL of the user"
    )
    person: Optional[Dict[str, Any]] = Field(
        default=None, description="The person object of the user"
    )
    bot: Optional[Dict[str, Any]] = Field(
        default=None, description="The bot object of the user"
    )


class Block(BaseModel):
    object: str = Field(..., description="The type of object. Always block")
    id: str = Field(..., description="The ID of the block. UUIDv4")
    parent: Dict[str, Any] = Field(..., description="The parent of the block")
    type: NotionBlockType = Field(..., description="The type of the block")
    created_time: str = Field(..., description="The time the block was created")
    created_by: Dict[str, Any] = Field(
        ..., description="The user who created the block"
    )
    last_edited_time: str = Field(..., description="The time the block was last edited")
    last_edited_by: Dict[str, Any] = Field(
        ..., description="The user who last edited the block"
    )
    archived: bool = Field(..., description="Whether the block is archived")
    in_trash: bool = Field(..., description="Whether the block is in the trash")
    has_children: bool = Field(..., description="Whether the block has children")

    indent: int = Field(0, description="The indent of the block", ge=0, le=10)

    static_file_output_dir: Optional[Path] = Field(
        default=None, description="The path to the static image directory"
    )

    static_file_context_path: Optional[str] = Field(
        default=None, description="The context path to the static file"
    )

    docs_root_node: Optional[Node] = Field(
        default=None, description="The root node of the this page(document)"
    )

    model_config = ConfigDict(
        extra="allow",
    )

    def get_type_object(self) -> BaseBlock:
        _type_object = self.model_dump(include={self.type}).get(self.type, {})
        _type_object["id"] = self.id
        _type_object["indent"] = self.indent
        _type_object["static_file_output_dir"] = self.static_file_output_dir
        _type_object["static_file_context_path"] = self.static_file_context_path
        _type_object["docs_root_node"] = self.docs_root_node

        if isinstance(_type_object, dict):
            if self.type == NotionBlockType.BOOKMARK:
                return Bookmark(**_type_object)
            elif self.type == NotionBlockType.BREADCRUMB:
                return Breadcrumb(**_type_object)
            elif self.type == NotionBlockType.BULLETED_LIST_ITEM:
                return BulletedListItem(**_type_object)
            elif self.type == NotionBlockType.CALLOUT:
                return Callout(**_type_object)
            elif self.type == NotionBlockType.CHILD_DATABASE:
                return ChildDataBase(**_type_object)
            elif self.type == NotionBlockType.CHILD_PAGE:
                return ChildPage(**_type_object)
            elif self.type == NotionBlockType.COLUMN:
                return Column(**_type_object)
            elif self.type == NotionBlockType.COLUMN_LIST:
                return ColumnList(**_type_object)
            elif self.type == NotionBlockType.DIVIDER:
                return Divider(**_type_object)
            elif self.type == NotionBlockType.EMBED:
                return Embed(**_type_object)
            elif self.type == NotionBlockType.CODE:
                return Code(**_type_object)
            elif self.type == NotionBlockType.EQUATION:
                return Equation(**_type_object)
            elif self.type == NotionBlockType.FILE:
                return XFile(**_type_object)
            elif self.type == NotionBlockType.HEADING_1:
                return Heading1(**_type_object)
            elif self.type == NotionBlockType.HEADING_2:
                return Heading2(**_type_object)
            elif self.type == NotionBlockType.HEADING_3:
                return Heading3(**_type_object)
            elif self.type == NotionBlockType.IMAGE:
                return Image(**_type_object)
            elif self.type == NotionBlockType.LINK_PREVIEW:
                return LinkPreview(**_type_object)
            elif self.type == NotionBlockType.LINK_TO_PAGE:
                return LinkToPage(**_type_object)
            elif self.type == NotionBlockType.NUMBERED_LIST_ITEM:
                return NumberedListItem(**_type_object)
            elif self.type == NotionBlockType.PARAGRAPH:
                return Paragraph(**_type_object)
            elif self.type == NotionBlockType.PDF:
                return PDF(**_type_object)
            elif self.type == NotionBlockType.QUOTE:
                return Quote(**_type_object)
            elif self.type == NotionBlockType.SYNCED_BLOCK:
                return SyncedBlock(**_type_object)
            elif self.type == NotionBlockType.TABLE:
                return Table(**_type_object)
            elif self.type == NotionBlockType.TABLE_OF_CONTENTS:
                return TableOfContents(**_type_object)
            elif self.type == NotionBlockType.TABLE_ROW:
                return TableRow(**_type_object)
            elif self.type == NotionBlockType.TEMPLATE:
                return Template(**_type_object)
            elif self.type == NotionBlockType.TO_DO:
                return ToDo(**_type_object)
            elif self.type == NotionBlockType.TOGGLE:
                return Toggle(**_type_object)
            elif self.type == NotionBlockType.VIDEO:
                return Video(**_type_object)
            elif self.type == NotionBlockType.UNSUPPORTED:
                return Unsupported(**_type_object)
            else:
                return Unsupported(**_type_object)
        else:
            # raise ValueError(f"Unsupported block type: {self.type}")
            return Unsupported()


class Page(BaseModel):
    object: str = Field(..., description="The type of object. Always page")
    id: str = Field(..., description="The ID of the page. UUIDv4")
    created_time: str = Field(..., description="The time the page was created")
    created_by: User = Field(..., description="The user who created the page")
    last_edited_time: str = Field(..., description="The time the page was last edited")
    last_edited_by: User = Field(..., description="The user who last edited the page")
    archived: bool = Field(..., description="Whether the page is archived")
    in_trash: bool = Field(..., description="Whether the page is in the trash")
    cover: Optional[File] = Field(None, description="The cover of the page")
    icon: Optional[Emoji] = Field(None, description="The icon of the page")
    parent: Optional[Parent] = Field(None, description="The parent of the page")
    properties: Properties = Field(..., description="The properties of the page")
    url: str = Field(..., description="The URL of the page")
    public_url: Optional[str] = Field(None, description="The public URL of the page")

    model_config = ConfigDict(
        extra="allow",
    )

    def get_markdownx_metadata(self, *, sidebar_position: int = 1) -> str:
        markdownx_metadata = "---\n"
        markdownx_metadata += f"id: {self.properties.renamed_page_title}\n"
        markdownx_metadata += f'title: "{self.properties.get_page_title()}"\n'
        markdownx_metadata += f"sidebar_position: {sidebar_position}\n"
        markdownx_metadata += "---\n\n"
        return markdownx_metadata

    def get_category_tag(self, *, position: int = 1) -> str:
        category_tag = "{\n"
        category_tag += f'  "label": "{self.properties.get_page_title()}",\n'
        category_tag += f'  "position": {position},\n'
        category_tag += '  "collapsible": true,\n'
        category_tag += '  "collapsed": true\n'
        category_tag += "}\n\n"
        return category_tag

    class Properties(BaseModel):
        title: Optional[Title] = Field(None, description="The title of the property")

        @property
        def renamed_page_title(self) -> str:
            title = self.get_page_title()
            # 특수 문자들을 "-"로 변환하고 연속된 "-"는 하나로 합침
            title = re.sub(r"[ _/\\!@#$%^&*()+=|:;<>,.?~`]", "-", title)
            title = re.sub(r"-+", "-", title)
            title = title.strip("-")
            return title.lower()

        def get_page_title(self) -> str:
            return (
                "".join(text.plain_text for text in self.title.title)
                if self.title
                else ""
            )

        class Title(BaseModel):
            id: str = Field(..., description="The ID of the title property")
            type: str = Field(..., description="The type of the title property")
            title: List[RichText] = Field(
                ..., description="The title of the title property"
            )


class Parent(BaseModel):
    type: ParentType = Field(
        ...,
        description="The type of the parent. database_id, page_id, workspace, block_id",
    )
    page_id: Optional[str] = Field(None, description="The ID of the page. UUIDv4")
    database_id: Optional[str] = Field(
        None, description="The ID of the database. UUIDv4"
    )
    workspace: Optional[bool] = Field(
        default=None, description="Whether the parent is a workspace"
    )
    block_id: Optional[str] = Field(None, description="The ID of the block. UUIDv4")


class RichText(BaseModel):
    type: RichTextType = Field(
        ...,
        description="The type of the rich text. possible values: text, mention, equation",
    )
    text: Optional[Text] = Field(
        default=None, description="The text object containing content and optional link"
    )
    mention: Optional[Mention] = Field(
        default=None, description="The mention object containing the user or database"
    )
    equation: Optional[Equation] = Field(
        default=None, description="The equation object containing the equation"
    )
    annotations: Annotations = Field(
        ..., description="The annotations applied to the text"
    )
    plain_text: str = Field(
        ..., description="The plain text representation of the rich text"
    )
    href: Optional[str] = Field(
        default=None, description="An optional hyperlink reference"
    )

    def generate_richtext_tag(
        self,
        *,
        rendering_mode: RenderingMode = RenderingMode.MARKDOWN,
        document_absolute_path: Path | None = None,
        docs_root_node: Node | None = None,
    ) -> str:
        if rendering_mode == RenderingMode.MARKDOWN:
            markdown = ""
            if self.type == RichTextType.MENTION:
                if self.mention.type == MentionType.USER:
                    markdown = f"@{self.mention.user.name}"
                elif self.mention.type == MentionType.DATE:
                    markdown = (
                        f"{self.mention.date.start}"
                        f"{' ~ ' if self.mention.date.end else ''}"
                        f"{self.mention.date.end if self.mention.date.end else ''}"
                        f"{self.mention.date.time_zone if self.mention.date.time_zone else ''}"
                    )
                elif self.mention.type == MentionType.CUSTOM_EMOJI:
                    markdown = (
                        f"<img src='{self.mention.custom_emoji.url}' "
                        f"alt='{self.mention.custom_emoji.name}' "
                        f"width='16' height='16'>"
                    )
            elif self.type == RichTextType.TEXT:
                if self.href:
                    if notion_page_id := get_notion_page_id(self.href):
                        context_path = docs_root_node.find_path_by_object_id(
                            notion_page_id
                        )
                        markdown = f"[{self.plain_text}](/{context_path})"
                    else:
                        markdown = f"[{self.plain_text}]({self.href})"
                else:
                    markdown += self.plain_text
            elif self.type == RichTextType.EQUATION:
                markdown = f"$$ {self.equation.expression} $$"
            else:
                ...

            if self.annotations.bold:
                markdown = f"**{markdown}**"
            if self.annotations.italic:
                markdown = f"_{markdown}_"
            if self.annotations.strikethrough:
                markdown = f"~{markdown}~"
            if self.annotations.underline:
                markdown = f"<u>{markdown}</u>"
            if self.annotations.color != "default":
                markdown = (
                    f"<span style='color: {self.annotations.color}'>{markdown}</span>"
                )
            if self.annotations.code:
                ...

            return markdown
        elif rendering_mode == RenderingMode.MARKDOWNX:
            markdown = ""
            if self.type == RichTextType.MENTION:
                if self.mention.type == MentionType.USER:
                    markdown = f"@{self.mention.user.name}"
                elif self.mention.type == MentionType.DATE:
                    markdown = (
                        f"{self.mention.date.start}"
                        f"{' ~ ' if self.mention.date.end else ''}"
                        f"{self.mention.date.end if self.mention.date.end else ''}"
                        f"{self.mention.date.time_zone if self.mention.date.time_zone else ''}"
                    )
                elif self.mention.type == MentionType.CUSTOM_EMOJI:
                    markdown = (
                        f"<img src='{self.mention.custom_emoji.url}' "
                        f"alt='{self.mention.custom_emoji.name}' "
                        f"width='16' height='16'>"
                    )
            elif self.type == RichTextType.TEXT:
                if self.href:
                    if notion_page_id := get_notion_page_id(self.href):
                        context_path = docs_root_node.find_path_by_object_id(
                            notion_page_id
                        )
                        markdown = f"[{self.plain_text}](/{context_path})"
                    else:
                        markdown = f"[{self.plain_text}]({self.href})"
                else:
                    markdown += self.plain_text
            elif self.type == RichTextType.EQUATION:
                markdown = f"$$ {self.equation.expression} $$"
            else:
                ...

            if self.annotations.bold:
                markdown = f"<b>{markdown}</b>"
            if self.annotations.italic:
                markdown = f"<i>{markdown}</i>"
            if self.annotations.strikethrough:
                markdown = f"<s>{markdown}</s>"
            if self.annotations.underline:
                markdown = f"<u>{markdown}</u>"
            if self.annotations.color != "default":
                markdown = (
                    "<span style={{color: "
                    f"'{self.annotations.color}'"
                    "}}>"
                    f"{markdown}"
                    "</span>"
                )
            if self.annotations.code:
                ...

            return markdown
        elif rendering_mode == RenderingMode.HTML:
            html = ""
            if self.type == RichTextType.MENTION:
                if self.mention.type == MentionType.USER:
                    html = f"@{self.mention.user.name}"
                elif self.mention.type == MentionType.DATE:
                    html = (
                        f"{self.mention.date.start}"
                        f"{' ~ ' if self.mention.date.end else ''}"
                        f"{self.mention.date.end if self.mention.date.end else ''}"
                        f"{self.mention.date.time_zone if self.mention.date.time_zone else ''}"
                    )
                elif self.mention.type == MentionType.CUSTOM_EMOJI:
                    html = (
                        f"<img src='{self.mention.custom_emoji.url}' "
                        f"alt='{self.mention.custom_emoji.name}' "
                        f"width='16' height='16'>"
                    )
            elif self.type == RichTextType.TEXT:
                if self.href:
                    html = f"<a href='{self.href}'>{self.plain_text}</a>"
                else:
                    html += self.plain_text
            elif self.type == RichTextType.EQUATION:
                html = f"<div class='equation'>{self.equation.expression}</div>"
            else:
                ...

            if self.annotations.bold:
                html = f"<b>{html}</b>"
            if self.annotations.italic:
                html = f"<i>{html}</i>"
            if self.annotations.strikethrough:
                html = f"<s>{html}</s>"
            if self.annotations.underline:
                html = f"<u>{html}</u>"
            if self.annotations.color != "default":
                html = f"<span style='color: {self.annotations.color}'>{html}</span>"
            if self.annotations.code:
                ...

            return html


class Annotations(BaseModel):
    bold: bool = Field(default=False, description="Indicates if the text is bold")
    italic: bool = Field(default=False, description="Indicates if the text is italic")
    strikethrough: bool = Field(
        default=False, description="Indicates if the text has a strikethrough"
    )
    underline: bool = Field(
        default=False, description="Indicates if the text is underlined"
    )
    code: bool = Field(default=False, description="Indicates if the text is code")
    color: str = Field(default="default", description="The color of the text")


class Text(BaseModel):
    content: str = Field(..., description="The content of the text")
    link: Optional[Link] = Field(
        default=None, description="An optional link associated with the text"
    )

    class Link(BaseModel):
        url: str = Field(..., description="The URL of the link")


class Mention(BaseModel):
    type: MentionType = Field(
        ...,
        description="The type of the mention. custom_emoji, user, date, database, page, link_preview, template_mention",
    )
    custom_emoji: Optional[CustomEmoji] = Field(
        default=None,
        description="The custom emoji object containing the custom emoji",
    )
    date: Optional[Date] = Field(
        default=None, description="The date object containing the date"
    )
    user: Optional[User] = Field(
        default=None, description="The user object containing the user"
    )
    # TODO: fix recursive reference issue for page object
    page: Optional[Dict[str, Any]] = Field(
        default=None, description="The page object containing the page"
    )

    class CustomEmoji(BaseModel):
        id: str = Field(..., description="The ID of the custom emoji")
        name: str = Field(..., description="The name of the custom emoji")
        url: str = Field(..., description="The URL of the custom emoji")

    class Date(BaseModel):
        start: str = Field(..., description="The start date of the date")
        end: Optional[str] = Field(default=None, description="The end date of the date")
        time_zone: Optional[str] = Field(
            default=None, description="The time zone of the date"
        )

    # TODO: add database, link_preview, template_mention


################################################################################
# Class for each block type
################################################################################


class Bookmark(BaseBlock):
    url: str
    caption: Optional[List[RichText]] = None

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        if rendering_mode in [RenderingMode.MARKDOWN, RenderingMode.MARKDOWNX]:
            return f"[{self.url}]({self.url})\n\n"
        elif rendering_mode == RenderingMode.HTML:
            return f"<a href='{self.url}'>{self.url}</a>\n\n"

    def generate_html_start_tag(self) -> str:
        return ""

    def generate_html_end_tag(self) -> str:
        return ""


# Not supported
class Breadcrumb(BaseBlock):
    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        return ""

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


class BulletedListItem(BaseBlock):
    rich_text: List[RichText]
    color: NotionColorType = NotionColorType.DEFAULT
    children: Optional[List[Block]] = None

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        if rendering_mode in [RenderingMode.MARKDOWN, RenderingMode.MARKDOWNX]:
            return f"{self.indent_space}- {generate_richtext_tag(self.rich_text, rendering_mode)}\n"
        elif rendering_mode == RenderingMode.HTML:
            return f"{self.indent_space}<li>{generate_richtext_tag(self.rich_text, rendering_mode)}</li>\n"

    def generate_html_end_tag(self) -> str:
        return f"{self.indent_space}</ul>\n\n"

    def generate_html_start_tag(self) -> str:
        return f"{self.indent_space}<ul>\n"


class Callout(BaseBlock):
    rich_text: List[RichText]
    color: NotionColorType = NotionColorType.DEFAULT
    icon: Optional[Union[Emoji, File]] = None

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        # icon.file.url is the url which can be accessed publicly so we don't need to download it
        emoji = ""
        if self.icon:
            emoji = (
                self.icon.emoji if isinstance(self.icon, Emoji) else self.icon.file.url
            )

        if rendering_mode == RenderingMode.MARKDOWN:
            return f"{self.indent_space} {emoji} {generate_richtext_tag(self.rich_text, rendering_mode)}\n\n"
        elif rendering_mode == RenderingMode.MARKDOWNX:
            self.has_end_tag = (
                True  # for admonition block, we need to add the end tag for children
            )
            # https://docusaurus.io/docs/3.3.2/markdown-features/admonitions
            admonition_type = self.color.get_admonition_type().value
            markdownx = ""
            markdownx += f":::{admonition_type}\n"
            markdownx += "\n"
            markdownx += f"{generate_richtext_tag(self.rich_text, rendering_mode)}\n"
            # comment out the end tag for admonition block
            # markdownx += "\n"
            # markdownx += ":::\n\n"
            return markdownx
        elif rendering_mode == RenderingMode.HTML:
            html = ""
            html += f"{self.indent_space}<div class='callout-header'>\n"
            html += (
                f"{self.indent_space}<span class='callout-header-icon'>{emoji}</span>\n"
            )
            html += f"{self.indent_space}<span class='callout-header-text'>"
            html += f"{generate_richtext_tag(self.rich_text, rendering_mode)}</span>\n"
            html += f"{self.indent_space}</div>\n"
            html += f"{self.indent_space}<div class='callout-content'>\n"
            return html

    def generate_html_start_tag(self) -> str:
        color = self.color.replace("_", "-")
        return f"{self.indent_space}<div class='callout-{color}'>\n"

    def generate_html_end_tag(self) -> str:
        return f"{self.indent_space}</div></div><br/>\n\n"

    def generate_end_tag(self) -> str:
        return ":::\n\n"


# Not supported
class ChildDataBase(BaseBlock):
    title: str

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""

    def generate_html_end_tag(self) -> str:
        return ""


# Not supported
class ChildPage(BaseBlock):
    title: str

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        return ""

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


class Code(BaseBlock):
    language: str
    caption: Optional[List[RichText]] = None
    rich_text: List[RichText]

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        if rendering_mode == RenderingMode.MARKDOWN:
            markdown = ""
            markdown += f"{self.indent_space}```{self.language}\n"
            markdown += f"{generate_richtext_tag(self.rich_text, rendering_mode)}\n"
            markdown += "```\n\n"
            return markdown
        elif rendering_mode == RenderingMode.MARKDOWNX:
            _language = MDXCodeLanguage.translate_to_language(self.language)
            markdownx = ""
            markdownx += f"```{_language}\n"
            markdownx += f"{generate_richtext_tag(self.rich_text, rendering_mode)}\n"
            markdownx += "```\n\n"
            return markdownx
        elif rendering_mode == RenderingMode.HTML:
            html = ""
            html += f"{self.indent_space}<pre><code class='language-{self.language}'>"
            html += generate_richtext_tag(self.rich_text, rendering_mode)
            html += "</code></pre>\n"
            return html

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


# Not supported
class Column(BaseBlock):
    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        return ""

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


# Not supported
class ColumnList(BaseBlock):
    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        return ""

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


class Divider(BaseBlock):
    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        if rendering_mode in [RenderingMode.MARKDOWN, RenderingMode.MARKDOWNX]:
            return "---\n\n"
        elif rendering_mode == RenderingMode.HTML:
            return "<hr/>\n"

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


class Embed(BaseBlock):
    url: str

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        if rendering_mode in [RenderingMode.MARKDOWN, RenderingMode.MARKDOWNX]:
            return f"{self.indent_space}<iframe src='{self.url}'></iframe>\n"
        elif rendering_mode == RenderingMode.HTML:
            return f"{self.indent_space}<iframe src='{self.url}'></iframe>\n"

    def generate_html_start_tag(self) -> str:
        return ""

    def generate_html_end_tag(self) -> str:
        return ""


class Equation(BaseBlock):
    expression: str

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        if rendering_mode in [RenderingMode.MARKDOWN, RenderingMode.MARKDOWNX]:
            return f"{self.indent_space}$$ {self.expression} $$\n\n"
        elif rendering_mode == RenderingMode.HTML:
            return f"{self.indent_space}<div class='equation'>{self.expression}</div>\n"

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


class XFile(BaseBlock):
    type: FileType
    caption: Optional[List[RichText]] = None
    file: Optional[Union[NotionHostedFile, NotionExternalFile]] = None
    name: str

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        url = None
        if self.type == FileType.FILE:
            url = self.file.url
        elif self.type == FileType.EXTERNAL:
            url = self.file.url

        response = requests.get(url)
        filepath = ""
        if response.status_code == 200:
            filepath = self.static_file_output_dir / self.name
            with open(filepath, "wb") as attached_file:
                attached_file.write(response.content)

        context_path = self.static_file_context_path + "/" + self.name

        if rendering_mode in [RenderingMode.MARKDOWN, RenderingMode.MARKDOWNX]:
            return f"{self.indent_space}[{self.name}]({context_path})\n\n"
        elif rendering_mode == RenderingMode.HTML:
            return f"{self.indent_space}<a href='{context_path}'>{self.name}</a>\n"

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


class Heading(BaseBlock):
    rich_text: List[RichText]
    color: NotionColorType = NotionColorType.DEFAULT
    is_toggleable: bool = False

    def generate_alink_tag(self) -> str:
        title = self._generate_richtext_to_plaintext()
        return f"{{#{title.replace(' ', '-').lower()}}}"

    def _generate_richtext_to_plaintext(self) -> str:
        markdown = []
        for rt in self.rich_text:
            if rt.type == RichTextType.TEXT:
                markdown.append(rt.plain_text)

        return f"{''.join(markdown)}"


class Heading1(Heading):
    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        if rendering_mode == RenderingMode.MARKDOWN:
            return f"{self.indent_space}# {generate_richtext_tag(self.rich_text, rendering_mode)}\n\n"
        elif rendering_mode == RenderingMode.MARKDOWNX:
            title = generate_richtext_tag(self.rich_text, rendering_mode)
            return f"{self.indent_space}# {title} {self.generate_alink_tag()}\n\n"
        elif rendering_mode == RenderingMode.HTML:
            return f"{self.indent_space}<h1>{generate_richtext_tag(self.rich_text, rendering_mode)}</h1>\n"

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


class Heading2(Heading):
    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        if rendering_mode == RenderingMode.MARKDOWN:
            return f"{self.indent_space}## {generate_richtext_tag(self.rich_text, rendering_mode)}\n\n"
        elif rendering_mode == RenderingMode.MARKDOWNX:
            title = generate_richtext_tag(self.rich_text, rendering_mode)
            return f"{self.indent_space}## {title} {self.generate_alink_tag()}\n\n"
        elif rendering_mode == RenderingMode.HTML:
            return f"{self.indent_space}<h2>{generate_richtext_tag(self.rich_text, rendering_mode)}</h2>\n"

    def generate_html_start_tag(self) -> str:
        return ""

    def generate_html_end_tag(self) -> str:
        return ""


class Heading3(Heading):
    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        if rendering_mode == RenderingMode.MARKDOWN:
            return f"{self.indent_space}### {generate_richtext_tag(self.rich_text, rendering_mode)}\n\n"
        elif rendering_mode == RenderingMode.MARKDOWNX:
            title = generate_richtext_tag(self.rich_text, rendering_mode)
            return f"{self.indent_space}### {title} {self.generate_alink_tag()}\n\n"
        elif rendering_mode == RenderingMode.HTML:
            return f"{self.indent_space}<h3>{generate_richtext_tag(self.rich_text, rendering_mode)}</h3>\n"

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


def download_image(url: str, destination_file: Path) -> Path:
    try:
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()

            if response.status_code == 200:
                with open(destination_file, "wb") as img_file:
                    img_file.write(response.content)
                    log.info(f"Downloaded image: {destination_file}")
                return destination_file
            else:
                log.error(
                    f"Error downloading image: {url} {destination_file} - {response.status_code}"
                )
                return None
    except Exception as e:
        log.error(f"Error downloading image: {url} {destination_file} - {e}")
        return None


class Image(File, BaseBlock):
    caption: Optional[List[RichText]] = None

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        alt = (
            generate_richtext_tag(self.caption, rendering_mode) if self.caption else ""
        )
        url = ""
        filename = ""
        if self.type == FileType.FILE:
            url = self.file.url
            filename = self.id + ".png"
        elif self.type == FileType.EXTERNAL:
            url = self.external.url
            filename = self.id + "_" + self.get_file_name_from_url(url)

        # response = requests.get(url)
        # if response.status_code == 200:
        #     filepath = self.static_file_output_dir / filename
        #     with open(filepath, "wb") as img_file:
        #         img_file.write(response.content)

        _executor.submit(download_image, url, self.static_file_output_dir / filename)

        context_path = self.static_file_context_path + "/" + filename

        if rendering_mode in [RenderingMode.MARKDOWN, RenderingMode.MARKDOWNX]:
            return f"{self.indent_space}![{alt}]({context_path})\n\n"
        elif rendering_mode == RenderingMode.HTML:
            return f"{self.indent_space}<img src='{context_path}' alt='{alt}'/>\n"

    def generate_html_start_tag(self) -> str:
        return ""

    def generate_html_end_tag(self) -> str:
        return ""


class LinkPreview(BaseBlock):
    url: str

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        if rendering_mode in [RenderingMode.MARKDOWN, RenderingMode.MARKDOWNX]:
            return f"{self.indent_space}[{self.url}]({self.url})\n\n"
        elif rendering_mode == RenderingMode.HTML:
            return f"{self.indent_space}<a href='{self.url}'>{self.url}</a>\n"

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


# Not supported
class LinkToPage(BaseBlock):
    url: Optional[str] = None
    page_id: Optional[str] = None

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        if rendering_mode in [RenderingMode.MARKDOWN, RenderingMode.MARKDOWNX]:
            if self.page_id:
                if validate_page_id(self.page_id):
                    context_path = self.docs_root_node.find_path_by_object_id(
                        self.page_id
                    )
                    linked_page_node = self.docs_root_node.find_by_object_id(
                        self.page_id
                    )
                    return f"{self.indent_space}[{linked_page_node.name}](/{context_path})\n\n"
                else:
                    return f"{self.indent_space}[{self.page_id}]({self.page_id})\n\n"
            elif self.url:
                if notion_page_id := get_notion_page_id(self.url):
                    context_path = self.docs_root_node.find_path_by_object_id(
                        notion_page_id
                    )
                    linked_page_node = self.docs_root_node.find_by_object_id(
                        notion_page_id
                    )
                    return f"{self.indent_space}[{linked_page_node.name}](/{context_path})\n\n"
                else:
                    return f"{self.indent_space}[{self.url}]({self.url})\n\n"
            else:
                return ""
        elif rendering_mode == RenderingMode.HTML:
            if self.page_id:
                if validate_page_id(self.page_id):
                    context_path = self.docs_root_node.find_path_by_object_id(
                        self.page_id
                    )
                    linked_page_node = self.docs_root_node.find_by_object_id(
                        self.page_id
                    )
                    return f"{self.indent_space}<a href='/{context_path}'>{linked_page_node.name}</a>\n"
                else:
                    return f"{self.indent_space}<a href='{self.page_id}'>{self.page_id}</a>\n"
            elif self.url:
                if notion_page_id := get_notion_page_id(self.url):
                    context_path = self.docs_root_node.find_path_by_object_id(
                        notion_page_id
                    )
                    linked_page_node = self.docs_root_node.find_by_object_id(
                        notion_page_id
                    )
                    return f"{self.indent_space}<a href='/{context_path}'>{linked_page_node.name}</a>\n"
                else:
                    return f"{self.indent_space}<a href='{self.url}'>{self.url}</a>\n"
        else:
            return ""

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


class NumberedListItem(BaseBlock):
    rich_text: List[RichText]
    color: NotionColorType = NotionColorType.DEFAULT
    children: Optional[List[Block]] = None

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        if rendering_mode in [RenderingMode.MARKDOWN, RenderingMode.MARKDOWNX]:
            markdown = ""
            markdown += f"{self.indent_space}1. "
            markdown += generate_richtext_tag(self.rich_text, rendering_mode)
            markdown += "\n"
            return markdown
        elif rendering_mode == RenderingMode.HTML:
            html = ""
            html += f"{self.indent_space}<li>"
            html += generate_richtext_tag(self.rich_text, rendering_mode)
            html += "</li>\n"
            return html

    def generate_html_end_tag(self) -> str:
        return f"{self.indent_space}</ol>\n"

    def generate_html_start_tag(self) -> str:
        return f"{self.indent_space}<ol>\n"


class Paragraph(BaseBlock):
    rich_text: List[RichText]
    color: NotionColorType = NotionColorType.DEFAULT
    children: Optional[List[Block]] = None

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        if rendering_mode in [RenderingMode.MARKDOWN, RenderingMode.MARKDOWNX]:
            markdown = []
            for rt in self.rich_text:
                markdown.append(
                    rt.generate_richtext_tag(
                        rendering_mode=rendering_mode,
                        docs_root_node=self.docs_root_node,
                    )
                )

            if len(markdown) > 0:
                # markdownx doesn't support indent_space for paragraph block
                # return f"\n{self.indent_space}{''.join(markdown)}\n\n"
                return f"\n{''.join(markdown)}\n\n"
            else:
                return "\n"
        elif rendering_mode == RenderingMode.HTML:
            html = ""
            html += f"{self.indent_space}<p>"
            html += generate_richtext_tag(self.rich_text, rendering_mode)
            html += "</p>\n"
            return html

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


class PDF(BaseBlock):
    type: FileType
    caption: Optional[List[RichText]] = None
    external: Optional[File] = None
    file: Optional[File] = None

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        url = None
        if self.type == FileType.FILE:
            url = self.file.file.url
        elif self.type == FileType.EXTERNAL:
            url = self.file.external.url

        if rendering_mode in [RenderingMode.MARKDOWN, RenderingMode.MARKDOWNX]:
            return f"{self.indent_space}[{self.name}]({url})\n\n"
        elif rendering_mode == RenderingMode.HTML:
            return f"{self.indent_space}<a href='{url}'>{self.name}</a>\n"

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


class Quote(BaseBlock):
    rich_text: List[RichText]
    color: NotionColorType = NotionColorType.DEFAULT
    children: Optional[List[Block]] = None

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        if rendering_mode in [RenderingMode.MARKDOWN, RenderingMode.MARKDOWNX]:
            markdown = ""
            markdown += f"{self.indent_space}> "
            markdown += generate_richtext_tag(self.rich_text, rendering_mode)
            markdown += "\n\n"
            return markdown
        elif rendering_mode == RenderingMode.HTML:
            html = ""
            html += f"{self.indent_space}<blockquote>"
            html += generate_richtext_tag(self.rich_text, rendering_mode)
            html += "</blockquote>\n"
            return html

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


# Not supported
class SyncedBlock(BaseBlock):
    synced_from: Optional[str] = None
    children: Optional[List[Block]] = None

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        return ""

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


class Table(BaseBlock):
    table_width: int
    has_column_header: bool = False
    has_row_header: bool = False

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        if rendering_mode in [RenderingMode.MARKDOWN, RenderingMode.MARKDOWNX]:
            return ""
        elif rendering_mode == RenderingMode.HTML:
            return ""

    def generate_html_end_tag(self) -> str:
        return f"{self.indent_space}</table>\n"

    def generate_html_start_tag(self) -> str:
        return f"{self.indent_space}<table>\n"


class MarkdownTableHeaderRow(BaseBlock):
    cells_count: int

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        if rendering_mode in [RenderingMode.MARKDOWN, RenderingMode.MARKDOWNX]:
            md = ""
            row_data = []
            for _ in range(self.cells_count):
                row_data.append("---")

            md += f"{self.indent_space}| {' | '.join(row_data)} |\n"

            return md
        elif rendering_mode == RenderingMode.HTML:
            return ""

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


class TableRow(BaseBlock):
    cells: List[List[RichText]]

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        if rendering_mode in [RenderingMode.MARKDOWN, RenderingMode.MARKDOWNX]:
            md = ""
            row_data = []
            for cell in self.cells:
                cell_data = []
                for element in cell:
                    cell_data.append(
                        element.generate_richtext_tag(
                            rendering_mode=rendering_mode
                        ).replace("\n", "<br/>")
                    )
                row_data.append("".join(cell_data))

            md += f"{self.indent_space}| {' | '.join(row_data)} |\n"
            return md
        elif rendering_mode == RenderingMode.HTML:
            html = ""
            for cell in self.cells:
                html += f"{self.indent_space}<td>"
                for element in cell:
                    cell_data = element.generate_richtext_tag(
                        rendering_mode=rendering_mode
                    ).replace("\n", "<br/>")
                    html += f"{cell_data}"

                html += "</td>\n"
            return html

    def generate_html_end_tag(self) -> str:
        return f"{self.indent_space}</tr>\n"

    def generate_html_start_tag(self) -> str:
        return f"{self.indent_space}<tr>\n"


class TableOfContents(BaseBlock):
    color: NotionColorType = NotionColorType.DEFAULT

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        if rendering_mode == RenderingMode.MARKDOWN:
            return f"{self.indent_space}Table of Contents\n\n"
        elif rendering_mode == RenderingMode.MARKDOWNX:
            # https://docusaurus.io/docs/3.3.2/markdown-features/toc#table-of-contents-heading-level
            markdownx = ""
            markdownx += "---\n"
            markdownx += "toc_min_heading_level: 1\n"
            markdownx += "toc_max_heading_level: 3\n"
            markdownx += "---\n\n"
            return markdownx
        elif rendering_mode == RenderingMode.HTML:
            return f"{self.indent_space}Table of Contents\n"

        log.warning(f"Table of Contents block type: {rendering_mode}")
        return ""

    def generate_html_start_tag(self) -> str:
        return f"{self.indent_space}<div class='toc'>\n"

    def generate_html_end_tag(self) -> str:
        return f"{self.indent_space}</div>\n"


# @deprecated(reason="Template is not supported by Notion API")
class Template(BaseBlock):
    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""

    def generate_html_end_tag(self) -> str:
        return ""


class ToDo(BaseBlock):
    rich_text: List[RichText]
    color: NotionColorType = NotionColorType.DEFAULT
    checked: Optional[bool] = None
    children: Optional[List[Block]] = None

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        if rendering_mode in [RenderingMode.MARKDOWN, RenderingMode.MARKDOWNX]:
            markdown = ""
            markdown += f"{self.indent_space}- [{'x' if self.checked else ' '}] "
            markdown += generate_richtext_tag(self.rich_text, rendering_mode)
            markdown += "\n\n"
            return markdown
        elif rendering_mode == RenderingMode.HTML:
            html = ""
            html += f"{self.indent_space}<input type='checkbox' {'checked' if self.checked else ''}/>"
            html += generate_richtext_tag(self.rich_text, rendering_mode)
            html += "\n"
            return html

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


# Not Supported
class Toggle(BaseBlock):
    rich_text: List[RichText]
    color: NotionColorType = NotionColorType.DEFAULT
    children: Optional[List[Block]] = None

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        return ""

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


class Video(File, BaseBlock):
    """Support Youtube and video file"""

    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        url = self.file.url if self.type == FileType.FILE else self.external.url
        # ex) https://www.youtube.com/watch?v=0LIht9rTrVs&t=7802s
        if url.startswith("https://www.youtube.com/"):
            video_id = url.split("v=")[1].split("&")[0]
            src = f"https://www.youtube.com/embed/{video_id}"
            tag = (
                f"{self.indent_space}<iframe src='{src}' "
                "width='600px' height='400px' "
                "frameborder='0' "
                "allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture' "
                "allowfullscreen></iframe><br/>\n\n"
            )
        else:
            tag = f"{self.indent_space}<video src='{url}' controls></video><br/>\n\n"
        return tag

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


class Unsupported(BaseBlock):
    def generate_tag(
        self, *, rendering_mode: RenderingMode = RenderingMode.MARKDOWN
    ) -> str:
        return ""

    def generate_html_end_tag(self) -> str:
        return ""

    def generate_html_start_tag(self) -> str:
        return ""


def generate_richtext_tag(
    rich_text: List[RichText],
    rendering_mode: RenderingMode = RenderingMode.MARKDOWN,
    docs_root_node: Node | None = None,
) -> str:
    markdown = []
    for rt in rich_text:
        markdown.append(
            rt.generate_richtext_tag(
                rendering_mode=rendering_mode,
                docs_root_node=docs_root_node,
            )
        )

    return f"{''.join(markdown)}"


def get_notion_page_id(url: str) -> str | None:
    page_id = str.split(url, "/")[-1]
    transformed_page_id = transform_block_id_to_uuidv4(page_id)
    if validate_page_id(transformed_page_id):
        return transformed_page_id
    else:
        return None


def get_relative_path(from_path: Path, to_path: Path) -> Path:
    try:
        return to_path.relative_to(from_path)
    except ValueError:
        return Path(os.path.relpath(to_path, start=from_path))
