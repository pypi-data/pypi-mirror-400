"""Documentation tests using mktestdocs."""
import pathlib

import pytest
from mktestdocs import check_md_file

DOCS_PATH = pathlib.Path(__file__).parent.parent / "docs"
README_PATH = pathlib.Path(__file__).parent.parent / "README.md"

ALL_DOCS = sorted(DOCS_PATH.glob("**/*.md"))


@pytest.mark.parametrize("fpath", ALL_DOCS, ids=lambda p: str(p.relative_to(DOCS_PATH)))
def test_python_examples(fpath):
    """Test Python code blocks in documentation."""
    check_md_file(fpath=fpath, lang="python", memory=True)


def test_readme_python():
    """Test Python examples in README."""
    check_md_file(fpath=README_PATH, lang="python", memory=True)


# No CLI tests - SlimSchema is Python SDK only
