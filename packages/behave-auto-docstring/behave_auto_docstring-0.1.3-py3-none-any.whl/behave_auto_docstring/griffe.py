import inspect
import logging

from griffe import (
    Docstring,
    Function,
    GriffeLoader,
    Extension,
    dynamic_import,
)

logger = logging.getLogger(__name__)


class DynamicDocstrings(Extension):
    def on_function(self, *, func: Function, loader: GriffeLoader, **kwargs) -> None:
        try:
            runtime_obj = dynamic_import(func.path)
        except ImportError:
            logger.debug(f"Could not get dynamic docstring for {func.path}")
            return
        try:
            docstring = runtime_obj.__doc__
        except AttributeError:
            logger.debug(f"Object {func.path} does not have a __doc__ attribute")
            return

        if docstring is None:
            return
        docstring = inspect.cleandoc(docstring)
        if func.docstring:
            func.docstring.value = docstring
        else:
            func.docstring = Docstring(docstring, parent=func)


Extension = DynamicDocstrings
