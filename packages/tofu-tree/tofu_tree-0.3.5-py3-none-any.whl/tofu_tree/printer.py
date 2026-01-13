"""
Tree printer module for Terraform/OpenTofu plan tree output.

Uses position-based prefix logic similar to the Unix 'tree' command
to display hierarchical resource structures.
"""

from __future__ import annotations

import re
from typing import Any

# ANSI color codes
COLOR_GREEN = "\033[32m"
COLOR_RED = "\033[31m"
COLOR_YELLOW = "\033[33m"
COLOR_MAGENTA = "\033[35m"
COLOR_RESET = "\033[0m"

# Position types
ONLY = "only"
FIRST = "first"
MIDDLE = "middle"
LAST = "last"

# Connectors per position
CONNECTORS: dict[str, str] = {
    ONLY: "└── ",
    FIRST: "├── ",
    MIDDLE: "├── ",
    LAST: "└── ",
}

# Inherited prefix per position (for children)
INHERITED: dict[str, str] = {
    ONLY: "    ",
    FIRST: "│   ",
    MIDDLE: "│   ",
    LAST: "    ",
}


def color_symbol(symbol: str, use_color: bool = False) -> str:
    """
    Color the symbol based on its value.

    Args:
        symbol: The symbol to color (+/-/~)
        use_color: Whether to apply ANSI colors

    Returns:
        Colored symbol string if use_color is True, otherwise plain symbol.
    """
    if not use_color:
        return symbol

    color_map = {
        "+": COLOR_GREEN,
        "-": COLOR_RED,
        "±": COLOR_MAGENTA,
        "~": COLOR_YELLOW,
    }

    color_code = color_map.get(symbol, "")
    return f"{color_code}{symbol}{COLOR_RESET}" if color_code else symbol


# Symbol display order for concatenation
SYMBOL_ORDER: list[str] = ["+", "-", "±", "~"]


def collect_symbols_from_node(node: dict[str, Any] | list[Any]) -> set[str]:
    """
    Recursively collect all unique symbols from a node.

    Args:
        node: A tree node (dict or list)

    Returns:
        Set of unique symbol strings found in the node.
    """
    symbols: set[str] = set()

    if isinstance(node, list):
        for item in node:
            if isinstance(item, dict):
                if "resource" in item:
                    symbols.add(item["resource"]["symbol"])
                if "children" in item:
                    symbols.update(collect_symbols_from_node(item["children"]))
    elif isinstance(node, dict):
        if "resources" in node:
            for r in node["resources"]:
                symbols.add(r["symbol"])
        if "children" in node:
            symbols.update(collect_symbols_from_node(node["children"]))
        for key, value in node.items():
            if key not in ["resources", "children"] and isinstance(value, (dict, list)):
                symbols.update(collect_symbols_from_node(value))

    return symbols


def format_symbols(symbols: set[str], use_color: bool = False) -> str:
    """
    Format a set of symbols as a concatenated, colored string.

    Args:
        symbols: Set of symbols to format
        use_color: Whether to apply ANSI colors

    Returns:
        Concatenated symbols in order, with colors if enabled.
    """
    if not symbols:
        return ""

    ordered = [s for s in SYMBOL_ORDER if s in symbols]
    colored = [color_symbol(s, use_color) for s in ordered]
    return "".join(colored) + " "


class TreePrinter:
    """
    Prints tree structures with position-based prefixes.

    Creates beautiful tree output similar to the Unix 'tree' command,
    with proper connectors (├──, └──) and vertical lines (│).

    Example:
        >>> printer = TreePrinter(use_color=True)
        >>> printer.print_tree(graph.get_tree())
        >>> printer.print_summary(graph.get_resources())
    """

    def __init__(self, use_color: bool = False) -> None:
        """
        Initialize the tree printer.

        Args:
            use_color: Whether to use ANSI colors for symbols.
        """
        self.use_color = use_color

    def print_tree(self, node: dict[str, Any], inherited_prefix: str = "") -> None:
        """
        Print the tree structure using position-based prefixes.

        Args:
            node: The tree node (dict) to print
            inherited_prefix: Accumulated prefix from all ancestors
        """
        if not isinstance(node, dict):
            return

        keys = self._get_sorted_keys(node)
        is_root_level = inherited_prefix == ""

        # Handle case where node only has "resources" (leaf node with no other keys)
        if "resources" in node and not keys:
            self._print_resources_leaf(node["resources"], inherited_prefix)
            return

        for i, key in enumerate(keys):
            value = node[key]

            # Determine position
            if len(keys) == 1:
                position = ONLY
            elif i == 0:
                position = FIRST
            elif i == len(keys) - 1:
                position = LAST
            else:
                position = MIDDLE

            # Build current line prefix
            connector = CONNECTORS[position]
            current_prefix = inherited_prefix + connector

            # Build inherited prefix for children
            if is_root_level:
                next_inherited = INHERITED[FIRST]
            else:
                next_inherited = inherited_prefix + INHERITED[position]

            # Print node header
            if isinstance(value, list):
                self._print_list_node(
                    value, key, current_prefix, next_inherited, is_root_level
                )
            elif isinstance(value, dict):
                self._print_dict_node(
                    value, key, current_prefix, next_inherited, is_root_level
                )

    def _get_sorted_keys(self, node: dict[str, Any]) -> list[str]:
        """Get sorted keys excluding internal keys."""
        return sorted([k for k in node if k not in ["children", "resources"]])

    def _print_list_node(
        self,
        value: list[Any],
        key: str,
        current_prefix: str,
        next_inherited: str,
        is_root_level: bool,
    ) -> None:
        """Print a node that contains a list of indexed items."""
        symbols = collect_symbols_from_node(value)
        symbol_str = format_symbols(symbols, self.use_color)

        if is_root_level:
            print(f"{symbol_str}{key}")
            if next_inherited == INHERITED[FIRST]:
                next_inherited = "│  "
        else:
            print(f"{current_prefix}{symbol_str}{key}")

        sorted_items = sorted(value, key=lambda x: x.get("key", ""))
        for j, item in enumerate(sorted_items):
            item_position = self._get_position(j, len(sorted_items))
            item_connector = CONNECTORS[item_position]
            item_prefix = next_inherited + item_connector
            item_next_inherited = next_inherited + INHERITED[item_position]

            self._print_list_item(item, item_prefix, item_next_inherited)
            if item_position in (LAST, ONLY):
                print(item_next_inherited)

    def _print_dict_node(
        self,
        value: dict[str, Any],
        key: str,
        current_prefix: str,
        next_inherited: str,
        is_root_level: bool,
    ) -> None:
        """Print a dict node, handling different dict structures."""
        if "children" in value:
            self._print_dict_with_children(
                value, key, current_prefix, next_inherited, is_root_level
            )
        elif "resources" in value:
            self._print_dict_with_resources(
                value, key, current_prefix, next_inherited, is_root_level
            )
        else:
            self._print_dict_node_only(
                value, key, current_prefix, next_inherited, is_root_level
            )

    def _print_dict_with_children(
        self,
        value: dict[str, Any],
        key: str,
        current_prefix: str,
        next_inherited: str,
        is_root_level: bool,
    ) -> None:
        """Print a dict node that has children."""
        children = value["children"]
        child_keys = sorted([k for k in children if k != "resources"])
        has_resources = "resources" in children

        # If only resources (no child keys), combine type and name on same line
        if has_resources and not child_keys:
            resources = children["resources"]
            sorted_resources = sorted(
                resources, key=lambda r: self._extract_resource_name(r["address"])
            )
            for k, resource in enumerate(sorted_resources):
                res_position = self._get_position(k, len(sorted_resources))
                if is_root_level:
                    res_prefix = ""
                    res_next_inherited = ""
                else:
                    res_connector = CONNECTORS[res_position]
                    res_prefix = current_prefix[:-4] + res_connector
                    res_next_inherited = current_prefix[:-4] + INHERITED[res_position]

                name = self._extract_resource_name(resource["address"])
                colored_symbol = color_symbol(resource["symbol"], self.use_color)
                print(f"{res_prefix}{colored_symbol} {key}.{name}")

                if res_position in (LAST, ONLY) and res_next_inherited:
                    print(res_next_inherited)
            return

        # Check if children are only simple types (lists or leaf dicts with only resources)
        # If so, flatten them all with parent prefix
        all_children_are_flat = child_keys and all(
            isinstance(children[k], list)
            or (
                isinstance(children[k], dict)
                and "children" in children[k]
                and "resources" in children[k]["children"]
                and not any(
                    kk not in ["resources", "children"]
                    for kk in children[k]["children"]
                )
            )
            for k in child_keys
        )

        is_module = key.startswith("module.")
        should_flatten = all_children_are_flat or (has_resources and not child_keys)

        if should_flatten:
            all_items: list[tuple[str, Any]] = []

            # Add non-indexed resources
            if has_resources:
                for resource in children["resources"]:
                    name = self._extract_resource_name(resource["address"])
                    all_items.append(("resource", name, resource))

            # Add indexed resources (lists) and leaf dicts
            for child_key in child_keys:
                child_value = children[child_key]
                if isinstance(child_value, list):
                    all_items.append(("list", child_key, child_value))
                elif isinstance(child_value, dict) and "children" in child_value:
                    child_children = child_value["children"]
                    if "resources" in child_children:
                        for resource in child_children["resources"]:
                            name = self._extract_resource_name(resource["address"])
                            all_items.append(
                                ("resource", f"{child_key}.{name}", resource)
                            )

            # Sort items
            all_items.sort(key=lambda x: x[1])

            # For modules at root, print module header first
            if is_module and is_root_level:
                symbols = collect_symbols_from_node(value)
                symbol_str = format_symbols(symbols, self.use_color)
                print(f"{symbol_str}{key}")
                base_inherited = "│  "
            else:
                base_inherited = next_inherited

            for idx, item in enumerate(all_items):
                item_type, item_key, item_value = item
                item_position = self._get_position(idx, len(all_items))

                if is_module and is_root_level:
                    item_connector = CONNECTORS[item_position]
                    item_prefix = base_inherited + item_connector
                    item_next_inherited = base_inherited + INHERITED[item_position]
                elif is_root_level:
                    item_prefix = ""
                    item_next_inherited = ""
                else:
                    item_connector = CONNECTORS[item_position]
                    item_prefix = current_prefix[:-4] + item_connector
                    item_next_inherited = current_prefix[:-4] + INHERITED[item_position]

                if item_type == "resource":
                    colored_symbol = color_symbol(item_value["symbol"], self.use_color)
                    if is_module and is_root_level:
                        print(f"{item_prefix}{colored_symbol} {item_key}")
                    else:
                        print(f"{item_prefix}{colored_symbol} {key}.{item_key}")
                    if is_root_level and not is_module:
                        print()
                    elif item_position in (LAST, ONLY):
                        print(item_next_inherited)
                elif item_type == "list":
                    list_symbols = collect_symbols_from_node(item_value)
                    list_symbol_str = format_symbols(list_symbols, self.use_color)
                    if is_module and is_root_level:
                        print(f"{item_prefix}{list_symbol_str}{item_key}")
                    else:
                        print(f"{item_prefix}{list_symbol_str}{key}.{item_key}")

                    if is_root_level and not is_module:
                        list_next_inherited = "│  "
                    else:
                        list_next_inherited = item_next_inherited

                    sorted_items = sorted(item_value, key=lambda x: x.get("key", ""))
                    for k, list_item in enumerate(sorted_items):
                        li_position = self._get_position(k, len(sorted_items))
                        li_connector = CONNECTORS[li_position]
                        li_prefix = list_next_inherited + li_connector
                        li_next_inherited = list_next_inherited + INHERITED[li_position]
                        self._print_list_item(list_item, li_prefix, li_next_inherited)
                        if li_position in (LAST, ONLY):
                            print(li_next_inherited)
            return

        symbols = collect_symbols_from_node(value)
        symbol_str = format_symbols(symbols, self.use_color)

        if is_root_level:
            print(f"{symbol_str}{key}")
            next_inherited = "│  "
        else:
            print(f"{current_prefix}{symbol_str}{key}")

        if has_resources:
            resources = children["resources"]
            sorted_resources = sorted(
                resources, key=lambda r: self._extract_resource_name(r["address"])
            )

            has_children_after = len(child_keys) > 0

            for k, resource in enumerate(sorted_resources):
                if has_children_after:
                    res_position = FIRST if k == 0 else MIDDLE
                else:
                    res_position = self._get_position(k, len(sorted_resources))

                res_connector = CONNECTORS[res_position]
                res_prefix = next_inherited + res_connector
                res_next_inherited = next_inherited + INHERITED[res_position]

                name = self._extract_resource_name(resource["address"])
                colored_symbol = color_symbol(resource["symbol"], self.use_color)
                print(f"{res_prefix}{colored_symbol} {name}")

                if res_position in (LAST, ONLY):
                    print(res_next_inherited)

        for j, child_key in enumerate(child_keys):
            child_position = self._get_position(j, len(child_keys))
            child_connector = CONNECTORS[child_position]
            child_prefix = next_inherited + child_connector
            child_next_inherited = next_inherited + INHERITED[child_position]

            child_value = children[child_key]
            if isinstance(child_value, dict) and "children" in child_value:
                child_children = child_value["children"]
                # Check if this is a leaf node with only resources (no nested keys)
                child_child_keys = [
                    k for k in child_children if k not in ["children", "resources"]
                ]
                if "resources" in child_children and not child_child_keys:
                    # Combine resource type and name on same line
                    resources = child_children["resources"]
                    sorted_resources = sorted(
                        resources,
                        key=lambda r: self._extract_resource_name(r["address"]),
                    )
                    for k, resource in enumerate(sorted_resources):
                        # Adjust position based on whether this is last child
                        if j == len(child_keys) - 1:
                            res_position = self._get_position(k, len(sorted_resources))
                        else:
                            res_position = FIRST if k == 0 else MIDDLE
                        res_connector = CONNECTORS[res_position]
                        res_prefix = next_inherited + res_connector
                        res_next_inherited = next_inherited + INHERITED[res_position]

                        name = self._extract_resource_name(resource["address"])
                        colored_symbol = color_symbol(resource["symbol"], self.use_color)
                        print(f"{res_prefix}{colored_symbol} {child_key}.{name}")

                        if res_position in (LAST, ONLY):
                            print(res_next_inherited)
                # Check if children are only lists (indexed resources)
                elif all(
                    isinstance(child_children.get(k), list)
                    for k in child_child_keys
                ):
                    # Combine parent.child and print list items under it
                    for kk, grandchild_key in enumerate(sorted(child_child_keys)):
                        grandchild_value = child_children[grandchild_key]
                        gc_position = self._get_position(kk, len(child_child_keys))
                        if j == len(child_keys) - 1:
                            gc_position = self._get_position(kk, len(child_child_keys))
                        else:
                            gc_position = FIRST if kk == 0 else MIDDLE
                        gc_connector = CONNECTORS[gc_position]
                        gc_prefix = next_inherited + gc_connector
                        gc_next_inherited = next_inherited + INHERITED[gc_position]

                        gc_symbols = collect_symbols_from_node(grandchild_value)
                        gc_symbol_str = format_symbols(gc_symbols, self.use_color)
                        print(f"{gc_prefix}{gc_symbol_str}{child_key}.{grandchild_key}")

                        sorted_items = sorted(
                            grandchild_value, key=lambda x: x.get("key", "")
                        )
                        for m, item in enumerate(sorted_items):
                            item_position = self._get_position(m, len(sorted_items))
                            item_connector = CONNECTORS[item_position]
                            item_prefix = gc_next_inherited + item_connector
                            item_next_inherited = (
                                gc_next_inherited + INHERITED[item_position]
                            )
                            self._print_list_item(item, item_prefix, item_next_inherited)
                            if item_position in (LAST, ONLY):
                                print(item_next_inherited)
                else:
                    child_symbols = collect_symbols_from_node(child_value)
                    child_symbol_str = format_symbols(child_symbols, self.use_color)
                    print(f"{child_prefix}{child_symbol_str}{child_key}")
                    self.print_tree(child_children, child_next_inherited)
            elif isinstance(child_value, list):
                child_symbols = collect_symbols_from_node(child_value)
                child_symbol_str = format_symbols(child_symbols, self.use_color)
                print(f"{child_prefix}{child_symbol_str}{child_key}")
                sorted_items = sorted(child_value, key=lambda x: x.get("key", ""))
                for k, item in enumerate(sorted_items):
                    item_position = self._get_position(k, len(sorted_items))
                    item_connector = CONNECTORS[item_position]
                    item_prefix = child_next_inherited + item_connector
                    item_next_inherited = (
                        child_next_inherited + INHERITED[item_position]
                    )

                    self._print_list_item(item, item_prefix, item_next_inherited)
                    if item_position in (LAST, ONLY):
                        print(item_next_inherited)
            else:
                self.print_tree({child_key: child_value}, child_next_inherited)

    def _print_dict_with_resources(
        self,
        value: dict[str, Any],
        key: str,
        current_prefix: str,
        next_inherited: str,
        is_root_level: bool,
    ) -> None:
        """Print a dict node that has resources."""
        resources = value["resources"]
        sorted_resources = sorted(
            resources, key=lambda r: self._extract_resource_name(r["address"])
        )

        # Print resource type and name on same line (e.g., random_string.updatable)
        for k, resource in enumerate(sorted_resources):
            res_position = self._get_position(k, len(sorted_resources))
            if is_root_level:
                res_prefix = ""
            else:
                res_connector = CONNECTORS[res_position]
                res_prefix = current_prefix[:-4] + res_connector  # Adjust prefix
            res_next_inherited = (
                current_prefix[:-4] + INHERITED[res_position] if not is_root_level else ""
            )

            name = self._extract_resource_name(resource["address"])
            colored_symbol = color_symbol(resource["symbol"], self.use_color)
            print(f"{res_prefix}{colored_symbol} {key}.{name}")

            if res_position in (LAST, ONLY):
                if res_next_inherited:
                    print(res_next_inherited)

            name = self._extract_resource_name(resource["address"])
            colored_symbol = color_symbol(resource["symbol"], self.use_color)
            print(f"{res_prefix}{colored_symbol} {name}")

            if res_position in (LAST, ONLY):
                print(res_next_inherited)

    def _print_dict_node_only(
        self,
        value: dict[str, Any],
        key: str,
        current_prefix: str,
        next_inherited: str,
        is_root_level: bool,
    ) -> None:
        """Print a dict node without explicit children or resources."""
        symbols = collect_symbols_from_node(value)
        symbol_str = format_symbols(symbols, self.use_color)

        if is_root_level:
            print(f"{symbol_str}{key}")
        else:
            print(f"{current_prefix}{symbol_str}{key}")

        self.print_tree(value, next_inherited)

    def _print_list_item(
        self,
        item: dict[str, Any],
        item_prefix: str,
        item_next_inherited: str,
    ) -> None:
        """Print a single item from a list node."""
        if "resource" in item:
            resource = item["resource"]
            colored_symbol = color_symbol(resource["symbol"], self.use_color)
            # Just show the key, not the resource name (parent already shown)
            print(f"{item_prefix}{colored_symbol} {item['key']}")
        elif "children" in item:
            print(f"{item_prefix}{item['key']}")
            self.print_tree(item["children"], item_next_inherited)

    def _print_resources_leaf(
        self,
        resources: list[dict[str, str]],
        inherited_prefix: str,
    ) -> None:
        """Print resources when they are the only content in a node."""
        sorted_resources = sorted(
            resources, key=lambda r: self._extract_resource_name(r["address"])
        )

        for k, resource in enumerate(sorted_resources):
            res_position = self._get_position(k, len(sorted_resources))
            res_connector = CONNECTORS[res_position]
            res_prefix = inherited_prefix + res_connector
            res_next_inherited = inherited_prefix + INHERITED[res_position]

            name = self._extract_resource_name(resource["address"])
            colored_symbol = color_symbol(resource["symbol"], self.use_color)
            print(f"{res_prefix}{colored_symbol} {name}")

            if res_position in (LAST, ONLY):
                print(res_next_inherited)

    def _get_position(self, index: int, total: int) -> str:
        """
        Determine position based on index and total count.

        Args:
            index: Current index (0-based)
            total: Total number of items

        Returns:
            Position string (ONLY, FIRST, MIDDLE, or LAST)
        """
        if total == 1:
            return ONLY
        elif index == 0:
            return FIRST
        elif index == total - 1:
            return LAST
        else:
            return MIDDLE

    def _extract_resource_name(self, address: str) -> str:
        """Extract resource name from address, removing index brackets."""
        return re.sub(r"\[.*\]", "", address.split(".")[-1])

    def print_summary(self, resources: list[dict[str, str]]) -> None:
        """
        Print summary of resource changes.

        Args:
            resources: List of resource dictionaries
        """
        SUMMARY_WIDTH = 3
        counts = self._count_resources_by_symbol(resources)

        created_symbol = color_symbol("+", self.use_color)
        destroyed_symbol = color_symbol("-", self.use_color)
        replaced_symbol = color_symbol("±", self.use_color)
        updated_symbol = color_symbol("~", self.use_color)

        print(f"{created_symbol} {counts['+']:{SUMMARY_WIDTH}d} to be created")
        print(f"{destroyed_symbol} {counts['-']:{SUMMARY_WIDTH}d} to be destroyed")
        print(f"{replaced_symbol} {counts['±']:{SUMMARY_WIDTH}d} to be replaced")
        print(f"{updated_symbol} {counts['~']:{SUMMARY_WIDTH}d} to be updated")

    def _count_resources_by_symbol(
        self, resources: list[dict[str, str]]
    ) -> dict[str, int]:
        """Count resources grouped by their symbol."""
        counts: dict[str, int] = {"+": 0, "-": 0, "±": 0, "~": 0}

        for resource in resources:
            symbol = resource.get("symbol", "?")
            if symbol in counts:
                counts[symbol] += 1

        return counts
