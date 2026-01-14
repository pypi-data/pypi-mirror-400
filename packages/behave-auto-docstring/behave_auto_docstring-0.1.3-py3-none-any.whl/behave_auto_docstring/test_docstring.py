from .docstring import add_to_docstring


def test_add_to_docstring_empty():
    result = add_to_docstring(None, "When Something")

    assert (
        result
        == """Usage:

```gherkin
When Something
```
"""
    )


def test_add_to_docstring_some_text():
    result = add_to_docstring("Some text", "When Something")

    assert (
        result
        == """Some text

Usage:

```gherkin
When Something
```
"""
    )


def test_add_to_docstring_add_to_gherkin_block():
    base = """wooo

```gherkin
Given Other
```
"""

    result = add_to_docstring(base, "When Something")

    assert (
        result
        == """wooo

```gherkin
Given Other
When Something
```
"""
    )
