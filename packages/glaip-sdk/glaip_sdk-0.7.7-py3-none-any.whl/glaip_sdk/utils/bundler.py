"""Tool source code bundling with import inlining.

This module provides the ToolBundler class for bundling Python tool source
code with all local dependencies inlined.

Authors:
    Christian Trisno Sen Long Chen (christian.t.s.l.chen@gdplabs.id)
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

from glaip_sdk.utils.import_resolver import ImportResolver
from glaip_sdk.utils.tool_detection import is_tool_plugin_decorator


class ToolBundler:
    """Bundles tool source code with inlined local imports.

    This class handles the complex process of taking a tool class and
    producing a single, self-contained source file with all local
    dependencies inlined.

    Attributes:
        tool_class: The tool class to bundle.
        tool_file: Path to the file containing the tool class.
        tool_dir: Directory containing the tool file.

    Example:
        >>> bundler = ToolBundler(MyToolClass)
        >>> bundled_source = bundler.bundle()
    """

    def __init__(self, tool_class: type) -> None:
        """Initialize the ToolBundler.

        Args:
            tool_class: The tool class or decorated function to bundle.
        """
        # If it's a gllm_core Tool, get the underlying function
        if hasattr(tool_class, "__wrapped__"):
            actual_func = tool_class.__wrapped__
        else:
            actual_func = tool_class

        self.tool_class = tool_class
        self.tool_file = Path(inspect.getfile(actual_func))
        self.tool_dir = self.tool_file.parent
        self._import_resolver = ImportResolver(self.tool_dir)

    def bundle(self, add_tool_plugin_decorator: bool = True) -> str:
        """Bundle tool source code with inlined local imports.

        Args:
            add_tool_plugin_decorator: If True, add @tool_plugin decorator to BaseTool classes.
                Set to False for newer servers (0.1.85+) where decorator is optional.
                Defaults to True for backward compatibility with older servers.

        Returns:
            Bundled source code with all local dependencies inlined.
        """
        with open(self.tool_file, encoding="utf-8") as f:
            full_source = f.read()

        tree = ast.parse(full_source)
        local_imports, external_imports = self._import_resolver.categorize_imports(tree)

        # NOTE: The @tool_plugin decorator is REQUIRED by older servers (< 0.1.85) for remote execution.
        # Newer servers (0.1.85+) make the decorator optional.
        # The server validates uploaded tool code and will reject tools without the decorator
        # with error: "No classes found with @tool_plugin decorator".
        # See: docs/resources/reference/schemas/tools.md - "Plugin Requirements"
        # TESTED: Commenting out this decorator addition causes HTTP 400 ValidationError from older servers.
        # We try without decorator first (for new servers), then retry with decorator if validation fails.
        if add_tool_plugin_decorator:
            self._add_tool_plugin_decorator(tree)

        # Extract main code nodes (excluding imports, docstrings, glaip_sdk.Tool subclasses)
        main_code_nodes = self._extract_main_code_nodes(tree)

        # Inline local imports and collect their external imports
        inlined_code, inlined_external_imports = self._import_resolver.inline_local_imports(local_imports)

        # Merge all external imports
        all_external_imports = external_imports + inlined_external_imports

        # NOTE: The gllm_plugin.tools import is REQUIRED when decorator is added.
        # Without this import, the decorator will cause a NameError when the server executes the code.
        # TESTED: Commenting out this import causes NameError when server tries to use the decorator.
        # This import is added automatically during bundling so source files can remain clean.
        if add_tool_plugin_decorator:
            self._ensure_tool_plugin_import(all_external_imports)

        # Build bundled code
        bundled_code = ["# Bundled tool with inlined local imports\n"]
        bundled_code.extend(self._import_resolver.format_external_imports(all_external_imports))

        # Add inlined dependencies FIRST (before main tool code)
        bundled_code.extend(inlined_code)

        # Then add main tool code
        bundled_code.append("# Main tool code\n")
        for node_code in main_code_nodes:
            bundled_code.append(node_code + "\n")
        bundled_code.append("\n")

        return "".join(bundled_code)

    def _extract_main_code_nodes(self, tree: ast.AST) -> list[str]:
        """Extract main code nodes from AST, excluding imports and Tool subclasses.

        Args:
            tree: AST tree of the source file.

        Returns:
            List of unparsed code node strings.
        """
        main_code_nodes = []
        for node in tree.body:
            # Skip imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            # Skip module docstrings
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                continue
            # Skip glaip_sdk.Tool subclasses
            if isinstance(node, ast.ClassDef) and self._is_sdk_tool_subclass(node):
                continue
            main_code_nodes.append(ast.unparse(node))
        return main_code_nodes

    @staticmethod
    def _add_tool_plugin_decorator(tree: ast.AST) -> None:
        """Add @tool_plugin decorator to BaseTool classes that don't have it.

        This allows tools to be clean (without decorator) for local use,
        while the decorator is automatically added during bundling for remote execution.

        Args:
            tree: AST tree to modify in-place.
        """
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            if not ToolBundler._inherits_from_base_tool(node):
                continue

            if ToolBundler._has_tool_plugin_decorator(node):
                continue

            decorator_call = ToolBundler._create_tool_plugin_decorator()
            node.decorator_list.insert(0, decorator_call)

    @staticmethod
    def _inherits_from_base_tool(class_node: ast.ClassDef) -> bool:
        """Check if a class inherits from BaseTool.

        Args:
            class_node: AST ClassDef node to check.

        Returns:
            True if class inherits from BaseTool.
        """
        for base in class_node.bases:
            if isinstance(base, ast.Name) and base.id == "BaseTool":
                return True
            if isinstance(base, ast.Attribute) and base.attr == "BaseTool":
                # Handle nested attributes like langchain_core.tools.BaseTool
                # Check if the value chain leads to langchain_core
                value = base.value
                while isinstance(value, ast.Attribute):
                    value = value.value
                if isinstance(value, ast.Name) and value.id == "langchain_core":
                    return True
        return False

    @staticmethod
    def _has_tool_plugin_decorator(class_node: ast.ClassDef) -> bool:
        """Check if a class already has the @tool_plugin decorator.

        Args:
            class_node: AST ClassDef node to check.

        Returns:
            True if decorator already exists.
        """
        for decorator in class_node.decorator_list:
            if is_tool_plugin_decorator(decorator):
                return True
        return False

    @staticmethod
    def _create_tool_plugin_decorator() -> ast.Call:
        """Create a @tool_plugin decorator AST node.

        Returns:
            AST Call node representing @tool_plugin(version="1.0.0").
        """
        return ast.Call(
            func=ast.Name(id="tool_plugin", ctx=ast.Load()),
            args=[],
            keywords=[ast.keyword(arg="version", value=ast.Constant(value="1.0.0"))],
        )

    @staticmethod
    def _ensure_tool_plugin_import(external_imports: list) -> None:
        """Ensure gllm_plugin.tools import is present in external imports.

        Args:
            external_imports: List of external import nodes (modified in-place).
        """
        # Check if import already exists
        for import_node in external_imports:
            if isinstance(import_node, ast.ImportFrom) and import_node.module == "gllm_plugin.tools":
                # Check if tool_plugin is in the names
                for alias in import_node.names:
                    if alias.name == "tool_plugin":
                        return  # Import already present

        # Add the import
        import_node = ast.ImportFrom(
            module="gllm_plugin.tools",
            names=[ast.alias(name="tool_plugin")],
            level=0,
        )
        external_imports.append(import_node)

    @staticmethod
    def _is_sdk_tool_subclass(node: ast.ClassDef) -> bool:
        """Check if AST class definition inherits from Tool.

        These classes are only needed locally for upload configuration
        and should be excluded from bundled code.

        Args:
            node: AST ClassDef node to check.

        Returns:
            True if class inherits from Tool.
        """
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Tool":
                return True
            if (
                isinstance(base, ast.Attribute)
                and base.attr == "Tool"
                and isinstance(base.value, ast.Name)
                and base.value.id in ("glaip_sdk",)
            ):
                return True
        return False

    @classmethod
    def bundle_from_source(cls, file_path: Path, add_tool_plugin_decorator: bool = True) -> tuple[str, str, str]:
        """Extract tool info directly from source file without importing.

        This is used as a fallback when the tool class cannot be imported
        due to missing dependencies.

        Args:
            file_path: Path to the tool source file.
            add_tool_plugin_decorator: If True, add @tool_plugin decorator to BaseTool classes.
                Set to False for newer servers (0.1.85+) where decorator is optional.
                Defaults to True for backward compatibility with older servers.

        Returns:
            Tuple of (name, description, bundled_source_code).

        Raises:
            FileNotFoundError: If the source file doesn't exist.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Tool source file not found: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            source_code = f.read()

        tree = ast.parse(source_code)
        tool_dir = file_path.parent
        import_resolver = ImportResolver(tool_dir)

        # NOTE: The @tool_plugin decorator is REQUIRED by older servers (< 0.1.85) for remote execution.
        # Newer servers (0.1.85+) make the decorator optional.
        # See bundle() method for detailed explanation.
        if add_tool_plugin_decorator:
            cls._add_tool_plugin_decorator(tree)

        # Find tool name and description from class definitions
        tool_name, tool_description = cls._extract_tool_metadata(tree, file_path.stem)

        # Categorize imports
        local_imports, external_imports = import_resolver.categorize_imports(tree)

        # Extract main code nodes
        main_code_nodes = []
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                continue
            main_code_nodes.append(ast.unparse(node))

        # Inline local imports
        inlined_code, inlined_external_imports = import_resolver.inline_local_imports(local_imports)

        # Build bundled code
        all_external_imports = external_imports + inlined_external_imports

        # NOTE: The gllm_plugin.tools import is REQUIRED when decorator is added.
        # See bundle() method for detailed explanation.
        # TESTED: Commenting out this import causes NameError when server tries to use the decorator.
        if add_tool_plugin_decorator:
            cls._ensure_tool_plugin_import(all_external_imports)

        bundled_code = ["# Bundled tool with inlined local imports\n"]
        bundled_code.extend(import_resolver.format_external_imports(all_external_imports))

        # Add main tool code
        bundled_code.append("# Main tool code\n")
        for node_code in main_code_nodes:
            bundled_code.append(node_code + "\n")
        bundled_code.append("\n")

        # Then add inlined dependencies
        bundled_code.extend(inlined_code)

        bundled_source = "".join(bundled_code)

        return tool_name, tool_description, bundled_source

    @staticmethod
    def _extract_tool_metadata(tree: ast.AST, fallback_name: str) -> tuple[str, str]:
        """Extract tool name and description from AST.

        Args:
            tree: AST tree of the source file.
            fallback_name: Name to use if not found in source.

        Returns:
            Tuple of (tool_name, tool_description).
        """
        tool_name, tool_description = ToolBundler._find_class_attributes(tree)

        if not tool_name:
            # Convert class name to snake_case as fallback
            tool_name = "".join(["_" + c.lower() if c.isupper() else c for c in fallback_name]).lstrip("_")

        if not tool_description:
            tool_description = f"Tool: {fallback_name}"

        return tool_name, tool_description

    @staticmethod
    def _find_class_attributes(tree: ast.AST) -> tuple[str | None, str | None]:
        """Find name and description attributes in class definitions.

        Args:
            tree: AST tree to search.

        Returns:
            Tuple of (name, description) if found.
        """
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            name, description = ToolBundler._extract_class_name_description(node)
            if name or description:
                return name, description
        return None, None

    @staticmethod
    def _extract_class_name_description(
        class_node: ast.ClassDef,
    ) -> tuple[str | None, str | None]:
        """Extract name and description from a single class definition.

        Args:
            class_node: AST ClassDef node.

        Returns:
            Tuple of (name, description) if found.
        """
        name = None
        description = None

        for item in class_node.body:
            if not isinstance(item, ast.AnnAssign):
                continue
            if not isinstance(item.target, ast.Name):
                continue
            if not isinstance(item.value, ast.Constant):
                continue

            if item.target.id == "name":
                name = item.value.value
            elif item.target.id == "description":
                description = item.value.value

        return name, description
