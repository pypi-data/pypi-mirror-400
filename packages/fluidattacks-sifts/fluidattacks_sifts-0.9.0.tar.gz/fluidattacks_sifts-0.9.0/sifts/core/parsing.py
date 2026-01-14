import logging
from collections.abc import AsyncGenerator
from pathlib import Path

import aiofiles
from fluidattacks_core.serializers.syntax import (
    TREE_SITTER_FUNCTION_DECLARATION_MAP,
    InvalidFileType,
    get_language_from_path,
    parse_content_tree_sitter,
    query_nodes_by_language,
)
from tree_sitter import Node

LOGGER = logging.getLogger(__name__)


def search_nodes_in_tree(root_node: Node, line: int, node_types: tuple[str, ...]) -> Node | None:
    # Convert from 1-based (input) to 0-based (tree-sitter) for comparison
    line_0based = line - 1
    # First check if the current node is of the desired type and contains the line
    if (
        root_node.type in node_types
        and root_node.start_point[0] <= line_0based <= root_node.end_point[0]
    ):
        return root_node

    # If this node doesn't contain the line we're looking for, no need to search its children
    if line_0based < root_node.start_point[0] or line_0based > root_node.end_point[0]:
        return None

    # Search in the children of the current node
    for child in root_node.children:
        result = search_nodes_in_tree(child, line, node_types)
        if result:
            return result

    return None


def _is_top_level_function(node: Node, function_node_names: set[str]) -> bool:
    parent = node.parent
    while parent:
        if parent.type in function_node_names:
            return False  # It's nested
        parent = parent.parent
    return True  # It's top-level


async def process_file_for_functions(
    file_path: Path,
    working_dir: Path | None = None,
) -> AsyncGenerator[tuple[str, Node], None]:
    language = get_language_from_path(str(file_path))
    if not language:
        return
    try:
        async with aiofiles.open(file=file_path, mode="rb") as f:
            content = await f.read()
            try:
                tree = parse_content_tree_sitter(content, language)
            except (OSError, InvalidFileType):
                return
    except FileNotFoundError:
        return

    function_node_names = TREE_SITTER_FUNCTION_DECLARATION_MAP[language]
    function_nodes = query_nodes_by_language(
        language,
        tree,
        TREE_SITTER_FUNCTION_DECLARATION_MAP,
    )

    # Prevent minified files
    if (
        len(function_nodes) > 1
        and len({node.start_point[0] for node in (y for x in function_nodes.values() for y in x)})
        == 1
    ):
        return
    for node in (y for x in function_nodes.values() for y in x):
        if _is_top_level_function(node, set(function_node_names)):
            # Yield relative path from working_dir
            if working_dir:
                yield (str(file_path.relative_to(working_dir)), node)
            else:
                yield (str(file_path), node)
