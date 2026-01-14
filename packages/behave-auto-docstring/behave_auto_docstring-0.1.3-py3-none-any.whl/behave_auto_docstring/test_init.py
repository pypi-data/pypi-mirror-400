from . import when, then, given


def test_when():
    @when("A function is declared")
    def function(context): ...

    assert (
        function.__doc__
        == """Usage:

```gherkin
When A function is declared
```
"""
    )


def test_when_skip_true():
    @when("Another function is declared", skip=True)
    def function(context):
        """Some docstring"""

    assert function.__doc__ == """Some docstring"""


def test_all():
    @given("A new function is declared")
    @when("A new function is declared")
    @then("A new function is declared")
    def function(context): ...

    assert (
        function.__doc__
        == """Usage:

```gherkin
Then A new function is declared
When A new function is declared
Given A new function is declared
```
"""
    )
