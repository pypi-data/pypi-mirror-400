from behave import when as behave_when, then as behave_then, given as behave_given

from .docstring import add_to_docstring


def when(step_name: str, skip: bool = False):
    def my_when(func):
        if not skip:
            func.__doc__ = add_to_docstring(func.__doc__, f"When {step_name}")

        return behave_when(step_name)(func)  # type: ignore

    return my_when


def then(step_name: str, skip: bool = False):
    def my_then(func):
        if not skip:
            func.__doc__ = add_to_docstring(func.__doc__, f"Then {step_name}")

        return behave_then(step_name)(func)  # type: ignore

    return my_then


def given(step_name: str, skip: bool = False):
    def my_given(func):
        if not skip:
            func.__doc__ = add_to_docstring(func.__doc__, f"Given {step_name}")

        return behave_given(step_name)(func)  # type: ignore

    return my_given
