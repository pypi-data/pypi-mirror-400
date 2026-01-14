"""Documentation coverage tests.

Ensures all public API exports are documented.
"""

import ast
import pathlib


def get_all_exports() -> set[str]:
    """Parse __init__.py to get all public exports."""
    init_path = pathlib.Path(__file__).parent.parent / "src" / "slimschema" / "__init__.py"
    tree = ast.parse(init_path.read_text(encoding="utf-8"))

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if getattr(target, "id", None) == "__all__":
                    if isinstance(node.value, ast.List):
                        return {elt.value for elt in node.value.elts if isinstance(elt, ast.Constant)}
    return set()


def get_docs_content() -> str:
    """Read all documentation content."""
    docs_path = pathlib.Path(__file__).parent.parent / "docs"
    readme_path = pathlib.Path(__file__).parent.parent / "README.md"

    content = ""
    for md in docs_path.glob("**/*.md"):
        content += md.read_text(encoding="utf-8")

    if readme_path.exists():
        content += readme_path.read_text(encoding="utf-8")

    return content


def test_all_exports_documented():
    """Every __all__ export should appear in documentation."""
    exports = get_all_exports()
    docs_content = get_docs_content()

    missing = []
    for export in sorted(exports):
        # Check if the export name appears in docs
        # Allow for various formats: `export`, export, "export"
        if export not in docs_content:
            missing.append(export)

    assert not missing, f"Undocumented exports: {missing}"


def test_core_api_has_examples():
    """Core API functions should have runnable examples."""
    docs_path = pathlib.Path(__file__).parent.parent / "docs" / "python"

    # Core APIs that must have examples
    core_apis = {
        "spec": "spec.md",
        "Schema": "schema.md",
        "ValidationError": "errors.md",
        "Len": "constraints.md",
        "Range": "constraints.md",
    }

    for api, expected_file in core_apis.items():
        file_path = docs_path / expected_file
        assert file_path.exists(), f"Missing doc file for {api}: {expected_file}"

        content = file_path.read_text(encoding="utf-8")
        assert api in content, f"{api} not mentioned in {expected_file}"
        assert "```python" in content, f"No Python examples in {expected_file}"
        assert "assert" in content, f"No assertions in {expected_file} examples"


def test_schema_class_fully_documented():
    """Schema class methods should all be documented."""
    schema_doc = pathlib.Path(__file__).parent.parent / "docs" / "python" / "schema.md"
    content = schema_doc.read_text(encoding="utf-8")

    # Key Schema class methods
    methods = [
        "from_yaml",
        "from_yaml_safe",
        "from_json_schema",
        "to_json_schema",
        "validate",
        "validate_json",
        "validate_or_raise",
    ]

    missing = [m for m in methods if m not in content]
    assert not missing, f"Schema methods not documented: {missing}"


def test_no_dead_links_in_python_docs():
    """Internal doc references should point to existing files."""
    docs_path = pathlib.Path(__file__).parent.parent / "docs" / "python"

    for md_file in docs_path.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")

        # Find references like `docs/python/foo.md`
        import re

        refs = re.findall(r"docs/python/(\w+\.md)", content)
        for ref in refs:
            ref_path = docs_path / ref
            assert ref_path.exists(), f"Dead link in {md_file.name}: docs/python/{ref}"
