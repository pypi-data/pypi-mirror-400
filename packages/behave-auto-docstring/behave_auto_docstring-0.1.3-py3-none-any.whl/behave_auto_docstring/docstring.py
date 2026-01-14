import re


def usage_info(line):
    return f"""Usage:

```gherkin
{line}
```
"""


def add_to_docstring(current: str | None, line: str) -> str:
    if current is None:
        return usage_info(line)

    match = re.match("(.*)```gherkin(.*?)```(.*)", current, re.DOTALL)
    if match:
        before = match.group(1)
        inside = match.group(2)
        after = match.group(3)

        return f"{before}```gherkin{inside}{line}\n```{after}"

    return current + "\n\n" + usage_info(line)
