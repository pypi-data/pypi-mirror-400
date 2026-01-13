"""
Test README.md code examples.

This module extracts Python code blocks from README.md that have
<!-- name: test_name --> comments and runs them as tests.
"""
import re
from pathlib import Path

import pytest


README_PATH = Path(__file__).parent.parent / "README.md"

# Pattern to match <!-- name: test_name --> followed by ```python code block
EXAMPLE_PATTERN = re.compile(
    r"<!--\s*name:\s*(\w+)\s*-->\s*\n```python\n(.*?)```",
    re.DOTALL
)


def extract_examples() -> list[tuple[str, str]]:
    """Extract named code examples from README.md."""
    content = README_PATH.read_text()
    return EXAMPLE_PATTERN.findall(content)


# Generate test IDs and code pairs
EXAMPLES = extract_examples()


@pytest.mark.parametrize("name,code", EXAMPLES, ids=[e[0] for e in EXAMPLES])
def test_readme_example(name: str, code: str) -> None:
    """Run a code example from README.md."""
    # Create a namespace for exec
    namespace = {"__name__": "__main__"}

    # Execute the code
    exec(compile(code, f"<README.md:{name}>", "exec"), namespace)
