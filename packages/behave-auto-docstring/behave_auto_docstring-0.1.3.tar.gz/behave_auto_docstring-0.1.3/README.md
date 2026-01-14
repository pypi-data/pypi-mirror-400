# behave_auto_docstring

Adds a simple docstring to behave step, e.g.

```python
from behave_auto_docstring import when

@when("A function is declared")
def function(context): ...
```

is equivalent to

```python
from behave import when

@when("A function is declared")
def function(context):
    """
    Usage:

    ```gherkin
    When A function is declared
    ```
    """"
```

## Usage with mkdocs

For mkdocstrings to parse the resulting docs, you need to add

```yaml
plugins:
  - mkdocstrings:
      handlers:
        python:
          options:
            extensions:
              - behave_auto_docstring.griffe
```

to your `mkdocs.yml` file.