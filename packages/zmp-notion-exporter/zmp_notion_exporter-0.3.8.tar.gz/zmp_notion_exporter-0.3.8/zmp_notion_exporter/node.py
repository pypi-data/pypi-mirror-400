from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Node(BaseModel):
    object_id: str
    name: str
    is_directory: bool = False
    parent: Optional[Node] = None
    children: Optional[list[Node]] = None
    last_edited_time: Optional[datetime] = None
    last_edited_by: Optional[str] = None
    last_editor_avatar_url: Optional[str] = None
    notion_url: Optional[str] = None
    index: int = 1

    def model_post_init(self, __context) -> None:
        """Pydantic v2의 초기화 후처리 메서드"""
        super().model_post_init(__context)
        if self.is_directory and self.children is None:
            self.children = []
        elif not self.is_directory:
            self.children = None

    @property
    def total_pages(self) -> int:
        if self.children is None:
            if self.is_directory:
                return 0
            else:
                return 1

        total = sum(1 for child in self.children if not child.is_directory)
        total += sum(child.total_pages for child in self.children if child.is_directory)

        return total

    @property
    def total_directories(self) -> int:
        if self.children is None:
            return 0
        total = sum(1 for child in self.children if child.is_directory)
        total += sum(
            child.total_directories for child in self.children if child.is_directory
        )
        return total

    def add_child(self, child_node: Node):
        """Add a child node to the current node.

        Args:
            child_node (Node): The child node to add.

        Raises:
            ValueError: If the current node is not a directory.
        """
        if not self.is_directory:
            raise ValueError("Cannot add child to a file node")

        child_node.parent = self
        child_node.index = len(self.children) + 1

        if self.children is None:
            self.children = [child_node]
        else:
            self.children.append(child_node)

    def __custom_repr__(self) -> str:
        """Return a string representation of the node.

        Returns:
            str: A string representation of the node.
        """
        result = (
            f"Node(object_id={self.object_id}, "
            f"name={self.name}, "
            f"is_directory={self.is_directory}, "
            f"parent={self.parent.name if self.parent else None}, "
            f"total_pages={self.total_pages}, "
            f"total_directories={self.total_directories}, "
            f"last_edited_time={self.last_edited_time}, "
            f"last_edited_by={self.last_edited_by}, "
            f"last_editor_avatar_url={self.last_editor_avatar_url})"
        )
        if self.is_directory and self.children:
            for child in self.children:
                child_repr = str(
                    child
                )  # This will recursively call __repr__ on children
                child_lines = child_repr.split("\n")
                result += "\n" + "\n".join("    " + line for line in child_lines)
        return result

    def find_by_object_id(self, object_id: str) -> Node | None:
        """Find a node by its object ID.

        Args:
            object_id (str): The object ID to find.

        Returns:
            Node | None: The node with the given object ID, or None if it is not found.
        """
        if self.object_id == object_id:
            return self
        if self.is_directory and self.children:
            for child in self.children:
                found = child.find_by_object_id(object_id)
                if found is not None:
                    return found

        return None

    def find_path_by_object_id(self, object_id: str) -> str | None:
        """Find the path to a node by its object ID.

        Args:
            object_id (str): The object ID to find.

        Returns:
            str | None: The path to the node with the given object ID, or None if it is not found.
        """
        if self.object_id == object_id:
            return self.name
        if self.is_directory and self.children:
            for child in self.children:
                found = child.find_path_by_object_id(object_id)
                if found is not None:
                    return f"{self.name}/{found}"
        return None

    def find_by_name(self, name: str) -> Node | None:
        """Find a node by its name.

        Args:
            name (str): The name to find.

        Returns:
            Node | None: The node with the given name, or None if it is not found.
        """
        if self.is_directory and self.children:
            for child in self.children:
                found = child.find_by_name(name)
                if found is not None:
                    return found
        return None

    def find_path_by_name(self, name: str) -> str | None:
        """Find the path to a node by its name.

        Args:
            name (str): The name to find.

        Returns:
            str | None: The path to the node with the given name, or None if it is not found.
        """
        if self.is_directory and self.children:
            for child in self.children:
                found = child.find_path_by_name(name)
                if found is not None:
                    return f"{self.name}/{found}"
        return None

    def print_pretty(self, *, indent: int = 0, include_leaf_node: bool = False):
        """Print the node in a pretty format.

        Args:
            indent (int, optional): The indentation level. Defaults to 0.
        """
        if include_leaf_node:
            indent_space = ""
            if self.parent:
                if indent > 1:
                    indent_space = "    " * (indent - 1)
                else:
                    indent_space = ""
            else:
                indent_space = ""
            prefix = "└── " if self.parent else ""
            display_name = Path(self.name).name

            print(
                indent_space
                + prefix
                + display_name
                + ("/" if self.is_directory else "")
            )

            if self.is_directory and self.children:
                for child in self.children:
                    child.print_pretty(
                        indent=indent + 1, include_leaf_node=include_leaf_node
                    )
        else:
            if self.is_directory:
                indent_space = ""
                if self.parent:
                    if indent > 1:
                        indent_space = "    " * (indent - 1)
                    else:
                        indent_space = ""
                else:
                    indent_space = ""
                prefix = "└── " if self.parent else ""
                display_name = Path(self.name).name

                print(
                    indent_space
                    + prefix
                    + display_name
                    + ("/" if self.is_directory else "")
                )

                if self.is_directory and self.children:
                    for child in self.children:
                        child.print_pretty(
                            indent=indent + 1, include_leaf_node=include_leaf_node
                        )

    def create_directory(self) -> None:
        """Create directories recursively from root node to leaf nodes.
        Only creates directories for nodes where is_directory=True.
        """
        if self.is_directory:
            # Build full path by traversing up to root
            path_parts = []
            current = self
            while current:
                path_parts.append(current.name)
                current = current.parent

            # Reverse to get correct order from root to current
            full_path = Path(*reversed(path_parts))
            full_path.mkdir(parents=True, exist_ok=True)

            # Recursively create directories for children
            if self.children:
                for child in self.children:
                    if child.is_directory:
                        child.create_directory()
